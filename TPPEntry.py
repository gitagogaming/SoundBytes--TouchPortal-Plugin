#!/usr/bin/env python3

PLUGIN_ID = "gitago.soundrecorder"
PLUGIN_NAME = "SoundBytes"
PLUGIN_FOLDER = "SoundBytes"
PLUGIN_ICON = ""

TP_PLUGIN_INFO = {
    "sdk": 6,
    "version": 100,
    "name": PLUGIN_NAME,
    "id": PLUGIN_ID,
    "configuration": {
        "colorDark": "#222423",
        "colorLight": "#1D9BF0",
        "parentCategory": "audio"
    },
    "plugin_start_cmd_windows": f"%TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}\\{PLUGIN_NAME}.exe"
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
        "format": "Start recording audio from Device: $[1]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.start_recording.device",
                "type": "choice",
                "label": "Select Input Device",
                "default": "",
                "valueChoices": []
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
        "format": "Stop recording audio from Device: $[1]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.stop_recording.device",
                "type": "choice",
                "label": "Select Input Device",
                "default": "",
                "valueChoices": []
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
        "format": "Save recorded audio from Device: $[1] for Duration: $[2] seconds with Filename: $[3]",
        "tryInline": True,
        "data": {
            "0": {
                "id": PLUGIN_ID + ".act.save_audio.device",
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

TP_PLUGIN_EVENTS = {}

