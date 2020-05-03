"""helper functions for Microsoft Graph"""
# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license.
# See LICENSE in the project root for license information.
import base64
import mimetypes
import os
import urllib
import webbrowser
import logging
import sys
import json

import msal
import atexit

import pyperclip
import requests

import config

import RPi.GPIO as GPIO
import time

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "RefreshToken.txt"
RefreshTokenFile = os.path.join(script_dir, rel_path)

def get_access_token(client_id):
    cache = msal.SerializableTokenCache()
    if os.path.exists(RefreshTokenFile):
        cache.deserialize(open(RefreshTokenFile, "r").read())
    atexit.register(lambda:
        open(RefreshTokenFile, "w").write(cache.serialize())
        # Hint: The following optional line persists only when state changed
        if cache.has_state_changed else None
    )

    app = msal.PublicClientApplication(
        client_id,
        authority=config.AUTHORITY_URL,
        token_cache = cache
        )

    # The pattern to acquire a token looks like this.
    result = None

    # Note: If your device-flow app does not have any interactive ability, you can
    #   completely skip the following cache part. But here we demonstrate it anyway.
    # We now check the cache to see if we have some end users signed in before.
    accounts = app.get_accounts()
    
    if accounts:
        logging.info("Account(s) exists in cache, probably with token too. Let's try.")
        print("Pick the account you want to use to proceed:")
        for a in accounts:
            print(a["username"])
        # Assuming the end user chose this one
        chosen = accounts[0]
        # Now let's try to find a token in cache for this account
        result = app.acquire_token_silent(config.SCOPES, account=chosen)

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")

        flow = app.initiate_device_flow(scopes=config.SCOPES)
        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

        print(flow["message"])
        sys.stdout.flush()  # Some terminal needs this to ensure the message is shown

        # Ideally you should wait here, in order to save some unnecessary polling
        input("Press Enter after signing in from another device to proceed, CTRL+C to abort.")
        result = app.acquire_token_by_device_flow(flow)


    if "access_token" in result:
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {result["access_token"]}',
                            'SdkVersion': 'sample-python-msal',
                            'x-client-SKU': 'sample-python-msal'})
        return session
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug

def api_endpoint(url):
    """Convert a relative path such as /me/photo/$value to a full URI based
    on the current RESOURCE and API_VERSION settings in config.py.
    """
    if urllib.parse.urlparse(url).scheme in ['http', 'https']:
        return url # url is already complete
    return urllib.parse.urljoin(f'{config.RESOURCE}/{config.API_VERSION}/',
                                url.lstrip('/'))

def led_status(color,status):
    GPIO.output(config.LED[color]["GPIO"], status)

def led_all_off(off):
    led_status("green",False)
    led_status("yellow",False)
    led_status("red",False)

#In case it's the first time you are using your GPIO to contorl led, we need this.
def initiate_led(Start):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) 
    GPIO.setup(config.LED["green"]["GPIO"], GPIO.OUT)
    GPIO.setup(config.LED["yellow"]["GPIO"], GPIO.OUT)
    GPIO.setup(config.LED["red"]["GPIO"], GPIO.OUT)