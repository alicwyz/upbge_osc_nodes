from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting, not_met
import time

# OSC Sequencer Node: Records and replays OSC messages
class ULOSCSequencer(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        
        # Inputs
        self.start_recording = None
        self.stop_recording = None
        self.play = None
        self.speed = None
        self.max_duration = None
        self.messages = None
        self.debug = None
        
        # Outputs
        self.RECORDING = ULOutSocket(self, self.get_recording)
        self.PLAYING = ULOutSocket(self, self.get_playing)
        self.FINISHED = ULOutSocket(self, self.get_finished)
        self.MESSAGE = ULOutSocket(self, self.get_message)
        
        # Internal state
        self._recording = False
        self._playing = False
        self._finished = False
        self._message = None
        
        self._recorded_data = []  # Stores (timestamp, address, value)
        self._start_time = None
        self._playback_index = 0
        self._playback_start = None
    
    def get_recording(self):
        return self._recording
    
    def get_playing(self):
        return self._playing
    
    def get_finished(self):
        return self._finished
    
    def get_message(self):
        return self._message
    
    def evaluate(self):
        _start_recording = self.get_input(self.start_recording)
        _stop_recording = self.get_input(self.stop_recording)
        _play = self.get_input(self.play)
        _speed = self.get_input(self.speed) or 1.0
        _max_duration = self.get_input(self.max_duration) or 5.0
        _messages = self.get_input(self.messages)
        _debug = self.get_input(self.debug)

        self._set_ready()
        
        current_time = time.time()

        # Start recording
        if _start_recording and not self._recording:
            self._recording = True
            self._recorded_data = []
            self._start_time = current_time
            self._finished = False
            if _debug: 
                print("OSC Sequencer: Recording started")
        
        # Stop recording
        if _stop_recording and self._recording:
            self._recording = False
            if _debug:
                print(f"OSC Sequencer: Recording stopped. {len(self._recorded_data)} messages recorded.")
        
        # Record incoming messages
        if self._recording and _messages:
            for address, value in _messages.items():
                timestamp = current_time - self._start_time
                if timestamp <= _max_duration:
                    self._recorded_data.append((timestamp, address, value))
                else:
                    self._recording = False  # Auto stop if duration exceeded
                    if _debug:
                        print("OSC Sequencer: Max recording duration reached.")
        
        # Start playback
        if _play and not self._playing and self._recorded_data:
            self._playing = True
            self._playback_index = 0
            self._playback_start = current_time
            self._finished = False
            if _debug:
                print("OSC Sequencer: Playback started")
        
        # Playback logic
        if self._playing:
            if self._playback_index < len(self._recorded_data):
                elapsed = (current_time - self._playback_start) * _speed
                next_timestamp, next_address, next_value = self._recorded_data[self._playback_index]
                
                if elapsed >= next_timestamp:
                    self._message = {next_address: next_value}
                    self._playback_index += 1
            else:
                self._playing = False
                self._finished = True
                if _debug:
                    print("OSC Sequencer: Playback finished")