import cv2
import numpy as np

video = cv2.VideoCapture("scotc_rouge2.mp4")

def onMouse(event,x,y,flags,param):
    global i0, j0
    if event == cv2.EVENT_LBUTTONUP:
        j0 = x
        i0 = y
        print(i0, j0)

if (video.isOpened() == False):
    print("Error Opening Video Stream or files")

while(video.isOpened()):
    ret, frame =video.read()

    if ret == True:

        blurred_img = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([160, 110, 80])
        upper_red = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        centre = 0

        #détection de les morceaux contenant la couleur dans la frame en cours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:

            area = cv2.contourArea(contour)

            # Détection d'une zone de couleur de plus de 15
            if area > 15:
                red = cv2.bitwise_and(frame, frame, mask=mask)
                M = cv2.moments(contour)
                contourX = int(M["m10"] / M["m00"])
                contourY = int(M["m01"] / M["m00"])

                # Permet l'affichage d'un cercle au centre de la zone de couleur
                if(contourY>300):
                    print("X:"+str(contourX)+"     Y:"+str(contourY))
                    cv2.circle(frame, (contourX, contourY), 5, (0, 255, 0), -1)
                    centre += 1

                    #création d'une ligne entre les deux points scotchs pour simulier la pagaie
                    if centre == 1:
                       centreX1 = contourX
                       centreY1 = contourY
                    if centre == 2:
                        centreX2 = contourX
                        centreY2 = contourY
                        cv2.line(frame, (centreX1, centreY1), (centreX2, centreY2), (0, 0, 255), 5)

        cv2.imshow("Frame", frame)
        cv2.imshow("Red", red)
        cv2.setMouseCallback('Frame', onMouse)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break

    else:
        break