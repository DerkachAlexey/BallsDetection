import cv2 as cv
import numpy as np
import imutils


class Draw:

    @staticmethod
    def draw_range(image, rectangles):

        for x1, y1, x2, y2 in rectangles:
            image = cv.rectangle(image, (x1, y1), (x2, y2), (255, 255, 0), 3)

        image = imutils.resize(image.copy(), width=600)

        return image

    @staticmethod
    def draw_rectangles(image, separated_players):

        for separated_player in separated_players:

            separated_players_ = separated_players[separated_player]

            for separated_player_color in separated_players_:

                separated_player_color_ = separated_players_[separated_player_color]

                for circles in separated_player_color_:
                    #print((np.min([x for x, y, radius in circles]), circles[0][1]))

                    image = cv.rectangle(image,
                                         (int(np.min([x for x, y, radius in circles]) - circles[0][2]),
                                          int(circles[0][1] - circles[0][2])),
                                         (int(np.max([x for x, y, radius in circles]) + circles[0][2]),
                                          int(circles[0][1] + circles[0][2])),
                                         (255, 0, 0) if separated_player == 'players1' else (0, 255, 0), 3)

        image = imutils.resize(image.copy(), width=600)

        return image