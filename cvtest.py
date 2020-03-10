import cv2
import numpy as np
import os
import serial
from typing import Iterable, Tuple

def get_black_image(frame):
    out = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))
    return cv2.bitwise_or(frame, frame, mask=out)

def check_cont(cont):
    return cv2.approxPolyDP(cont, 0.005*cv2.arcLength(cont, True), True)

# y - y1 = m(x-x1)
# y = mx - mx1 + y1
# y = mx + (y1 - mx1)
# (0, y1 - mx1), (w, mw + y1 - mx1

class LegoTracker:
    def __init__(self,
                 hues: Iterable[Tuple[int,int]],
                 saturation_min: int,#Tuple[int,int],
                 value_min: int,#Tuple[int,int],
                 boundary_slope: float,
                 boundary_yint: int,
                 horizon: int,
                 width: int,
                 height: int,
                 find_single: bool,
    ):
        self.hues = hues
        self.saturation_range = (saturation_min, 255)
        self.value_range = (value_min, 255)
        self.boundary_slope = boundary_slope
        self.boundary_yint = boundary_yint
        self.horizon = horizon
        self.width = width
        self.height = height
        self.find_single = find_single
        self.current_size = None
        self.current_direction = None
        self.side_color = {
            -1: (300, 240, 240),
            0: (0, 0, 255),
            1: (120, 240, 240)
            }

    def get_max_contour(self, contours):
        contours = filter(lambda cont: len([pt for pt in cont if pt[0][1] < self.horizon]) == 0 and cv2.contourArea(cont) > 100, contours)
        return max(contours, key=cv2.contourArea, default=None)
        
    def largest_merge(self, frame):
        mask = None
        smin, smax = self.saturation_range
        vmin, vmax = self.value_range
        for hmin, hmax in self.hues:
            if mask is None:
                mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, smax, vmax))
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(frame, (hmin, smin, vmin), (hmax, smax, vmax)))
        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return self.get_max_contours(contours), (5, 240, 240)

    def largest_single(self, frame):
        largest = None
        lineColor = None
        smin, smax = self.saturation_range
        vmin, vmax = self.value_range
        for hmin, hmax in self.hues:
            mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, smax, vmax))
            _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            poss = self.get_max_contour(contours)
            if poss is not None and (largest is None or cv2.contourArea(poss) > cv2.contourArea(largest)):
                largest = poss
                lineColor = (int(hmin + (hmax-hmin)/2), 240, 240)
        return largest, lineColor

    def get_side(self, moment):
        if moment["m00"] == 0:
            return None
        y = int(moment["m01"]/moment["m00"])
        x = int(moment["m10"]/moment["m00"])
        if -x*self.boundary_slope + self.boundary_yint + ((self.width/2)*self.boundary_slope) > y:
            return -1 # left
        if x*self.boundary_slope + self.boundary_yint - ((self.width/2)*self.boundary_slope) > y:
            return 1 # right
        return 0

    def get_contour(self, frame):
        if self.find_single:
            return self.largest_single(frame)
        else:
            return self.largest_merge(frame)
    
    def draw_contour(self, frame, cont, color):
        if cont is not None:
            m = cv2.moments(cont)

            # draw COM and direction line
            if m["m00"] != 0:
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
                side = self.get_side(m)
                if side is not None:
                    cv2.line(frame, (cx, 0), (cx, self.height), self.side_color[side], 2)

                cv2.circle(frame, (cx, cy), 5, color, -1)
            cv2.drawContours(frame, [cont], 0, color, 3)
            
    def draw_guides(self, frame):
        # horizon
        cv2.line(frame, (0, self.horizon), (self.width, self.horizon), (0, 0, 0), 1)
        # center line
        cv2.line(frame, (int(self.width/2), 0), (int(self.width/2), self.height), (0, 0, 0), 1)

        # boundary lines
        # left
        cv2.line(frame, (0, int(self.boundary_yint+((self.width/2)*self.boundary_slope))), (self.width, int(-self.width*self.boundary_slope + self.boundary_yint+((self.width/2)*self.boundary_slope))), (0, 240, 240), 1)
        # right
        cv2.line(frame, (0, int(self.boundary_yint-((self.width/2)*self.boundary_slope))), (self.width, int(self.width*self.boundary_slope + self.boundary_yint-((self.width/2)*self.boundary_slope))), (0, 240, 240), 1)

    def write_text(self, frame):
        
        directions = {
            -1: "Left",
            0: "Forward",
            1: "Right",
            None: "Search",
        }

        direction = "Direction: " + directions[self.current_direction]
        
        color = self.side_color.get(self.current_direction, (0, 240, 240))

        cv2.putText(frame, direction, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.putText(frame, "Size: "+str(self.current_size), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
    def update(self, frame, draw=False):
        cont, color = self.get_contour(frame)
        if cont is not None:
            self.current_size = cv2.contourArea(cont)
        self.current_direction = self.get_side(cv2.moments(cont))
        if draw:
            self.draw_contour(frame, cont, color)
            self.draw_guides(frame)
            self.write_text(frame)

def main():
    #global hmin
    #global hmax
    cv2.namedWindow("res")
    
    #hmin, hmax = red_hue
    
    #cv2.createTrackbar("Hue: red, orange, lime, green, sky", "res", 0, 4, set_hue)
    #cv2.createTrackbar("H max", "res", hmax, 360, set_hmax)
    #cv2.createTrackbar("S min", "res", smin, 255, set_smin)
    #cv2.createTrackbar("S max", "res", smax, 255, set_smax)
    #cv2.createTrackbar("V min", "res", vmin, 255, set_vmin)
    #cv2.createTrackbar("V max", "res", vmax, 255, set_vmax)
    v = cv2.VideoCapture(1)
    cap_width = 1920
    cap_height = 1080
    w = int(cap_width/2)
    h = int(cap_height/2)

    red_hue = 0, 7
    orange_hue = 10, 20
    lime_hue = 33, 48
    sky_hue = 92, 105
    green_hue = 65, 79
    
    hues = (red_hue, orange_hue, lime_hue, green_hue, sky_hue)

    tracker = LegoTracker(hues, 50, 110, -1.519, 1.320, 616, -665, 0, w, h, True)

    v.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_width)
    v.set(cv2.CAP_PROP_FRAME_WIDTH, cap_height)
    v.set(cv2.CAP_PROP_FPS, 24)

    comm = None
    comm_text = "No connection"
    debug = True
    while True:
        _, frame = v.read()
        if frame is None:
            break
        inp = cv2.waitKey(1) & 0xFF
        if inp == ord("q"):
            break
        if inp == ord("s"):
            tracker.find_single = not tracker.find_single
        if inp == ord("d"):
            debug = not debug

        frame = cv2.resize(frame, (w,h), interpolation=cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        #frame = cv2.bitwise_or(frame, frame, mask=mask)
        #frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        out = frame

        tracker.update(out, draw=debug)
        if inp == ord("c"):
            if comm is None or comm.closed():
                if os.path.exists("/dev/ttyUSB0"):
                    path = "/dev/ttyUSB0"
                elif os.path.exists("/dev/ttyACM0"):
                    path = "/dev/ttyACM0"
                else:
                    path = None
                if path is not None:
                    cv2.putText(out, "Connecting...", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 240), 1)
                    try:
                        comm = serial.Serial(path, 9600, write_timeout=0)
                    except serial.SerialExcpetion:
                        pass
                    if comm is not None:
                        comm_text = "Connected on " + path
                    else:
                        comm_text = "No connection"
        else:
            cv2.putText(out, comm_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 240), 1)
        
        # draw the image - convert to BGR since cv2 uses bgr to draw
        out = cv2.cvtColor(out, cv2.COLOR_HSV2BGR)
        cv2.imshow("res", out)


    #v.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# at 220, (420-230) = 190 -> 1ft
# at 260, (460-190) = 270 -> 1ft
# at 350, (555-90) = 465 -> 1ft
# at 400, (605-40) = 565 -> 1ft
# 357 609 @ 107
# 50, 540 and 960/2 - 125, 107
# 913, 540 and 960/2 + 125, 107
