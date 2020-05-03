"""PiBusyLight with device flow authentication."""
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import pprint
import time
import config

from helpers import api_endpoint, get_access_token, led_all_off, led_status, initiate_led
laststatus = "Offline"
initiate_led(True)

def getpresence(session):
    """Get Presence from logged in user"""
    user_profile = session.get(api_endpoint('me'))
   
    if not user_profile.ok:
        pprint.pprint(user_profile.json()) # display error
        return
    user_data = user_profile.json()
    
    user_presence = session.get(api_endpoint('me/presence'))
   
    if not user_presence.ok:
        pprint.pprint(user_presence.json()) # display error
        return
    user_data = user_presence.json()
    availability = user_data['availability']
    return availability

while True:
    GRAPH_SESSION = get_access_token(config.CLIENT_ID)
    if GRAPH_SESSION:
        currentstatus = getpresence(GRAPH_SESSION)
        print("Current: "+currentstatus)
        print("Last: "+laststatus)
        print("")
        if not currentstatus == laststatus:
            #I find it easier to just shutdown all led but I know I could I have used the laststatus
            #This way if I miss something I'm sure than only one LED is open at a time.
            led_all_off(True)
            laststatus = currentstatus
            if not config.STATUS[currentstatus] == "off":
                #Send the signal to open the right led based on the current status
                led_status(config.STATUS[currentstatus],True)
    #You can increase the poolling interval, but don't go crazy you will be throttled. 
    time.sleep(30)