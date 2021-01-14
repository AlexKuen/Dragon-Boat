import numpy as np
import cv2

cap = cv2.VideoCapture(0)

img2 = cv2.imread('image.png',0)


while(cap.isOpened()):
    orb = cv2.ORB_create()
    ret, img1 = cap.read()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    pts1 = []
    pts2 = []

    #récupération de tous les matchs triés
    for match in matches:
        pts1.append(kp1[match.queryIdx].pt)
        pts2.append(kp2[match.trainIdx].pt)

    pts1 = np.array(pts1)
    pts2 = np.array(pts2)

    h, status = cv2.findHomography(pts1, pts2, cv2.RANSAC)

    g_kp1 = []
    g_kp2 = []
    g_des1 = []
    g_des2 = []

    stop_list = []

    #suppression des faux-positifs, permettants de supprimer tous les liens inexacts
    for i, stat in enumerate(status):
        if stat == 1:
            g_kp1.append(kp1[matches[i].queryIdx])
            g_kp2.append(kp2[matches[i].trainIdx])
            g_des1.append(des1[matches[i].queryIdx])
            g_des2.append(des2[matches[i].trainIdx])

    g_des1 = np.array(g_des1)
    g_des2 = np.array(g_des2)

    matches2 = bf.match(g_des1, g_des2)
    matches2 = sorted(matches2, key=lambda x: x.distance)


    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches2[:10], None, flags=2)
    cv2.imshow("frame", img3)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break

