import cv2
import imutils
from imutils.video import WebcamVideoStream as wvs

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
    # create a black image to draw contours on
    out = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))
    out = cv2.bitwise_or(frame, frame, mask=out)
    
    for hmin, hmax in hues:
        mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            poss = max(contours, key=cv2.contourArea)
            
            if largest is None or cv2.contourArea(poss) > cv2.contourArea(largest):
                largest = poss
                lineColor = (int(hmin + (hmax-hmin)/2), 240, 240)
    if largest is not None:
        m = cv2.moments(largest)
        cv2.circle(out, (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])), 5, lineColor, -1)
        cv2.drawContours(out, [largest], 0, lineColor, 3)
    out = cv2.cvtColor(out, cv2.COLOR_HSV2BGR)
    return out    

def largest_merge_colors(frame, hues):
    # create a black image to draw contours on
    out = cv2.inRange(frame, (0, 0, 0), (0, 0, 0))
    out = cv2.bitwise_or(frame, frame, mask=out)
    mask = None
    for hmin, hmax in hues:
        if mask is None:
            mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        else:
            mask = cv2.bitwise_or(mask, cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax)))
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        cont = max(contours, key=cv2.contourArea)
        m = cv2.moments(cont)
        lineColor = (5, 240, 240)
        cv2.circle(out, (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])), 5, lineColor, -1)
        cv2.drawContours(out, [cont], 0, lineColor, 3)
    out = cv2.cvtColor(out, cv2.COLOR_HSV2BGR)
    return out

def main():
    #global hmin
    #global hmax
    cv2.namedWindow("res")

    #hmin, hmax = red_hue
    
    #cv2.createTrackbar("Hue: red, orange, lime, green, sky", "res", 0, 4, set_hue)
    #cv2.createTrackbar("H max", "res", hmax, 360, set_hmax)
    cv2.createTrackbar("S min", "res", smin, 255, set_smin)
    cv2.createTrackbar("S max", "res", smax, 255, set_smax)
    cv2.createTrackbar("V min", "res", vmin, 255, set_vmin)
    cv2.createTrackbar("V max", "res", vmax, 255, set_vmax)
    v = wvs(src=1).start()
    while True:
        frame = v.read()
        if frame is None:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(frame, (hmin, smin, vmin), (hmax, vmax, smax))
        #frame = cv2.bitwise_or(frame, frame, mask=mask)
        #frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        out = largest_merge_colors(frame, hues)
        cv2.imshow("res", out)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    #v.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
