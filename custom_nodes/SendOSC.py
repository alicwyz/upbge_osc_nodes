from bge_netlogic import custom_node
from bge_netlogic.editor.nodes.node import LogicNodeCustomType
from bge_netlogic.editor.sockets import *

@custom_node
class LogicNodeSendOSC(LogicNodeCustomType):
    bl_idname = "LogicNodeSendOSC"
    bl_label = "Send OSC Message"
    #bl_icon = 'OUTLINER_DATA_GP_LAYER'
    #nl_category = "Network"
    #nl_module = 'actions'
    nl_module = ".SendOSCLogic"
    nl_class = "LogicSendOSC"

    def init(self, context):
        #NLActionNode.init(self, context)
        
        self.add_input(NodeSocketLogicCondition, "Condition", "condition")
        
        self.add_input(NodeSocketLogicString, "IP", "ip")
        #self.inputs[-1].value = socket.gethostbyname(socket.gethostname())
        
        self.add_input(NodeSocketLogicIntegerPositive, "Port", "port")
        #self.inputs[-1].value = 5005
        
        self.add_input(NodeSocketLogicString, "OSC Address", "osc")
        #self.inputs[-1].value = "/osc"
        
        self.add_input(NodeSocketLogicParameter, "Data", "data")
        
        self.add_output(NodeSocketLogicCondition, "Done", "DONE")


