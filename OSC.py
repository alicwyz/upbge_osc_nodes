import bge
import bpy
from bge import logic
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading
import time
import queue

class OSCServer:
    def __init__(self, ip="127.0.0.1", port=9001, input_rate_ms=40):
        self.ip = ip  # IP address to listen for OSC messages
        self.port = port  # Port to listen for OSC messages
        self.input_rate_ms = input_rate_ms  # Input rate filter in milliseconds
        
        self.scene = logic.getCurrentScene()  # Get current UPBGE scene
        self.objects = self.scene.objects  # Retrieve objects in the scene
        
        self.should_run = True  # Flag to control server loop
        self.q = queue.Queue()  # Store server instance
        self.server_thread = None  # Thread for running server
        
        self.dispatcher = Dispatcher()  # OSC message dispatcher
        self._setup_dispatcher()

        self.last_processed_time = 0  # Store last processed time for all requests

    def _setup_dispatcher(self):
        # Map OSC addresses to corresponding methods
        self.dispatcher.map("/set", self.set_property)
        self.dispatcher.map("/get", self.get_property)
        self.dispatcher.map("/quit", self.quit)

    def _rate_limit(self):
        if self.input_rate_ms == 0:
            return True
        current_time = int(time.time() * 1000)  # Get current time in milliseconds
        elapsed_time = current_time - self.last_processed_time
        if elapsed_time < self.input_rate_ms:
            return False
        self.last_processed_time = current_time
        return True

    def set_property(self, unused_addr, prop_path, *values):
        if not self._rate_limit():
            return
        #Check if the method calls for bpy or KX
        if prop_path.startswith("bpy"):
            self.set_bpy_property(prop_path, *values)
        else:
            self.set_kx_property(prop_path, *values)

    def get_property(self, unused_addr, prop_path, *args):
        if not self._rate_limit():
            return
        #Check if the method calls for bpy or KX
        if prop_path.startswith("bpy"):
            self.get_bpy_property(prop_path)
        else:
            self.get_kx_property(prop_path, *args)

    def set_kx_property(self, obj_name, prop_path, *values):
        # Retrieve the object from the scene
        obj = self.objects.get(obj_name)
        if not obj:
            print(f"Object '{obj_name}' not found.")
            return
        try:
            # Check if the property is a method and call it with the provided values
            if hasattr(obj, prop_path) and callable(getattr(obj, prop_path)):
                method = getattr(obj, prop_path)
                method(*values)
                print(f"Called method '{prop_path}' of '{obj_name}' with values {values}")
            else:
                # Set the specified property on the KX_GameObject
                full_command = f"obj.{prop_path} = {values[0] if len(values) == 1 else values}"
                exec(full_command)
                print(f"Set '{prop_path}' of '{obj_name}' to {values}")
        except AttributeError as e:
            print(f"Property or method '{prop_path}' not found on '{obj_name}'. Error: {e}")
        except Exception as e:
            print(f"Error setting property or calling method: {e}")

    def get_kx_property(self, obj_name, prop_path, *args):
        # Retrieve the object from the scene
        obj = self.objects.get(obj_name)
        if not obj:
            print(f"Object '{obj_name}' not found.")
            return
        try:
            # Try to get the specified property from the KX_GameObject
            full_command = f"getattr(obj, '{prop_path}')"
            value = eval(full_command)
            print(f"'{prop_path}' of '{obj_name}' is {value}")
            return value
        except AttributeError as e:
            print(f"Property '{prop_path}' not found on '{obj_name}' as KX_GameObject. Error: {e}")
        except Exception as e:
            print(f"Error getting property: {e}")

    def set_bpy_property(self, prop_path, *values):
        try:
            # Set the specified property on the bpy object
            exec(f"{prop_path} = {values[0] if len(values) == 1 else values}")
            print(f"Set '{prop_path}' to {values}")
        except ValueError as e:
            print(f"Error parsing values: {e}")
        except AttributeError as e:
            print(f"Property '{prop_path}' not found. Error: {e}")
        except Exception as e:
            print(f"Error setting property: {e}")

    def get_bpy_property(self, prop_path):
        try:
            # Get the specified property from the bpy object
            value = eval(prop_path)
            print(f"'{prop_path}' is {value}")
            return value
        except AttributeError as e:
            print(f"Property '{prop_path}' not found. Error: {e}")
        except Exception as e:
            print(f"Error getting property: {e}")

    def quit(self, unused_addr, *args):
        # Handle quit command
        print("Received /quit command.")
        self.should_run = False  # Stop server loop
        threading.Thread(target=self.shutdown_server).start()

    def server_thread_func(self):
        # Function to run the OSC server in a thread
        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.dispatcher)
        print(f"OSC Server running on {self.ip}:{self.port}")
        self.q.put(server)  # Put the server reference on the queue
        server.serve_forever()  # Handle incoming OSC requests

    def shutdown_server(self):
        # Function to shut down the OSC server
        server = self.q.get()  # Retrieve the server instance
        print("Shutting down server...")
        server.shutdown()  # Shut down the server
        time.sleep(0.01)
        print('... server shutdown!')
        server.server_close()  # Close the server
        print('... finished server_close!')
        time.sleep(0.01)
        print("Ending game")
        logic.endGame()  # End the Blender Game Engine

    def start(self):
        # Start the OSC server if not already started
        if not bge.logic.globalDict.get("server_started", False):
            print("Starting OSC Server...")
            self.server_thread = threading.Thread(target=self.server_thread_func,  name="OSCserver")
            self.server_thread.start()
            bge.logic.globalDict["server_started"] = True

if __name__ == "__main__":
    server = OSCServer()
    server.start()

# Documentation
# Usage:
# 1. Start the server on port 9000 with a filter rate of 100ms:
#    server = OSCServer(ip="127.0.0.1", port=9000, input_rate_ms=100)
#    server.start()
# 2. Set the X position of a Cube object:
#    /set Cube worldPosition[0] 1.0
# 3. Apply movement to a Cube object:
#    /set Cube applyMovement 1.0 0.0 0.0
# 4. Play an action on a Cube object:
#    /set Cube playAction "Action" 1 50
# 5. Retrieve the current X position of the Cube:
#    /get Cube worldPosition[0]
# 6. Set a bpy property (e.g., shape key value):
#    /set bpy.data.objects["Cube"].data.shape_keys.key_blocks["Key 1"].value 0.5
# 7. Get a bpy property (e.g., material color):
#    /get bpy.data.materials["Material"].node_tree.nodes["Principled BSDF"].inputs[0].default_value
# 8. Quit the server:
#    /quit