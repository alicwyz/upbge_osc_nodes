from uplogic.nodes import LogicNodeCustom
import pythonosc.udp_client


class LogicSendOSC(LogicNodeCustom):
    def __init__(self):
        #ULActionNode.__init__(self)
        # Call superclass (parent class) constructor
        super().__init__()
      
        #Inputs
        self.condition = None
        self.ip = None
        self.port = None
        self.osc = None
        self.data = None
        
        #Outputs
        self.DONE = self.add_output(self.get_done)
        
        #Internal
        self._done = False
        self._client = None

    def get_done(self):
        return self._done

    def evaluate(self):
        # This function is called every frame, regardless of whether the
        # node is needed or not. Keep this as slim as possible.
        _condition = self.get_input(self.condition)
        _data = self.get_input(self.data)
        
        if not _condition or not _data:
            return
        
        _ip = self.get_input(self.ip)
        _port = self.get_input(self.port)
        _osc = self.get_input(self.osc)
        
        
        #self._set_ready()
        
        if self.setup_server(_ip, _port):
            self._done = self.send_osc(_osc, _data)
        else: self._done = False

    def reset(self):
        # This is called at the end of each frame. Same as with 'evaluate()',
        # keep code in here to a minimum. At the very least you need to call
        # the superclass function though.
        super().reset()
    
    
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