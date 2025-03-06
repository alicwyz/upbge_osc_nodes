import socket
from bge_netlogic.basicnodes import NLActionNode, NLConditionSocket, NLParameterSocket, NLPositiveIntegerFieldSocket, NLQuotedStringFieldSocket


class LogicNodeSendOSC(NLActionNode):
    bl_idname = "LogicNodeSendOSC"
    bl_label = "Send OSC Message"
    bl_icon = 'OUTLINER_DATA_GP_LAYER'
    nl_category = "Network"
    nl_module = 'actions'

    def init(self, context):
        NLActionNode.init(self, context)
        
        self.inputs.new(NLConditionSocket.bl_idname, "Condition")
        
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "IP")
        self.inputs[-1].value = socket.gethostbyname(socket.gethostname())
        
        self.inputs.new(NLPositiveIntegerFieldSocket.bl_idname, "Port")
        self.inputs[-1].value = 5005
        
        self.inputs.new(NLQuotedStringFieldSocket.bl_idname, "OSC Address")
        self.inputs[-1].value = "/osc"
        
        self.inputs.new(NLParameterSocket.bl_idname, "Data")
        
        self.outputs.new(NLConditionSocket.bl_idname, "Done")

    def get_netlogic_class_name(self):
        return "ULSendOSCMessage"

    def get_input_sockets_field_names(self):
        return [
            "condition",
            "ip",
            "port",
            "osc",
            "data"
        ]

    def get_output_socket_varnames(self):
        return ['DONE']

_nodes.append(LogicNodeSendOSC)