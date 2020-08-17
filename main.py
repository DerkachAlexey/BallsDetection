import cv2 as cv

from detect_ball import DetectBall
from config import Config
from draw import Draw
from preprocess import simplest_cb
from db_master import DbMaster
from enum import Enum
import imutils

class VideoType(Enum):
    FILE = 0 #read video from file
    RTSP = 1 #read video from rtsp link

config = Config()
videoType = VideoType(config.get('video_type'))

cap = cv.VideoCapture()
if videoType == VideoType.FILE:
    cap = cv.VideoCapture('./data/'+config.get('video_name'))
elif videoType == VideoType.RTSP:
    cap = cv.VideoCapture(config.get('rtsp_stream'))


if __name__ == '__main__':

    master_db = DbMaster(config.get('db_name'))

    if not master_db.table_exists(config.get('table_name')):
        master_db.create_table(config.get('table_name'), {'player_number' : 'INTEGER', 'red_balls' : 'INTEGER', 'white_balls' : 'INTEGER'})
        master_db.insert_values(config.get('table_name'), [1, 0, 0])
        master_db.insert_values(config.get('table_name'), [2, 0, 0])

    detectBall = DetectBall(config)

    frame_number = 0

    players_count = {'players1':{'red':0, 'white':0}, 'players2':{'red':0, 'white':0}}


    while(cap.isOpened()):

        ret, frame = cap.read()

        frame_number += 1

        if (frame_number % 20) != 0:
            continue


        if len(frame) == 0:
            break

        frame = simplest_cb(frame, 10)

        rect_for_first_players = config.get('players1').get('rectangle')
        rect_for_second_players = config.get('players2').get('rectangle')

        frame_first_players = frame[rect_for_first_players[1]: rect_for_first_players[3],
                              rect_for_first_players[0]: rect_for_first_players[2]]
        frame_second_players = frame[rect_for_second_players[1]: rect_for_second_players[3],
                               rect_for_second_players[0]: rect_for_second_players[2]]

        first_player_balls = detectBall.find_balls(frame_first_players, True)
        second_players_balls = detectBall.find_balls(frame_second_players, True)

        player_1 = detectBall.separate_players(first_player_balls, 1)
        player_2 = detectBall.separate_players(second_players_balls, 2)

        rectangles_first = detectBall.find_rectangles(player_1).get('players1')
        rectangles_second = detectBall.find_rectangles(player_2).get('players2')

        if rectangles_first['red'] :
            players_count['players1']['red'] = detectBall.calculate_sets(player_1, rectangles_first)

        if rectangles_first['white']:
            players_count['players1']['white'] = detectBall.calculate_games(player_1, rectangles_first)

        if rectangles_second['red'] :
            players_count['players2']['red'] = detectBall.calculate_sets(player_2, rectangles_second)

        if rectangles_second['white']:
            players_count['players2']['white'] = detectBall.calculate_games(player_2, rectangles_second)


        master_db.update(config.get('table_name'), 1, ['red_balls', 'white_balls'], [players_count['players1']['red'], players_count['players1']['white']])
        master_db.update(config.get('table_name'), 2, ['red_balls', 'white_balls'], [players_count['players2']['red'], players_count['players2']['white']])

        cv.imshow('players_1', Draw.draw_rectangles(frame_first_players, player_1))
        cv.imshow('players_2', Draw.draw_rectangles(frame_second_players, player_2))

        print(players_count)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()