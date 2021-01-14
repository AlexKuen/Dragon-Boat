
import numpy as np
import cv2

cap=cv2.VideoCapture(0)
#cap=cv2.VideoCapture("scotc_rouge2.mp4")

orb = cv2.ORB_create()


ret, originale=cap.read()
img_clone = originale.copy()
kp0, des0 = orb.detectAndCompute(img_clone, None)

while True:

    ret, frame=cap.read()
    kp1, des1 = orb.detectAndCompute(frame, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des0, des1)
    matches = sorted(matches, key=lambda x: x.distance)
    img_BF = cv2.drawMatches(originale, kp0, frame, kp1, matches, None, flags=2)
    #cv2.imshow("Image_match1", img_BF)

    pts0 = []
    pts1 = []

    for match in matches:
        pts0.append(kp0[match.queryIdx].pt)
        pts1.append(kp1[match.trainIdx].pt)

    pts0 = np.array(pts0)
    pts1 = np.array(pts1)

    h, status = cv2.findHomography(pts0, pts1, cv2.RANSAC)

    g_kp0 = []
    g_kp1 = []
    g_des0 = []
    g_des1 = []

    stop_list = []

    for i, stat in enumerate(status):
        stop = 0
        x0, y0 = kp0[matches[i].queryIdx].pt
        x1, y1 = kp1[matches[i].trainIdx].pt
        #récupération des points ou il y a un match décallé d'au moins un pixel
        if (x1-1 <= x0 <= x1+1 or y1-1 <= y0 <= y1+1):
            stop_list.append([x0, y0])

        #bloque l'affichage de points considérés comme immobile
        for j in stop_list:
            if j[0] == x1 and j[1] == y1:
                stop = 1

        #récupération des vrais points communs entre les deux frames
        if stat == 1 and stop == 0:
            g_kp0.append(kp0[matches[i].queryIdx])
            g_kp1.append(kp1[matches[i].trainIdx])
            g_des0.append(des0[matches[i].queryIdx])
            g_des1.append(des1[matches[i].trainIdx])

    g_des0 = np.array(g_des0)
    g_des1 = np.array(g_des1)

    matches2 = bf.match(g_des0, g_des1)
    matches2 = sorted(matches2, key=lambda x: x.distance)
    img_BF = cv2.drawMatches(originale, g_kp0, frame, g_kp1, matches2, None, flags=2)

    #affichage des deux frames avec leurs points commun respectifs
    cv2.imshow("Image_match2", img_BF)
    #affichage des points d'interets dans la frame courante
    img2_kp = cv2.drawKeypoints(frame, g_kp1, None, color=(0, 255, 0))
    cv2.imshow("test", img2_kp)
    cv2.imshow("frame", frame)

    #récupération de la frame t pour être utilisé à la frame t+1
    originale = frame.copy()
    kp0 = kp1
    des0 = des1

    key=cv2.waitKey(30)&0xFF
    if key==ord('q'):
        break


cap.release()
cv2.destroyAllWindows()