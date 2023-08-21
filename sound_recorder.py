import pyaudio
import numpy as np
from collections import deque
from scipy.io import wavfile
import tkinter as tk
from tkinter import ttk


class DeviceNotFoundError(Exception):
    pass

class ChannelLimitExceededError(Exception):
    pass

class DeviceAlreadyRecordingError(Exception):
    pass

class AudioRecorderApp:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.RATE = 44100
        self.RECORD_SECONDS = 10
        self.MAX_PRE_RECORD_SECONDS = 30
        self.MAX_CHANNELS = 4
        self.audio_recorded_flags = [False] * self.MAX_CHANNELS  # Flags to indicate audio recorded

        self.p = pyaudio.PyAudio()
        self.num_input_devices = self.p.get_device_count()

        self.audio_buffers = [deque(maxlen=int(self.RATE * self.RECORD_SECONDS)) for _ in range(self.MAX_CHANNELS)]
        self.recording_states = [False] * self.MAX_CHANNELS
        self.selected_device_indices = [None] * self.MAX_CHANNELS

        #self.device_vars = [i for i in range(1, self.MAX_CHANNELS+1)]
        self.device_vars = [i for i in range(self.MAX_CHANNELS)]
        self.active_recordings = {}  # Dictionary to track active recordings by device name
        self.device_name_to_index = {}
        self.index_to_device_name = {}
        self.active_streams = {}  # Dictionary to track active streams by device name

        for i in range(self.num_input_devices):
            device_info = self.p.get_device_info_by_index(i)
            device_name = device_info['name']
            self.device_name_to_index[device_name] = i
            self.index_to_device_name[i] = device_name

        self.tkinter = False

    def start_recording(self, channel, device_name, channels):
        if device_name not in self.device_name_to_index:
            raise DeviceNotFoundError(f"Device '{device_name}' not found in available devices.")

        if len(self.active_recordings) >= self.MAX_CHANNELS:
            raise ChannelLimitExceededError("All channels are already in use.")

        if device_name in self.active_recordings:
            raise DeviceAlreadyRecordingError(f"Device '{device_name}' on channel {channel} is already being recorded.")
        


       #for i in range(self.num_input_devices):
       #    device_info = self.p.get_device_info_by_index(i)
       #    if device_info['name'] == device_name:
       #        self.selected_device_indices[channel] = i
       #        break
       
        ## Setting the Device Names Index
        self.selected_device_indices[channel] = self.device_name_to_index[device_name]
        
        self.recording_states[channel] = True
        self.audio_buffers[channel].clear()
        stream = self.p.open(format=self.FORMAT,
                             channels=channels,
                             rate=self.RATE,
                             input=True,
                             input_device_index=self.selected_device_indices[channel],
                             frames_per_buffer=self.CHUNK,
                             stream_callback=lambda in_data, frame_count, time_info, status: self.audio_callback(in_data, frame_count, time_info, status, channel))

        self.active_streams[device_name] = stream
        self.active_recordings[device_name] = channel
    #    self.update_button_states()
        return self.active_recordings
        

    def stop_recording(self, chanNum):
        device_name = ""
        if self.tkinter:
            device_name = self.device_vars[device_name].get()

        ## find device name for channel number
        device_name = self.index_to_device_name.get(self.selected_device_indices[int(chanNum)], None)
        if device_name is None or device_name == "None":
            raise DeviceNotFoundError(f"Device '{device_name}' not found in available devices.")
        
        if device_name not in self.device_name_to_index:
            raise DeviceNotFoundError(f"Device '{device_name}' not found in available devices.")

        if device_name in self.active_recordings:
            try:
                channel = self.active_recordings[device_name]
                self.recording_states[channel] = False
                stream = self.active_streams.pop(device_name, None)
                if stream:
                    stream.stop_stream()
                    stream.close()
                del self.active_recordings[device_name]
            except:
                raise DeviceNotFoundError(f"Device '{device_name}' not found in available devices.")
        
        return self.active_recordings

    def save_recorded_audio(self, chanNum, duration=10, filename = "recorded_audio"):
        if self.tkinter:
            device_name = self.device_vars[device_name].get()

        device_name = self.index_to_device_name[self.selected_device_indices[int(chanNum)]]

        if filename == "recorded_audio":
            filename = f"recorded_{device_name}_{duration}seconds"

        if device_name not in self.active_recordings:
            print(f"Device '{device_name}' is not being recorded.")
            return

        channel = self.active_recordings[device_name]
        if self.audio_buffers[channel]:
            audio_data = np.array(list(self.audio_buffers[channel]))[-int(self.RATE * duration):]
            wavfile.write(filename +".wav", self.RATE, audio_data)
        else:
            print(f"No recorded audio for Device '{device_name}' on Channel {channel} to save.")



    def audio_callback(self, in_data, frame_count, time_info, status, channel):
        if self.recording_states[channel]:
            data_array = np.frombuffer(in_data, dtype=np.int16)
            self.audio_buffers[channel].extend(data_array)
        return in_data, pyaudio.paContinue
    

    def update_button_states(self):
        # Update button states based on recording_states and recorded audio
        for i, (recording_state, audio_recorded) in enumerate(zip(self.recording_states, self.audio_recorded_flags)):
            if recording_state:
                self.recording_buttons[i].config(state="disabled")
                self.stop_buttons[i].config(state="normal")
                self.save_buttons[i].config(state="disabled"  if audio_recorded else "enabled")
            else:
                self.recording_buttons[i].config(state="normal")
                self.stop_buttons[i].config(state="disabled")
                self.save_buttons[i].config(state="normal" if audio_recorded else "disabled")
        self.root.after(500, self.update_button_states)  # Schedule the function to run again after 500 milliseconds
