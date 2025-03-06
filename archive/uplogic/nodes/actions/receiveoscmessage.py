from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting, not_met
from pythonosc import dispatcher, osc_server


# Receive OSC Message Node
class ULReceiveOSCMessage(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        
        self.messages = None
        self.osc_address = None
        self.ignore_repeats = None  # Toggle for ignoring repeated values
        
        self.RECEIVED = ULOutSocket(self, self.get_received)
        self.VALUE = ULOutSocket(self, self.get_value)
        
        self._received = False
        self._value = None
        self._last_value = None  # Store last received value for filtering
    
    def get_received(self):
        return self._received
    
    def get_value(self):
        return self._value
    
    def evaluate(self):
        _messages = self.get_input(self.messages)
        _address = self.get_input(self.osc_address)
        _ignore_repeats = self.get_input(self.ignore_repeats)
        
        self._set_ready()
        
        if _messages and _address in _messages:
            new_value = _messages.pop(_address)
            if _ignore_repeats and new_value == self._last_value:
                self._received = False
            else:
                self._value = new_value
                self._last_value = new_value
                self._received = True
        else:
            self._received = False
