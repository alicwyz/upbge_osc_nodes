# OSC Nodes for UPBGE Logic Nodes

## 1. Introduction

This is a modified version of UPBGE that enhances the **Logic Nodes** addon by adding **Open Sound Control (OSC) nodes**. These nodes allow UPBGE to send, receive, and process OSC messages, making it easier to integrate with external applications such as **PureData, Max/MSP, TouchDesigner, and DAWs**.

These nodes enable real-time communication between UPBGE and external software, allowing for interactive music systems, live performances, and procedural animations controlled via OSC.

## 2. Installation

To install the OSC Nodes:

1. Download this repository.
2. Locate the folder **`/3.6`** inside this repository.
3. Copy and paste the **`/3.6`** folder into your **UPBGE main directory**, overwriting any existing files.

After installation, restart UPBGE and you should see the new OSC nodes available in the **Logic Nodes** editor.

## 3. Documentation

### **Added Nodes and Their Functionality**

#### 🔹 **OSC Server Node** (`Setup OSC Server`)

- Starts an OSC server to receive messages from external applications.
- Outputs a dictionary of received OSC messages.
- Can enable a debug mode to print received messages.
- **Inputs:**
  - `Start` (Condition) → Starts the server.
  - `Stop` (Condition) → Stops the server.
  - `IP` (String) → IP address to listen on.
  - `Port` (Integer) → Port to listen on.
  - `Default Address` (String) → Filters messages starting with this address.
  - `Debug` (Condition) → Prints received messages to the console.
- **Outputs:**
  - `Messages` (Parameter) → Dictionary containing received OSC messages.

#### 🔹 **OSC Receive Node** (`Receive OSC Message`)

- Extracts a specific OSC message from the server’s dictionary.
- Can ignore repeated values to optimize performance.
- **Inputs:**
  - `Messages` (Parameter) → Dictionary from `Setup OSC Server`.
  - `OSC Address` (String) → The address to filter.
  - `Ignore Repeats` (Condition) → If enabled, ignores repeated values.
- **Outputs:**
  - `Received` (Condition) → Triggers when a new message is received.
  - `Value` (Parameter) → The value of the received OSC message.

#### 🔹 **OSC Send Node** (`Send OSC Message`)

- Sends an OSC message to an external application.
- **Inputs:**
  - `Condition` (Condition) → Triggers the message.
  - `IP` (String) → Target IP address.
  - `Port` (Integer) → Target port.
  - `OSC Address` (String) → The OSC address to send the message to.
  - `Data` (Parameter) → The value to send.
- **Outputs:**
  - `Done` (Condition) → Activates when the message is sent.

#### 🔹 **OSC Sequencer Node** (`OSC Sequencer`)

- Records and replays OSC messages over time.
- Useful for live performances and procedural animations.
- **Inputs:**
  - `Start Recording` (Condition) → Starts recording messages.
  - `Stop Recording` (Condition) → Stops recording.
  - `Play` (Condition) → Plays the recorded sequence.
  - `Speed` (Float) → Controls playback speed (default = 1.0).
  - `Max Duration` (Float) → Limits the recording length (default = 5s).
  - `Messages` (Parameter) → Dictionary of received OSC messages.
- **Outputs:**
  - `Recording` (Condition) → True while recording.
  - `Playing` (Condition) → True while playing back.
  - `Finished Playing` (Condition) → Triggers when playback ends.
  - `Message` (Parameter) → Outputs the replayed OSC message.

---

These new OSC nodes make UPBGE a **powerful tool for interactive media, live performances, and game development**. **Enjoy real-time OSC communication in UPBGE!** 🚀