#

    def run(self):
        self.tkinter = True

        self.root = tk.Tk()
        self.root.title("Multi-Channel Audio Recorder")  

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))    

        for i in range(self.num_input_devices):
            device_info = self.p.get_device_info_by_index(i)
            device_name = device_info['name']
            self.device_name_to_index[device_name] = i   
        self.device_labels = [ttk.Label(self.frame, text=f"Select Input Device for Channel {i + 1}:") for i in range(self.MAX_CHANNELS)]
        self.device_vars = [tk.StringVar() for _ in range(self.MAX_CHANNELS)]
        self.device_dropdowns = [ttk.Combobox(self.frame, textvariable=var, state="readonly") for var in self.device_vars]   
        for i in range(self.MAX_CHANNELS):
            self.device_labels[i].grid(row=2 * i, column=0, padx=10, pady=5, sticky=tk.W)
            self.device_dropdowns[i]["values"] = list(self.device_name_to_index.keys())
            self.device_dropdowns[i].grid(row=2 * i, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)   
        self.duration_labels = [ttk.Label(self.frame, text=f"Recording seconds:") for i in range(self.MAX_CHANNELS)]
        self.duration_vars = [tk.StringVar(value=str(self.RECORD_SECONDS)) for _ in range(self.MAX_CHANNELS)]
        self.duration_entries = [ttk.Entry(self.frame, textvariable=var) for var in self.duration_vars]  
        for i in range(self.MAX_CHANNELS):
         #   self.device_dropdowns[i].grid(row=2 * i, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)  # Place the dropdowns in column 1
            self.duration_labels[i].grid(row=2 * i, column=2, padx=10, pady=5, sticky=tk.W)  # Place the duration labels in column 3
            self.duration_entries[i].grid(row=2 * i, column=3, padx=10, pady=5, sticky=tk.W)  # Place the duration entries in column 4   

        self.recording_buttons = [ttk.Button(self.frame, text=f"Start Recording Channel {i + 1}", command=lambda i=i: self.start_recording(i)) for i in range(self.MAX_CHANNELS)]
        self.stop_buttons = [ttk.Button(self.frame, text=f"Stop Recording Channel {i + 1}", command=lambda i=i: self.stop_recording(i), state="disabled") for i in range(self.MAX_CHANNELS)]
        self.save_buttons = [ttk.Button(self.frame, text=f"Save Audio Channel {i + 1}", command=lambda i=i: self.save_recorded_audio(i), state="disabled") for i in range(self.MAX_CHANNELS)]    
        for i in range(self.MAX_CHANNELS):
            self.recording_buttons[i].grid(row=2 * i + 1, column=0, padx=10, pady=5)
            self.stop_buttons[i].grid(row=2 * i + 1, column=1, padx=10, pady=5)
            self.save_buttons[i].grid(row=2 * i + 1, column=2, padx=10, pady=5)  
        self.status_label = ttk.Label(self.frame, text="Ready")
        self.status_label.grid(row=2 * self.MAX_CHANNELS + 1, columnspan=3)  
        self.root.mainloop()

