import numpy as np
import cv2
cap = cv2.VideoCapture("Batteur sans parole 1.mp4")
# cap = cv2.VideoCapture(0)
roi = False
window_name = 'IMAGE'
rec_color = (255, 0, 0)

h_bins = 50
s_bins = 60
histSize = [h_bins, s_bins]

# hue varies from 0 to 179, saturation from 0 to 255
h_ranges = [0, 180]
s_ranges = [0, 256]
ranges = h_ranges + s_ranges # concat lists
# Use the 0-th and 1-st channels
channels = [0, 1]
top = 0
backToBase = True
while True:
    ret, frame = cap.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    while not roi:
        print("select ROI")

        (x, y, w, h) = cv2.selectROI(window_name, frame)

        #récupérer l'image du tambour sans baton
        img_base = frame[y:y+h, x:x+w]
        hsv_base = cv2.cvtColor(img_base, cv2.COLOR_BGR2HSV)

        hist_base = cv2.calcHist([hsv_base], channels, None, histSize, ranges, accumulate=False)
        cv2.normalize(hist_base, hist_base, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        compare_ref = cv2.compareHist(hist_base, hist_base, cv2.HISTCMP_CORREL)
        print("COMPARE REF : ", compare_ref)

        roi = True

    rect = cv2.rectangle(frame, (x, y), (x + w, y + h), rec_color, 2)
    img_drum = rect[y:y+h, x:x+w]
    hsv_drum = cv2.cvtColor(img_drum, cv2.COLOR_BGR2HSV)

    hist_drum = cv2.calcHist([hsv_drum], channels, None, histSize, ranges, accumulate=False)
    cv2.normalize(hist_drum, hist_drum, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    cv2.imshow(window_name, frame)
    cv2.imshow('cropped', img_drum)

    compare = cv2.compareHist(hist_base, hist_drum, cv2.HISTCMP_CORREL)
    if compare < 0.92 and backToBase:
        backToBase = False
        top += 1
        print("TOP number : ", top)
    if compare <= 1:
        backToBase = True

    print("compare : ", compare)

    # diff_frame = img_drum - img_base
    # print("ref : ", sum(sum(img_base - img_base)))
    # print(sum(sum(diff_frame)))

    # diff_img = cv2.subtract(img_base, img_drum)
    # print("diff: ", diff_img)
    # cv2.normalize(diff_img, diff_img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



