# BallsDetection

### Application for counting players' during the tennis play game.
### To use this app, please, put the camera opposite the judge chair, set up the config file (description below) and run the app.

### Config file settings:

1. File config.json contains information about videofile name: "video_name" : ["example.mp4"]. Video should be in a data folder
2. Balls detection regions for first and second teams. These regions must containt both rows, where white and red balls are placed: 
"players1": 
   {
      "rectangle": [x1, y1, x2, y2]
   },
   "players2":
   {
      "rectangle": [x1, y1, x2, y2]
   }
3. DataBase name: a data base is used for storing information about players' scores.