if __name__ == "__main__":
    recorder = AudioRecorderApp()
    recorder.run()


## signle working minus recording seconds max   import pyaudio
## signle working minus recording seconds max   import numpy as np
## signle working minus recording seconds max   from collections import deque
## signle working minus recording seconds max   from scipy.io import wavfile
## signle working minus recording seconds max   import tkinter as tk
## signle working minus recording seconds max   from tkinter import ttk
## signle working minus recording seconds max   
## signle working minus recording seconds max   CHUNK = 1024  # Number of frames per buffer
## signle working minus recording seconds max   FORMAT = pyaudio.paInt16  # Audio format (16-bit integer)
## signle working minus recording seconds max   RATE = 44100  # Sampling rate (samples per second)
## signle working minus recording seconds max   RECORD_SECONDS = 10  # Default number of seconds to record
## signle working minus recording seconds max   MAX_PRE_RECORD_SECONDS = 30  # Maximum number of seconds to record back
## signle working minus recording seconds max   
## signle working minus recording seconds max   # Initialize audio stream
## signle working minus recording seconds max   p = pyaudio.PyAudio()
## signle working minus recording seconds max   num_input_devices = p.get_device_count()
## signle working minus recording seconds max   
## signle working minus recording seconds max   # Create a buffer to store the recorded audio
## signle working minus recording seconds max   audio_buffer = deque(maxlen=int(RATE * RECORD_SECONDS))
## signle working minus recording seconds max   recording = False  # Flag to indicate recording state
## signle working minus recording seconds max   
## signle working minus recording seconds max   def start_recording():
## signle working minus recording seconds max       global recording
## signle working minus recording seconds max       recording = True
## signle working minus recording seconds max       record_button.config(state="disabled")
## signle working minus recording seconds max       stop_button.config(state="normal")
## signle working minus recording seconds max       status_label.config(text="Recording...")
## signle working minus recording seconds max       audio_buffer.clear()  # Clear the buffer when starting a new recording
## signle working minus recording seconds max       selected_device_name = device_var.get()
## signle working minus recording seconds max       selected_device_index = device_name_to_index[selected_device_name]
## signle working minus recording seconds max       stream = p.open(format=FORMAT,
## signle working minus recording seconds max                       channels=1,  # Always record in mono for simplicity
## signle working minus recording seconds max                       rate=RATE,
## signle working minus recording seconds max                       input=True,
## signle working minus recording seconds max                       input_device_index=selected_device_index,
## signle working minus recording seconds max                       frames_per_buffer=CHUNK,
## signle working minus recording seconds max                       stream_callback=audio_callback)
## signle working minus recording seconds max       print("Recording started.")
## signle working minus recording seconds max   
## signle working minus recording seconds max   def stop_recording():
## signle working minus recording seconds max       global recording
## signle working minus recording seconds max       recording = False
## signle working minus recording seconds max       record_button.config(state="normal")
## signle working minus recording seconds max       stop_button.config(state="disabled")
## signle working minus recording seconds max       status_label.config(text="Recording stopped.")
## signle working minus recording seconds max       print("Recording stopped.")
## signle working minus recording seconds max   
## signle working minus recording seconds max   def save_recorded_audio():
## signle working minus recording seconds max       global audio_buffer
## signle working minus recording seconds max       filename = "recorded_audio.wav"
## signle working minus recording seconds max       
## signle working minus recording seconds max       if not audio_buffer:
## signle working minus recording seconds max           print("No recorded audio to save.")
## signle working minus recording seconds max           return
## signle working minus recording seconds max       
## signle working minus recording seconds max       # Convert audio buffer to a NumPy array
## signle working minus recording seconds max       audio_data = np.array(audio_buffer)
## signle working minus recording seconds max       
## signle working minus recording seconds max       # Save audio data to a WAV file
## signle working minus recording seconds max       wavfile.write(filename, RATE, audio_data)
## signle working minus recording seconds max       print(f"Recorded audio saved as '{filename}'.")
## signle working minus recording seconds max       status_label.config(text="Audio saved.")
## signle working minus recording seconds max   
## signle working minus recording seconds max   def audio_callback(in_data, frame_count, time_info, status):
## signle working minus recording seconds max       global audio_buffer
## signle working minus recording seconds max       data_array = np.frombuffer(in_data, dtype=np.int16)
## signle working minus recording seconds max       audio_buffer.extend(data_array)
## signle working minus recording seconds max       return in_data, pyaudio.paContinue
## signle working minus recording seconds max   
## signle working minus recording seconds max   def update_pre_record_seconds(value):
## signle working minus recording seconds max       global RECORD_SECONDS
## signle working minus recording seconds max       new_value = int(value)
## signle working minus recording seconds max       if new_value > MAX_PRE_RECORD_SECONDS:
## signle working minus recording seconds max           new_value = MAX_PRE_RECORD_SECONDS
## signle working minus recording seconds max       RECORD_SECONDS = new_value
## signle working minus recording seconds max   
## signle working minus recording seconds max   # Get device names and indexes
## signle working minus recording seconds max   device_name_to_index = {}
## signle working minus recording seconds max   for i in range(num_input_devices):
## signle working minus recording seconds max       device_info = p.get_device_info_by_index(i)
## signle working minus recording seconds max       device_name = device_info['name']
## signle working minus recording seconds max       device_name_to_index[device_name] = i
## signle working minus recording seconds max   
## signle working minus recording seconds max   # GUI setup
## signle working minus recording seconds max   root = tk.Tk()
## signle working minus recording seconds max   root.title("Audio Recorder")
## signle working minus recording seconds max   
## signle working minus recording seconds max   frame = ttk.Frame(root, padding=10)
## signle working minus recording seconds max   frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
## signle working minus recording seconds max   
## signle working minus recording seconds max   record_button = ttk.Button(frame, text="Start Recording", command=start_recording)
## signle working minus recording seconds max   record_button.grid(row=0, column=0, padx=10, pady=5)
## signle working minus recording seconds max   
## signle working minus recording seconds max   stop_button = ttk.Button(frame, text="Stop Recording", command=stop_recording, state="disabled")
## signle working minus recording seconds max   stop_button.grid(row=0, column=1, padx=10, pady=5)
## signle working minus recording seconds max   
## signle working minus recording seconds max   save_button = ttk.Button(frame, text="Save Audio", command=save_recorded_audio)
## signle working minus recording seconds max   save_button.grid(row=0, column=2, padx=10, pady=5)
## signle working minus recording seconds max   
## signle working minus recording seconds max   status_label = ttk.Label(frame, text="Ready")
## signle working minus recording seconds max   status_label.grid(row=1, columnspan=3)
## signle working minus recording seconds max   
## signle working minus recording seconds max   device_label = ttk.Label(frame, text="Select Input Device:")
## signle working minus recording seconds max   device_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
## signle working minus recording seconds max   
## signle working minus recording seconds max   # Dropdown menu to select audio input device
## signle working minus recording seconds max   device_var = tk.StringVar()
## signle working minus recording seconds max   device_dropdown = ttk.Combobox(frame, textvariable=device_var, state="readonly")
## signle working minus recording seconds max   device_dropdown["values"] = list(device_name_to_index.keys())
## signle working minus recording seconds max   device_dropdown.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
## signle working minus recording seconds max   
## signle working minus recording seconds max   pre_record_label = ttk.Label(frame, text="Seconds to Record Back:")
## signle working minus recording seconds max   pre_record_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
## signle working minus recording seconds max   
## signle working minus recording seconds max   pre_record_var = tk.StringVar(value=str(RECORD_SECONDS))
## signle working minus recording seconds max   pre_record_entry = ttk.Entry(frame, textvariable=pre_record_var)
## signle working minus recording seconds max   pre_record_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
## signle working minus recording seconds max   
## signle working minus recording seconds max   update_button = ttk.Button(frame, text="Update", command=lambda: update_pre_record_seconds(pre_record_var.get()))
## signle working minus recording seconds max   update_button.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
## signle working minus recording seconds max   
## signle working minus recording seconds max   root.mainloop()




