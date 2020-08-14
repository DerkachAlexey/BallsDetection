import cv2 as cv

from detect_ball import DetectBall
from config import Config
from draw import Draw
from preprocess import simplest_cb
import imutils

cap = cv.VideoCapture('C:/Users/alexey.derkach/Downloads/detectBall/data/5.mp4')

if __name__ == '__main__':

    config = Config()

    detectBall = DetectBall(config)

    frame_number = 0

    while(cap.isOpened()):

        #frame = cv.imread('data/image.png')
        ret, frame = cap.read()

        frame_number += 1

        if (frame_number % 60) != 0:
            continue

        frame = simplest_cb(frame, 10)

        rect_for_first_players = config.get('players1').get('rectangle')
        rect_for_second_players = config.get('players2').get('rectangle')

        frame_first_players = frame[rect_for_first_players[1]: rect_for_first_players[3],
                              rect_for_first_players[0]: rect_for_first_players[2]]
        frame_second_players = frame[rect_for_second_players[1]: rect_for_second_players[3],
                               rect_for_second_players[0]: rect_for_second_players[2]]



        cv.imshow('first players', frame_first_players)
        cv.imshow('second players', frame_second_players)


        cv.waitKey(1)
        first_player_balls = detectBall.find_balls(frame_first_players, True)
        second_players_ball = detectBall.find_balls(frame_second_players, True)

        separated_players = detectBall.separate_players( first_player_balls)

        rectangles = detectBall.find_rectangles(separated_players)

        print(rectangles)

        print(detectBall.calculate_sets(separated_players, rectangles))
        print(detectBall.calculate_games(separated_players, rectangles))

        cv.imshow('range', Draw.draw_range(frame, [config.get('players1')['rectangle'],
                                                        config.get('players2')['rectangle']]))
        cv.imshow('rectangles', Draw.draw_rectangles(frame, separated_players))
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        cv.imwrite('out/ranges.jpg', Draw.draw_range(frame, [config.get('players1')['rectangle'],
                                                        config.get('players2')['rectangle']]))

        cv.imwrite('out/res.jpg', Draw.draw_rectangles(frame, separated_players))

    cap.release()
    cv.destroyAllWindows()