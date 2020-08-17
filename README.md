# BallsDetection

### Application for counting players' scores during the tennis play game.
### To use this app, please, put the camera opposite the judge chair, set up the config file (description below) and run the app (main.py).

## General settings:

- video file should be in a data folder
- config.json should be in a data folder
- database file should be in a root folder and have .db extension

### Config file settings:

1. Name of the config file is config.json. This file should be in a data folder
2. Video type: 0 - read from source file (in this case user must provide "video_name"), 1 - rtsp/rtp/http stream (in this case user must provide "rtsp_stream")
3. Rtsp stream: link to rtsp stream
4. Balls detection regions for first and second teams. These regions must containt both rows, where white and red balls are placed: 
"players1": 
   {
      "rectangle": [x1, y1, x2, y2]
   },
   "players2":
   {
      "rectangle": [x1, y1, x2, y2]
   }
5. Information about videofile name: "video_name" : "example.mp4". Video should be in a data folder
6. DataBase name: a data base is used for storing information about players' scores.
7. Table name: the name of the table in the database