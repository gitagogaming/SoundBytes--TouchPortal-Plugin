#!/usr/bin/env python3

PLUGIN_ID = "gitago.soundrecorder"
PLUGIN_NAME = "SoundBytes"
PLUGIN_FOLDER = "SoundBytes"
PLUGIN_ICON = ""

TP_PLUGIN_INFO = {
    "sdk": 6,
    "version": 101,
    "name": PLUGIN_NAME,
    "id": PLUGIN_ID,
    "configuration": {
        "colorDark": "#222423",
        "colorLight": "#1D9BF0",
        "parentCategory": "audio"
    },
    "plugin_start_cmd_windows": f"%TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}\\{PLUGIN_NAME}.exe",
    "plugin_start_cmd_linux": f"sh %TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}//start.sh {PLUGIN_NAME}",
    "plugin_start_cmd_mac": f"sh %TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}//start.sh {PLUGIN_NAME}",
}

TP_PLUGIN_SETTINGS = {   
    
    "1": {
      "name": "Max Pre-Record Time (seconds)",
      "type": "text",
      "default": "30",
      "readOnly": False
    },
    "2": {
      "name": "Debug Mode",
      "type": "text",
      "default": "off",
      "readOnly": False
    },
    "3": {
      "name": "Audio Sample Rate",
      "type": "text",
      "default": "44100",
      "readOnly": False
    }
    
}

TP_PLUGIN_CATEGORIES = {
    "main": {
        "id": PLUGIN_ID + ".main",
        "name": "Sound Recorder",
        "imagepath": "%TP_PLUGIN_FOLDER%Sound_Recorder\\Sound_Icon_26px.png"
    }
}

TP_PLUGIN_CONNECTORS = {}

TP_PLUGIN_ACTIONS = {
    "1": {
        "id": PLUGIN_ID + ".act.start_recording",
        "name": "Start Recording",
        "prefix": "Prefix",
        "type": "communicate",
        "description": "Start recording audio",
        "format": "Start recording audio on Channel $[1] from Device: $[2]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.start_recording.channel",
                "type": "choice",
                "label": "Channel",
                "default": "1",
                "valueChoices": ["1", "2", "3"]
            },
            "1": {
                "id": PLUGIN_ID + ".act.start_recording.device",
                "type": "choice",
                "label": "Select Input Device",
                "default": "",
                "valueChoices": []
            }, 
            "2": {
                "id": PLUGIN_ID + ".act.start_recording.stereo",
                "type": "choice",
                "label": "Mono or Stereo",
                "default": "mono",
                "valueChoices": ["mono", "stereo"]
            }
        },
        "category": "main"
    },
    "2": {
        "id": PLUGIN_ID + ".act.stop_recording",
        "name": "Stop Recording",
        "prefix": "Prefix",
        "type": "communicate",
        "description": "Stop recording audio",
        "format": "Stop recording audio on Channel: $[1]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.stop_recording.channel",
                "type": "choice",
                "label": "Select Input Device",
                "default": "",
                "valueChoices": ["1", "2", "3"]
            }
        },
        "category": "main"
    },
    "3": {
        "id": PLUGIN_ID + ".act.save_audio",
        "name": "Save Audio",
        "prefix": "Prefix",
        "type": "communicate",
        "description": "Save recorded audio",
        "format": "Save recorded audio on Channel: $[1] for Duration: $[2] seconds with Filename: $[3]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.save_audio.channel",
                "type": "choice",
                "label": "Select Input Device",
                "default": "",
                "valueChoices": []
            },
            "1": {
                "id": PLUGIN_ID + ".act.save_audio.duration",
                "type": "text",
                "label": "Recording Duration (seconds)",
                "default": "10"
            },
            "2": {
                "id": PLUGIN_ID + ".act.save_audio.filename",
                "type": "text",
                "label": "Filename",
                "default": "filename.wav"
            }
        },
        "category": "main"
    }
}

TP_PLUGIN_STATES = {
    "0": {
        "id": PLUGIN_ID + ".state.active_recording_devices",
        "type": "text",
        "desc": "Active Recording Devices",
        "default": "0",
        "category": "main"
    }
}

## make a loop of 3 to add recording status for 3 different channels
for i in range(1, 4):
    TP_PLUGIN_STATES[str(i)] = {
        "id": PLUGIN_ID + f".recording_state.Channel_{i}",
        "type": "text",
        "desc": f"Recording State - Channel:{i}",
        "default": "False",
        "category": "main"
    }

TP_PLUGIN_EVENTS = {}

