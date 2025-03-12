from uplogic.nodes import LogicNodeCustom


class MyCustomNode(LogicNodeCustom):

    def __init__(self):
        # Call superclass (parent class) constructor
        super().__init__()

        # Initialize input socket values
        self.game_object = None

        # Initialize output sockets.
        # 'self.add_output()' needs the getter function which is called
        # when a linked socket requests a value.
        self.NAME = self.add_output(self.get_name)

    def get_name(self):
        # This getter function contains the logic that is executed
        # when the first linked socket requests data. Once calculated,
        # the value is stored to avoid re-calculation if there's more
        # than one linked socket.
        game_object = self.get_input(self.game_object)
        return game_object.name

    def evaluate(self):
        # This function is called every frame, regardless of whether the
        # node is needed or not. Keep this as slim as possible.
        pass

    def reset(self):
        # This is called at the end of each frame. Same as with 'evaluate()',
        # keep code in here to a minimum. At the very least you need to call
        # the superclass function though.
        super().reset()
