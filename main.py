import TouchPortalAPI
from TouchPortalAPI import TYPES
from TPPEntry import TP_PLUGIN_ACTIONS, TP_PLUGIN_STATES, TP_PLUGIN_EVENTS, PLUGIN_ID
from sound_recorder import AudioRecorderApp, DeviceAlreadyRecordingError, DeviceNotFoundError, ChannelLimitExceededError
from sys import exit


## make a custom soundboard page that will check if we have 'record new sound' set for 'Button 1' for example.. 
## if we have "Record Enabled" then button 1 press will set the 'Value' for the button to be recorded next as 'Button1.wav
## so when the user hits "save audio" it will save automatically to button1.wav and then disable the button selection..

## So 10 buttons on a page.. each button places button1.wav, button2.wav etc.. 
## BUT if the user wants to re-record this sound, they will click a button that says "Record New Sound" and then click the button they want to re-record..
## this eanbled the 'save button' to be enabled and then they can save the new sound to the button..



## things need changed so we have 3 states.. and then go back to how we checked for channel 0, 1, 2 when using tkiner originally.



## the sound_recorder.py is lokoing for the 'channel'.. IE channel 1, 2 or 3 as shown in tkinter gui.. it needs to reference the name instead

class ClientInterface(TouchPortalAPI.Client):
    def __init__(self):
        super().__init__(self)
        
        self.pluginId = PLUGIN_ID
        # TP connection settings
        self.TPHOST = "127.0.0.1"
        self.TPPORT = 12136
        self.RCV_BUFFER_SZ = 4096 
        self.SND_BUFFER_SZ = 1048576

        # Log settings
        self.logLevel = "INFO"
        self.setLogFile("Sound_Recorder")

        # Register events
        self.add_listener(TYPES.onConnect, self.onConnect)
        self.add_listener(TYPES.onAction, self.onAction)
        self.add_listener(TYPES.onShutdown, self.onShutdown)
        self.add_listener(TYPES.onSettingUpdate, self.onSettings)

    def settingsToDict(self, settings):
        """ 
        Convert a list of settings to a dictionary
        """
        return { list(settings[i])[0] : list(settings[i].values())[0] for i in range(len(settings)) }

    def onSettings(self, data):
        self.log.debug(f"Connection: {data}")
        self.plugin_settings = self.settingsToDict(data['values'])

        self.activateSettings()


    def activateSettings(self):
        """
         Doing things with the settings
        """
        soundRecorder.MAX_PRE_RECORD_SECONDS = int(self.plugin_settings.get('Max Pre-Record Time (seconds)', 30))
        soundRecorder.RATE = int(self.plugin_settings.get('Audio Sample Rate', 44100))
        self.log.info(f"Settings: Max Pre-Record Time changed to: {soundRecorder.MAX_PRE_RECORD_SECONDS}")

        if self.plugin_settings.get('Debug Mode').lower() == "on":
            self.setLogLevel("DEBUG")
            self.log.debug("Settings: Debug mode enabled")
        else:
            self.setLogLevel("INFO")
            self.log.info("Settings: Debug mode disabled")


    def onConnect(self, data):
        self.log.info("Connected to Touch Portal")
        self.plugin_settings = self.settingsToDict(data['settings'])
        self.activateSettings()
        
        ## set all recording states to false
        for i in range(1, 4):
            plugin.stateUpdate(f"{PLUGIN_ID}.recording_state.Channel_{i}", "False")

    
        plugin.stateUpdate(f"{PLUGIN_ID}.state.active_recording_devices", "0")
        plugin.choiceUpdate(f"{PLUGIN_ID}.act.start_recording.device", list(soundRecorder.device_name_to_index_and_rate.keys()))
        plugin.choiceUpdate(f"{PLUGIN_ID}.act.save_audio.channel", ["1", "2", "3"])


    def onAction(self, data):
        action_id = data.get('actionId')
        action_data = data.get('data', [])

        if action_id == f"{PLUGIN_ID}.act.start_recording":
            deviceName = action_data[1]['value']
            chanNum = action_data[0]['value']
            channels = action_data[2]['value']
            if channels == "mono":
                channels = 1
            elif channels == "stereo":
                channels = 2

            try:
                response = soundRecorder.start_recording(int(chanNum), deviceName, channels)
                if response is not None:
                    if deviceName in response:
                        device_channel = response[deviceName]
                        plugin.stateUpdate(f"{PLUGIN_ID}.recording_state.Channel_{chanNum}",
                                            "True")

                        self.log.info(f"Recording State for {deviceName} {soundRecorder.recording_states[device_channel]}")

                    ## update total recording devices
                    plugin.stateUpdate(f"{PLUGIN_ID}.state.active_recording_devices", str(len(response.keys() if response is not None else "0")))

                    self.log.info(f"Started recording for {deviceName} on Channel {chanNum} ")
            except DeviceNotFoundError as e:
                self.log.error(f"Not Found: {e}")
            except DeviceAlreadyRecordingError as e:
                self.log.error(f"Already Recording: {e}")
            except ChannelLimitExceededError as e:
                self.log.error(f"Channel limit exceeded: {e}")


        elif action_id == f"{PLUGIN_ID}.act.stop_recording":
            chanNum = action_data[0]['value']
            response = None
            try:
                response = soundRecorder.stop_recording(chanNum)
            except DeviceNotFoundError as e:
                self.log.error(f"Not Found: {e}")

            print("This is response to stop recording: ", response)
            try:
                active_recording_devices = str(len(response.keys()))
            except:
                active_recording_devices = "0"

            if response and response is not None:
                self.log.info(f"Stopped recording for {chanNum}")

            plugin.stateUpdate(f"{PLUGIN_ID}.recording_state.Channel_{chanNum}", "False")
            ## update total recording devices 
            plugin.stateUpdate(f"{PLUGIN_ID}.state.active_recording_devices", active_recording_devices)

        


        elif action_id == f"{PLUGIN_ID}.act.save_audio":
            chanNum = action_data[0]['value']
            duration = int(action_data[1]['value'])  # Duration in seconds
            filename = action_data[2]['value']

            # Save recording logic for the device name and duration
            try:
                soundRecorder.save_recorded_audio(chanNum, duration, filename)
                self.log.info(f"Saved audio for {chanNum} for {duration} seconds to {filename}")
            except DeviceNotFoundError as e:
                self.log.error(f"Already Recording: {e}")


    def onShutdown(self, data):
        pass



soundRecorder = AudioRecorderApp()
plugin = ClientInterface()
ret = 0
try:
    plugin.connect()
except KeyboardInterrupt:
    plugin.log.warning("Caught keyboard interrupt, exiting.")
except Exception:
    from traceback import format_exc
    plugin.log.error(f"Exception in TP Client:\n{format_exc()}")
    ret = -1
finally:
    plugin.disconnect()
    del plugin
    exit(ret)


