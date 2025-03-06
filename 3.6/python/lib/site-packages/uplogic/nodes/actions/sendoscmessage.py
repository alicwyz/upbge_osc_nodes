from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils import is_waiting
from uplogic.utils import not_met
import pythonosc.udp_client

class ULSendOSCMessage(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
      
        #Inputs
        self.condition = None
        self.ip = None
        self.port = None
        self.osc = None
        self.data = None
        
        #Outputs
        self.DONE = ULOutSocket(self, self.get_done)
        
        #Internal
        self._done = False
        self._client = None

    def get_done(self):
        return self._done

    def evaluate(self):
        '''
        self._done = False
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_ready()
            return
        entity = self.get_input(self.entity)
        if entity:
            entity.send(self.get_input(self.data), self.get_input(self.subject))
        self._done = True
        '''
        _condition = self.get_input(self.condition)
        if _condition is is_waiting:
            return
        
        _data = self.get_input(self.data)
        if _data is is_waiting:
            return
        
        _ip = self.get_input(self.ip)
        _port = self.get_input(self.port)
        _osc = self.get_input(self.osc)
        
        self._done = False
        
        self._set_ready()
        
        if self.setup_server(_ip, _port):
            self._done = self.send_osc(_osc, _data)

     #Create OSC Server
    def setup_server(self, ip, port):
        if self._client is None:
            try:
                self._client = pythonosc.udp_client.SimpleUDPClient(
                    ip, 
                    port
                )
            except Exception as e:
                print(f"OSC Send Error: Could not create client - {e}")
                return False
        return True
    
    def send_osc(self, osc, data):
        try:
            # Send message with appropriate type handling
            self._client.send_message(osc, [data])
            return True
        except Exception as e:
            print(f"OSC Send Error: {e}")
            return False