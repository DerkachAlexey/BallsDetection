
import cv2 as cv
import numpy as np
import imutils
import operator

from config import Config

print(cv.ocl.haveOpenCL())
cv.ocl.setUseOpenCL(True)
print(cv.ocl.useOpenCL())

ballsColors = {'red', 'white'}
lowerNumberBallsInLine = {'red': 3, 'white': 6}
upperNumberBallsInLine = {'red': 3, 'white': 6}

#lower = {'red': (165, 100, 170), 'white': (0, 0, 168)}
#upper = {'red': (186, 232, 232), 'white': (160, 30, 255)}

lower = {'red': (160, 100, 100), 'white': (0, 0, 168)}
upper = {'red': (179, 255, 255), 'white': (130, 15, 255)}

class DetectBall:

    def __init__(self, config: Config):

        self.players1 = config.get('players1')
        self.players2 = config.get('players2')

    def calculate_mask(self, frame_hsv, color_lower, color_upper):

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv.inRange(frame_hsv, color_lower, color_upper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        rectangles = [self.players1['rectangle'], self.players2['rectangle']]

        mask_result = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)
        mask_result = cv.cvtColor(mask_result, cv.COLOR_BGR2GRAY)

        for x1, y1, x2, y2 in rectangles:
            mask_result[y1:y2, x1:x2] = mask[y1:y2, x1:x2]

        # elliptical_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7, 7))
        # mask_ = mask.copy()
        # cv.morphologyEx(mask, cv.MORPH_TOPHAT, elliptical_kernel, mask_)
        # mask = mask - mask_

        # rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        # mask_ = mask.copy()
        # cv.morphologyEx(mask, cv.MORPH_GRADIENT, rect_kernel, mask_)
        # mask = mask - mask_

        return mask_result

    def calculate_all_masks(self, frame):

        if frame is None:
            return None

        # resize the frame, blur it, and convert it to the HSV
        # color space
        # frame = imutils.resize(frame, width=600)
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        cv.imwrite('out/blurred.jpg', blurred)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        result = {}

        for color in ballsColors:
            color_lower = lower[color]
            color_upper = upper[color]

            mask = self.calculate_mask(hsv, color_lower, color_upper)

            cv.imwrite('C:/Users/alexey.derkach/Downloads/detectBall/out/mask_' + color + '.jpg', mask)

            result[color] = mask

        return result

    def find_hough_circles(self, image, mask, color):

        blurred = cv.blur(mask, (7, 7))

        #cv.imwrite('C:/Users/alexey.derkach/Documents/Ball/Ball/out/blurred_mask_' + color + '.jpg', mask)
        #print("ss")
        circles = cv.HoughCircles(mask, cv.HOUGH_GRADIENT, 1, 40,
                                  param1=400, param2=4, minRadius=15, maxRadius=20)

        # for test
        # image = imutils.resize(image, width=600)

        result = []

        if circles is not None:
            if len(circles) > 0:

                for x, y, radius in circles[0, :]:

                    if radius > 4:
                        cv.circle(image, (int(x), int(y)), int(radius),
                                  (0, 255, 255), 2)
                        result.append((x, y, radius))

        cv.imwrite('out/circles_' + color + '.jpg', image)
        return result

    def find_circles(self, image, mask, color):
        cnts = cv.findContours(mask.copy(),
                               cv.RETR_EXTERNAL,
                               cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # for test
        # image = imutils.resize(image, width=600)

        result = []

        if len(cnts) > 0:

            for cnt in cnts:

                ((x, y), radius) = cv.minEnclosingCircle(cnt)

                if radius > 3:
                    cv.circle(image, (int(x), int(y)), int(radius),
                              (0, 255, 255), 2)
                    result.append((x, y, radius))

        cv.imwrite('out/circles_' + color + '.jpg', image)
        return result

    def find_circles_groups(self, circles):

        result = []

        used_circles = []
        for firstCircle in circles:

            if firstCircle in used_circles:
                continue

            x, y, radius = firstCircle

            circles_group = []

            for circle in circles:

                if circle in used_circles:
                    continue

                x1, y1, radius1 = circle

                a = (radius / radius1 - 1.0) if (radius / radius1 > 1.0) else (radius1 / radius - 1.0)

                if (a < 3.0) and (abs(y - y1) < 20):
                    circles_group.append((x1, y1, radius1))
                    used_circles.append(circle)

            result.append(circles_group)

        return result

    def filtration_groups(self, circles_groups, color):

        result = []

        for circles_group in circles_groups:

            if not ((lowerNumberBallsInLine[color] <= len(circles_group)) and
                    (len(circles_group) <= upperNumberBallsInLine[color])):
                continue

            result.append(circles_group)

        return result

    def find_lines(self, image_gray):

        img_to_draw = cv.cvtColor(image_gray, cv.COLOR_GRAY2BGR)

        # Detect vertical lines
        vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 10))
        detect_vertical = cv.morphologyEx(image_gray, cv.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv.findContours(detect_vertical, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv.drawContours(img_to_draw, [c], -1, (36, 255, 12), 2)

        cv.imwrite('out/lines.jpg', img_to_draw)

    def find_balls(self, image, hough=False):

        result = {}

        self.find_lines(cv.cvtColor(image, cv.COLOR_BGR2GRAY))

        masks = self.calculate_all_masks(image)

        for mask in masks:

            result[mask] = []

            circles = self.find_hough_circles(image, masks[mask], mask) if hough else \
                self.find_circles(image, masks[mask], mask)
            circles_groups = self.find_circles_groups(circles)

            filtered_circles_groups = self.filtration_groups(circles_groups, mask)

            if len(filtered_circles_groups) > 0:
                result[mask].append(filtered_circles_groups[0])

        return result

    def separate_players(self, balls_groups):

        result = {'players1': {}, 'players2': {}}

        for balls_groups_ in balls_groups:

            result['players1'][balls_groups_] = []
            result['players2'][balls_groups_] = []

            for balls_group_ in balls_groups[balls_groups_]:

                balls_group_players1 = []
                balls_group_players2 = []

                if len(balls_group_) > 0:
                    center_x = np.sum([x for x, y, z in balls_group_]) / \
                               len(balls_group_)

                    for circle in balls_group_:
                        x, y, radius = circle
                        if x < center_x:
                            balls_group_players1.append(circle)
                        else:
                            balls_group_players2.append(circle)

                result['players1'][balls_groups_].append(balls_group_players1)
                result['players2'][balls_groups_].append(balls_group_players2)

        return result

    def find_rectangles(self, separated_players):

        result = {}

        for separated_player in separated_players:

            result[separated_player] = {}

            separated_players_ = separated_players[separated_player]

            for separated_player_color in separated_players_:

                result[separated_player][separated_player_color] = []

                separated_player_color_ = separated_players_[separated_player_color]

                for circles in separated_player_color_:
                    result[separated_player][separated_player_color].append(
                        (int(np.min([x for x, y, radius in circles]) - circles[0][2]),
                         int(circles[0][1] - circles[0][2]),
                         int(np.max([x for x, y, radius in circles]) + circles[0][2]),
                         int(circles[0][1] + circles[0][2])))  # x1, y1, x2, y2

        return result

    def calculate_sets(self, separated_players, rectangles):

        number_of_sets = {'players1': 0, 'players2': 0}

        # for players1
        rectangle = rectangles['players1']['white']
        if len(separated_players['players1']['red']) > 0 and \
                len(rectangle) > 0:
            x1, y1, x2, y2 = rectangle[0]
            for circle in separated_players['players1']['red'][0]:
                if circle[0] < (x1 + x2) / 2:
                    number_of_sets['players1'] += 1
        else:
            number_of_sets['players1'] = None

        # for players2
        rectangle = rectangles['players2']['white']
        if len(separated_players['players2']['red']) > 0 and \
                len(rectangle) > 0:
            x1, y1, x2, y2 = rectangle[0]
            for circle in separated_players['players2']['red'][0]:
                if circle[0] > (x1 + x2) / 2:
                    number_of_sets['players2'] += 1
        else:
            number_of_sets['players2'] = None

        return number_of_sets

    def calculate_games_(self, separated_players, rectangles, player):

        number_of_games = 0

        rectangle = self.players1['rectangle'] if player == 'players1' else self.players2['rectangle']
        if len(separated_players[player]['white']) > 0:
            balls = {x1: (x1, y1, r) for x1, y1, r in separated_players[player]['white'][0]}
            balls = sorted(balls.items(), key=operator.itemgetter(0))

            last_ball = None
            for ball in balls:
                x, y, r = ball[1]

                if last_ball is None:
                    last_ball = ball
                    if (x - rectangle[0]) < 4 * r:
                        number_of_games += 1
                    else:
                        break
                else:
                    if (x - last_ball[0]) < 4 * r:
                        last_ball = ball
                        number_of_games += 1
                    else:
                        break

            return number_of_games

        return None

    def calculate_games(self, separated_players, rectangles):

        number_of_games = {'players1': 0, 'players2': 0}

        # for players1
        number_of_games['players1'] = None if self.calculate_games_(separated_players, rectangles, 'players1')==None \
            else self.calculate_games_(separated_players, rectangles, 'players1')

        # for players2
        number_of_games['players2'] = None if self.calculate_games_(separated_players, rectangles, 'players2')==None \
            else 6 - self.calculate_games_(separated_players, rectangles, 'players2')

        return number_of_games