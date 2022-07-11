from asyncio import exceptions
from distutils.log import error
import time
import serial
import requests
import time

#
# CHANGE ACCESS_TOKEN TO YOUR OWN
#
ACCESS_TOKEN = '[YOUR ACCESS TOKEN]'

# The serial port used to communicate with the LCD
s = serial.Serial()

# Used to open the serial port and set the port and buadrate
def OpenSerialPort(port, baud):
    try :
        s.port = port
        s.baudrate = baud
        s.open()
        return True
    except exceptions.SerialException:
        print("Error: Serial Port Not Connected")
        return False

# Checks to see if the serial port is connected
# Useful to tell if the device was unplugged, so we know to kill the deamon
def SerialPortConnected():
    return s.is_open

# check if the time has changed
last_time = "None"
def TimeDifference(current_time):
    global last_time

    if current_time != last_time:
        last_time = current_time
        return True
    else:
        return False

# Should spotify recheck if the song is changed?
last_spotify_time = time.time()
program_start_time = time.time()
time_interval = 20
def ShouldSpotifySendRequest(token):
    global last_spotify_time
    global time_interval
    global program_start_time

    if token == "None":
        return False # No token, no request

    if time.time() - last_spotify_time > time_interval or time.time() - program_start_time < time_interval / 2:
        last_spotify_time = time.time()
        return True
    else:
        return False

# Add to the time interval
def AddMoreTimeBetweenRequests(amount):
    global time_interval
    time_interval += amount

# Get the current time in a nice little string
def GetCurrentTime():
    now = time.localtime()
    return time.strftime("%I:%M:%S %p", now)

# Get the track info from spotify
def GetCurrentSpotifyInfo(access_token):
    SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'

    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if response.status_code != 200:
        current_track_info = {
            "id": "None",
            "track_name": "None",
            "artists": "None",
            "link": "None",
            "error": response.status_code
        }

        return current_track_info

    json_resp = response.json()

    track_id = json_resp['item']['id']
    track_name = json_resp['item']['name']
    artists = [artist for artist in json_resp['item']['artists']]

    link = json_resp['item']['external_urls']['spotify']

    artist_names = ', '.join([artist['name'] for artist in artists])

    current_track_info = {
        "id": track_id,
        "track_name": track_name,
        "artists": artist_names,
        "link": link,
        "error": 0
    }
    
    return current_track_info

# Get the currently playing track
def GetCurrentTrack(access_token):
    spotify_info = GetCurrentSpotifyInfo(access_token)
    error_code = spotify_info["error"]
    current_track = ""

    if error_code == 0:
        current_track = spotify_info["track_name"]
    else:
        current_track = "$error:" + str(error_code)

    return current_track

# Clears the screen of the lcd
def ClearLCD():
    # '~' is the clear command for the LCD
    s.write(b"~")

# Write output to the first line on the lcd
def WriteFirstLine(output):
    s.write(b"<") # Start the first line
    s.write(output.encode('ascii', 'ignore'))

# Write output to the second line on the lcd
def WriteSecondLine(output):
    s.write(b">") # Start the second line
    s.write(output.encode('ascii', 'ignore'))

# Clears the text on the first line
def ClearFirstLine():
    WriteFirstLine("                ")
    WriteFirstLine("")
    
# Clears the second line
def ClearSecondLine():
    WriteSecondLine("                ")
    WriteSecondLine("")

# Init the lcd, and make sure its ready
def InitLCD():
    current_time_seconds = time.time()

    while SerialPortConnected() and time.time() - current_time_seconds < 5:
        time.sleep(1)

        ClearLCD()
        s.write(b"DeskLCD`v0.1!       ")

        # Show a little status bar to let the user know the lcd is respoinding to the deamon
        # it also gives a indication of how long the init process is taking
        for i in range(0, int(time.time() - current_time_seconds)):
            s.write(b"#")

# Does spotify have an error?
def IsSongValid(song):
    return not "$error" in song

# Has Song changed?
last_song = "None"
def SongChanged(song):
    global last_song

    if song != last_song:
        last_song = song
        return True
    else:
        return False

# Main function
def main():
    # Get the token
    global ACCESS_TOKEN

    # Open the serial port
    if OpenSerialPort("/dev/ttyUSB0", 9600):
        print("[INFO]: Connected to LCD")
    else:
        print("[ERROR]: Could not connect to LCD")
        return

    # Init
    InitLCD()
    ClearLCD()

    song = "None"

    # Main Loop of the deamon
    while SerialPortConnected():
        current_time = GetCurrentTime()

        # Check if the time has changed (a second has passed)
        if TimeDifference(current_time):
            
            # Check if we should send a request to spotify
            # This has two jobs:
            #   1. Check if the token is valid
            #   2. Check if the time has changed a significant amount to not spam the spotify api
            if ShouldSpotifySendRequest(ACCESS_TOKEN):
                song = GetCurrentTrack(ACCESS_TOKEN)

                if not IsSongValid(song):
                    error_code = song.split(":")[1]

                    if error_code == "401": # Token expired
                        print("[ERROR]: Invalid Access Token")
                        ACCESS_TOKEN = "None"

                    elif error_code == "204": # No song playing
                        print("[ERROR]: No Song Currently Playing")
                        song = "None"

                    elif error_code == "500" or error_code == "503": # Internal Server Error
                        print("[ERROR]: Spotify Server Error")
                        song = "None"

                    elif error_code == "429": # Too Many Requests
                        print("[ERROR]: Too Many Requests to the Spotify API")
                        song = "None"

                        # If the spotify API is having issues, or network is down
                        # we should add more time between requests
                        AddMoreTimeBetweenRequests(10)

                    else:
                        print("[ERROR]: Unknown Error \"{}\"!".format(error_code))
                        song = "None"

                else:
                    # Finally we have a valid song, but did it change?
                    if SongChanged(song):
                        # Send the song to the lcd
                        ClearFirstLine()
                        WriteFirstLine(song)

            # Check if the song is 'None'
            if song == "None":
                # If the song is 'None', just tell the time
                WriteFirstLine("Current Time:   ")

            # Finally output the time
            WriteSecondLine(current_time)
                        

# Makes the python script runnable
if __name__ == "__main__":
    try:
        main()
    
    except KeyboardInterrupt:
        print("[INFO]: Stopping...")
        ClearLCD()
        WriteFirstLine("Goodbye!")
        time.sleep(1)
        ClearLCD()
        print("[INFO]: Closing Serial Port...")
        s.close()
        print("[INFO]: Goodbye!")
        exit()
    except Exception as e:
        print("[ERROR]: Unexpected {}".format(e))
        ClearLCD()
        WriteFirstLine("Error!")
        WriteSecondLine("Closed Deamon...")
        print("[INFO]: Closing Serial Port...")
        s.close()
        print("[INFO]: Goodbye!")
        exit()
