import cv2
import imutils
from imutils.video import WebcamVideoStream as wvs
import numpy as np

hmin = 0
hmax = 360
smin = 50
smax = 255
vmin = 110
vmax = 255

red_hue = 0, 7
orange_hue = 10, 20
lime_hue = 33, 48
sky_hue = 92, 105
green_hue = 65, 79

hues = (red_hue, orange_hue, lime_hue, green_hue, sky_hue)

def set_hue(x):
    global hmin
    global hmax
    hmin, hmax = hues[x]

def set_hmin(x):
    global hmin
    hmin = x

def set_hmax(x):
    global hmax
    hmax = x

def set_smin(x):
    global smin
    smin = x

def set_smax(x):
    global smax
    smax = x

def set_vmin(x):
    global vmin
    vmin = x

def set_vmax(x):
    global vmax
    vmax = x

def get_color(h):
    if h < 8:
        # red
        return (0, 255, 0)
    if h < 25:
        # orange
        return (230, 102, 23)
    if h < 50:
        # lime
        return

def largest_single_color(frame, hues):
    largest = None
    poss = None
    lineColor = None
    
    for hmin, hmax in hues:
        mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(filter(lambda cont: len([pt for pt in cont if pt[0][1] < 150]) == 0, contours))
        if len(contours) > 0:
            poss = max(contours, key=cv2.contourArea)
            
            if largest is None or cv2.contourArea(poss) > cv2.contourArea(largest):
                largest = poss
                lineColor = (int(hmin + (hmax-hmin)/2), 240, 240)
    return largest, lineColor

def largest_merge_colors(frame, hues):
    mask = None
    for hmin, hmax in hues:
        if mask is None:
            mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        else:
            mask = cv2.bitwise_or(mask, cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax)))
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(filter(lambda cont: len([pt for pt in cont if pt[0][1] < 150]) == 0, contours))
    if len(contours) > 0:
        cont = max(contours, key=cv2.contourArea)
        lineColor = (5, 240, 240)
    else:
        cont = None
        lineColor = None
    return (cont, lineColor)

def get_black_image(frame):
    out = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))
    return cv2.bitwise_or(frame, frame, mask=out)
    

def draw_cont(img, cont, color):
    m = cv2.moments(cont)
    if m["m00"] != 0:
        cv2.circle(img, (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])), 5, color, -1)
    cv2.drawContours(img, [cont], 0, color, 3)

def check_cont(cont):
    return cv2.approxPolyDP(cont, 0.005*cv2.arcLength(cont, True), True)

def get_side(cont):
    m = cv2.moments(cont)
    if m["m00"] == 0:
        return None
    y = int(m["m01"]/m["m00"])
    x = int(m["m10"]/m["m00"])
    if -(x*91/95) + 127+(480*91/95) > y:
        return -1 # left
    if x*91/95 + 127-(480*91/95) > y:
        return 1 # right
    return 0 # forward
    
side_color = {
    -1: (300, 240, 240),
    0: (0, 0, 255),
    1: (120, 240, 240)
    }

# y - y1 = m(x-x1)
# y = mx - mx1 + y1
# y = mx + (y1 - mx1)
# (0, y1 - mx1), (w, mw + y1 - mx1

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
    v.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_width)
    v.set(cv2.CAP_PROP_FRAME_WIDTH, cap_height)
    v.set(cv2.CAP_PROP_FPS, 24)
    while True:
        _, frame = v.read()
        if frame is None:
            break

        frame = cv2.resize(frame, (w,h), interpolation=cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        #frame = cv2.bitwise_or(frame, frame, mask=mask)
        #frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        out = frame
    
        cont, color = largest_single_color(frame, hues)
        if cont is not None:
            draw_cont(out, cont, color)
            cont = check_cont(cont)
            draw_cont(out, cont, color)
        cont, color = largest_merge_colors(frame, hues)
        if cont is not None:
            draw_cont(out, cont, color)
            m = cv2.moments(cont)
            side = get_side(cont)
            if side is not None:
                cv2.line(out, (int(m["m10"] / m["m00"]), 0), (int(m["m10"] / m["m00"]), 480), side_color[side], 2)
            cont = check_cont(cont)
            draw_cont(out, cont, color)
        cv2.line(out, (0, int(0.3125*h)), (w, int(0.3125*h)), (0, 0, 0), 1)
        cv2.line(out, (int(w/2), 0), (int(w/2), h), (0, 0, 0), 1)
        cv2.line(out, (0, int(127+(w/2)*91/95)), (w, int(-(w*91/95) + 127+(w/2)*91/95)), (0, 240, 240), 1)
        cv2.line(out, (0, int(127-(w/2)*91/95)), (w, int((w*91/95)+127-(w/2)*91/95)), (0, 240, 240), 1)
        out = cv2.cvtColor(out, cv2.COLOR_HSV2BGR)
        cv2.imshow("res", out)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    #v.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# at 220, (420-230) = 190 -> 1ft
# at 260, (460-190) = 270 -> 1ft
# at 350, (555-90) = 465 -> 1ft
# at 400, (605-40) = 565 -> 1ft
