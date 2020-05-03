"""Configuration settings for PiBusyLight app using device flow authentication
"""

CLIENT_ID = '6a02705e-5df7-4850-a867-75b6d6804792'

AUTHORITY_URL = 'https://login.microsoftonline.com/common'
SCOPES = ['Presence.Read']
RESOURCE = 'https://graph.microsoft.com'
API_VERSION = 'beta'
#If you didn't used the same GPIO than on https://www.instructables.com/id/Controlling-Multiple-LEDs-With-Python-and-Your-Ras/
#Please change the GPIO accordingly
LED = {
    "green" : {
        "GPIO": 22
    },
    "yellow" : {
        "GPIO": 18
    },
    "red" : {
        "GPIO": 17
    }
}

#Current Teams Status, you can change the color if you want to match other LED Color
STATUS = {
    "Available" : "green", 
    "AvailableIdle" : "yellow", 
    "Away" : "yellow", 
    "BeRightBack" : "yellow", 
    "Busy" : "red", 
    "BusyIdle" : "red", 
    "DoNotDisturb" : "red", 
    "Offline" : "off", 
    "PresenceUnknown" : "off"
}

# This code can be removed after configuring CLIENT_ID and CLIENT_SECRET above.
if 'ENTER_YOUR' in CLIENT_ID:
    print('ERROR: config.py does not contain valid CLIENT_ID.')
    import sys
    sys.exit(1)
