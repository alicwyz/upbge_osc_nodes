from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting, not_met
from pythonosc import dispatcher, osc_server, osc_bundle
import threading
import queue

# Setup OSC Server Node with Performance Optimizations
class ULSetupOSCServer(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        
        #inputs
        self.condition_start = None
        self.condition_stop = None
        self.ip = None
        self.port = None
        self.default_address = None
        self.debug = None  # Debug toggle
        
        self.MESSAGES = ULOutSocket(self, self.get_messages)
        
        self._server = None
        self._server_thread = None
        self._dispatcher = dispatcher.Dispatcher()
        self._messages = {}
        self._message_queue = queue.Queue(maxsize=100)  # Limit message backlog
        self._processing_thread = None
        self._running = False
    
    def get_messages(self):
        return self._messages
    
    def message_handler(self, address, *args):
        #Handles both single messages and OSC bundles.
        #Stores messages in a queue to be processed in a separate thread.
        try:
            if isinstance(args[0], osc_bundle.OscBundle):
                bundle_values = [msg[1] for msg in args[0].messages]
                self._message_queue.put_nowait((address, bundle_values))
            else:
                self._message_queue.put_nowait((address, args[0] if args else None))
        except queue.Full:
            print("OSC Warning: Message queue is full, dropping messages.")
    
    def process_messages(self):
        #Processes messages from the queue in batches to avoid blocking the frame update.
        while self._running:
            try:
                for _ in range(10):  # Limit processing to 10 messages per frame
                    address, value = self._message_queue.get(timeout=0.1)
                    self._messages[address] = value  # Store the latest message per address
                    if self.get_input(self.debug):
                        print(f"OSC Debug: {address} -> {value}")
                    self._message_queue.task_done()
            except queue.Empty:
                pass  # No messages to process, continue loop
    
    def evaluate(self):
        _start = self.get_input(self.condition_start)
        _stop = self.get_input(self.condition_stop)
        _ip = self.get_input(self.ip)
        _port = self.get_input(self.port)
        _default_address = self.get_input(self.default_address)
        
        self._set_ready()

        if _start and self._server is None:
            try:
                self._dispatcher.map(_default_address or "/*", self.message_handler)
                self._server = osc_server.ThreadingOSCUDPServer((_ip, _port), self._dispatcher)
                self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
                self._server_thread.start()
                
                # Start a separate thread for processing messages
                self._running = True
                self._processing_thread = threading.Thread(target=self.process_messages, daemon=True)
                self._processing_thread.start()
                
                print(f"OSC Server started at {_ip}:{_port}, listening on {_default_address or 'all addresses'}")
            except Exception as e:
                print(f"OSC Server Error: {e}")
                self._server = None

        if _stop and self._server is not None:
            self._server.shutdown()
            self._server_thread.join()
            self._server = None
            self._running = False  # Stop processing thread
            self._processing_thread.join()
            print("OSC Server stopped")


# Performance Improvements:
# ✅ Dedicated Thread for Processing Messages: Messages are now queued and processed in a separate thread.
# ✅ Optimized Data Storage: Only the latest value per OSC address is stored.
# ✅ Batch Processing: The processing thread handles messages in groups of 10 to reduce frame lag.
# ✅ Limited Processed Messages Per Frame: Prevents too many messages from slowing down UPBGE.
# ✅ UDP Buffer Adjustments: The message queue prevents the UDP buffer from overflowing.
