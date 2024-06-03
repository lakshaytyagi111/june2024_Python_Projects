# This is initial commit more automation will be added soon...

# problem for which i tried to create this project

#i have two devices connected to my laptop, 1 my mobile phone and 2 my bluetooth speaker, 
# i wanted to play songs from mobile and listen to them on my bluetooth speaker.
# speaker doesnot have multiple device connection feature, but i wanted to listen audio both from my laptop to speaker and mobile to speaker.
# so i wrote a python script to proxy the audio data from mobile to speaker via laptop.
# i have mobile and speaker connected to my laptop, so i can read audio data from mobile and write it to speaker.
# i don't use pyaudio, i use subprocess to read audio data from mobile and write it to speaker.

import subprocess
import time
import sys
import shlex

# Bluetooth device addresses of mobile and speaker (physical address)
mobile = "00:00:00:00:00:00"
speaker = "00:00:00:00:00:00"

# Get the Bluetooth device name of mobile and speaker
def get_device_name(device):
    device_name = None
    try:
        output = subprocess.check_output(["bluetoothctl", "info", device]).decode("utf-8")
        for line in output.split("\n"):
            if "Alias" in line:
                device_name = line.split(":")[1].strip()
                break
    except Exception as e:
        print(f"Error getting device name for {device}: {e}")
    return device_name

# Get device names
# This part is hard coded 
# Make sure both mobile and speaker are connected to laptop
# Use this command to get the name of sources (mobile) :
# > pactl list sources | grep Name: 
mobile_name = "bluez_source.E4_EC_E8_D2_3A_4F.a2dp_source"

# Use this command to get the name of sinks(speaker) :
# > pactl list sinks | grep Name:
speaker_name = "bluez_sink.3B_FC_62_6C_FD_E7.a2dp_sink"

print(f"Mobile name: {mobile_name}")
print(f"Speaker name: {speaker_name}")

if not mobile_name or not speaker_name:
    print("Could not find mobile or speaker device names.")
    sys.exit(1)

# Function to run pactl commands as the current user
def run_pactl_command(command):
    try:

        cmd = f"pactl {command}"
        print(f"Running command: {cmd}")
        subprocess.check_call(shlex.split(cmd)) 
    except subprocess.CalledProcessError as e:
        print(f"Error executing pactl command: {e}")
        sys.exit(1)

# Function to proxy the Bluetooth data coming from mobile to speaker
def proxy(mobile_name, speaker_name):
    try:
        # Load the loopback module
        #adjust the latency_msec value to reduce the latency
        latency_msec = 0
        loopback_command = f"load-module module-loopback source={mobile_name} sink={speaker_name} "
        print(f"Loading loopback module with command: pactl {loopback_command}")
        run_pactl_command(loopback_command)
        print("Loopback module loaded.")

        # Get the index of the speaker sink
        sinks_output = subprocess.check_output(["pactl", "list", "short", "sinks"]).decode("utf-8").split("\n")
        sink_index = None
        for line in sinks_output:
            if speaker_name in line:
                sink_index = line.split()[0]
                break

        if sink_index is None:
            print(f"Could not find sink index for {speaker_name}")
            sys.exit(1)

        # Set the default source and sink
        print(f"Setting default source to {mobile_name}")
        run_pactl_command(f"set-default-source {mobile_name}")
        print(f"Setting default sink to index {sink_index}")
        run_pactl_command(f"set-default-sink {sink_index}")

        print(f"Proxying audio from {mobile_name} to {speaker_name}. Press Ctrl+C to stop.")
        
        # Wait for the user to interrupt
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Unload the loopback module when interrupted
        print("Unloading loopback module")
        run_pactl_command("unload-module module-loopback")
        print("Proxy stopped.")

    except subprocess.CalledProcessError as e:
        # Handle errors when executing pactl commands
        print(f"Error executing pactl command: {e}")
        sys.exit(1)

    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected error: {e}")
        sys.exit(1)

# Proxy the Bluetooth data coming from mobile to speaker
proxy(mobile_name, speaker_name)
