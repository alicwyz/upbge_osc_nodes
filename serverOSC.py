from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting, not_met
from pythonosc import dispatcher, osc_server, osc_bundle
import threading
import collections
import re

# Setup Optimized OSC Server Node
class ULSetupOSCServer(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        
        # Inputs
        self.condition_start = None
        self.condition_stop = None
        self.ip = None
        self.port = None
        self.filters = None  # Filter configuration
        self.debug = None  # Debug toggle
        
        self.MESSAGES = ULOutSocket(self, self.get_messages)
        
        self._server = None
        self._server_thread = None
        self._dispatcher = dispatcher.Dispatcher()
        self._messages = {}
        self._message_queue = collections.deque()  # ✅ Changed queue to deque (faster)
        self._processing_thread = None
        self._running = False
        
        # Default filter configuration
        self._filter_config = {
            "default_address": "",
            "queue_length": 100,
            "messages_per_frame": 10,
            "filter_repeats": False,
            "vector_mode": False,
            "repeat_threshold": 0.001,
            "drop_overflow": True,
            "address_filter": "",
            "last_values": {}
        }
        
        # Compiled regex patterns for address filtering
        self._valid_addresses = set()  # ✅ Avoid redundant regex matching
        self._valid_patterns = []  # ✅ Store regex patterns for wildcard matching
        
        # Separate dictionary for last values to improve performance
        self.last_values = {}  # ✅ Faster lookups, avoids modifying _filter_config frequently
    
    def get_messages(self):
        return self._messages
    
    def _should_process_message(self, address, value):
        """Determine if a message should be processed based on filter settings."""
   
        # ✅ First, check exact matches for speed
        if self._valid_addresses and address in self._valid_addresses:
            pass  # Exact match found
        
        # ✅ Then, check regex wildcard matches
        elif self._valid_patterns:
            if not any(pattern.match(address) for pattern in self._valid_patterns):
                return False  # No match found, skip message
        
        # ✅ Check for repeating messages efficiently
        if self._filter_config["filter_repeats"] and address in self.last_values:
            last_value = self.last_values[address]
            if value == last_value:
                return False
            elif isinstance(value, float) and isinstance(last_value, float):
                if abs(value - last_value) < self._filter_config["repeat_threshold"]:
                    return False
            elif self._filter_config["vector_mode"] and isinstance(value, list) and isinstance(last_value, list):
                if all(abs(v - lv) < self._filter_config["repeat_threshold"] for v, lv in zip(value, last_value)):
                    return False
            self.last_values[address] = value
        
        return True
        
    def message_handler(self, address, *args):
        """Handles OSC messages and applies filtering."""
        try:
            value = args[0] if len(args) == 1 else list(args)
            if self._should_process_message(address, value):
                if len(self._message_queue) < self._filter_config["queue_length"]:
                    self._message_queue.append((address, value))  # ✅ Faster non-blocking enqueue
        except Exception as e:
            if self.get_input(self.debug):
                print(f"OSC Error in message handler: {e}")
    
    def process_messages(self):
        """Process messages from the deque dynamically."""
        while self._running:
            try:
                queue_size = len(self._message_queue)
                msgs_to_process = min(queue_size, self._filter_config["messages_per_frame"] * 2)  # ✅ Dynamic batch size
                
                for _ in range(msgs_to_process):
                    if self._message_queue:
                        address, value = self._message_queue.popleft()  # ✅ Faster deque processing
                        self._messages[address] = value
                        if self.get_input(self.debug):
                            print(f"OSC Debug: {address} -> {value}")
            except Exception as e:
                if self.get_input(self.debug):
                    print(f"OSC Processing Error: {e}")
    
    def evaluate(self):
        """Evaluates conditions and manages OSC server state."""
        _start = self.get_input(self.condition_start)
        _stop = self.get_input(self.condition_stop)
        
        # Get filter configuration if connected
        filter_input = self.get_input(self.filters)
        if filter_input:
            self._filter_config.update(filter_input)
        
        self._set_ready()
        
        # ✅ Prevent redundant server restarts
        if _start and (self._server is None or not self._server_thread.is_alive()):
            threading.Thread(target=self._setup_server, daemon=True).start()  # ✅ Non-blocking evaluate()
        
        if _stop and self._server is not None:
            self._shutdown_server()
    
    def _setup_server(self):
        """Sets up the OSC server and starts message processing."""
        try:
            self._message_queue = collections.deque(maxlen=self._filter_config["queue_length"])
            self._valid_addresses = set()
            self._valid_patterns = []
            
            # ✅ Precompile address filter patterns (handles wildcards like "/osc/*")
            if self._filter_config["address_filter"]:
                addresses = re.split(r'[,;]', self._filter_config["address_filter"])
                for addr in addresses:
                    addr = addr.strip()
                    if '*' in addr:
                        regex_pattern = re.compile(f"^{re.escape(addr).replace('\\*', '.*')}$")
                        self._valid_patterns.append(regex_pattern)
                    else:
                        self._valid_addresses.add(addr)  # Exact match optimization
            self._dispatcher.map(self._filter_config["default_address"] or "/*", self.message_handler)
            
            self._server = osc_server.ThreadingOSCUDPServer((self.get_input(self.ip), self.get_input(self.port)), self._dispatcher)
            self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._server_thread.start()
            
            self._running = True
            self._processing_thread = threading.Thread(target=self.process_messages, daemon=True)
            self._processing_thread.start()
            
            if self.get_input(self.debug):
                print(f"OSC Server started at {self.get_input(self.ip)}:{self.get_input(self.port)}")
                if self.get_input(self.filters):
                    config = self._filter_config
                    debug_config = f"Default address: {config["default_address"]}"
                    debug_config += f", Queue: {config['queue_length']}, Msgs/frame: {config['messages_per_frame']}"
                    
                    if config["filter_repeats"]:
                        debug_config += f", Filtering repeats (threshold: {config['repeat_threshold']}, vector mode: {config["vector_mode"]} )"
                    
                    if config["adress_filter"]:
                        debug_config += f", Advanced filter: {config['address_filter']}"
                        
                    print(debug_config)      
        except Exception as e:
            print(f"OSC Server Error: {e}")
            self._server = None
    
    def _shutdown_server(self):
        """Shuts down the OSC server gracefully."""
        self._server.shutdown()
        self._server_thread.join()
        self._server = None
        self._running = False
        self._processing_thread.join()
        self._message_queue.clear()
        self._filter_config["last_values"] = {}
        if self.get_input(self.debug):
            print("OSC Server stopped")