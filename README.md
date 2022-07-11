# DeskLCD
A Little project to show the current song and time on a 16x2 LCD
![IMG_20220711_000321(1)](https://user-images.githubusercontent.com/33582457/178192994-35237df1-2a9b-4348-94ae-889b4354c27d.jpg)

# Software
Currently the python script is designed to run on linux. It uses `/dev/ttyUSB0`, but can be changed inside the script. Make sure you have your spotify token for reading currently playing song (link can be found [here](https://developer.spotify.com/console/get-users-currently-playing-track/?market=&additional_types=))

### Uploading Code to Arduino
The arduino code is stored inside the DeskLCD.ino file and needs to be uploaded before you run the python script. 

### Running Python
Make sure your spotify token and serial port is configured, then start up the script. The lcd should change to `DeskLCD` to init the lcd and make sure the serial port is open. After 4 seconds, the lcd should change to showing either the song that is playing or the current time. All errors should be caught and debug info sent to terminal. 

### Using Spotify API
Once the script starts, it sends API requests about every second to spotify. This is to make sure the API is working and to get any song the user started to play when starting the script. After about 5 seconds, the script will begin to wait 20 seconds in-between requests. If the API returns that we are requesting too much, then we add 10 seconds to our wait request time. This is to keep your token from getting shut down and becoming inactive.

# Hardware
Highlevel Project Overview Diagram![image](https://user-images.githubusercontent.com/33582457/178192131-b896e729-a777-4b82-81e1-90d2ced28166.png)
Wiring Diagram![Wiring](https://user-images.githubusercontent.com/33582457/178193056-b0b894bd-90e1-4daa-903d-bc29a4eeee31.png)

