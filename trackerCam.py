
import cv2
import numpy as np
import sys
import time
import socket
import select
import errno


(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

if __name__ == '__main__' :

    HEADER_LENGTH = 10

    IP = "127.0.0.1"
    PORT = 1234
    my_username = input("Username (equipe_role ex: 1_p1): ")
    start = 'n'
    my_role = my_username[2]

    # Create a socket
    # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
    # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to a given ip and port
    client_socket.connect((IP, PORT))

    # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
    client_socket.setblocking(False)

    # Prepare username and header and send them
    # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)

    def receive_message(client_socket):

        try:

            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                return False

            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:

            # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
            # or just lost his connection
            # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
            # and that's also a cause when we receive an empty message
            return False


    # initialize a dictionary that maps strings to their corresponding
    # OpenCV object tracker implementations
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }

    # Read camera
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FPS, 30.0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    #video = cv2.VideoCapture("drap4.mp4")

    # Read paddle picture
    src1 = cv2.imread(cv2.samples.findFile("paggai.png") )

    # used to record the time when we processed last frame 
    prev_frame_time = 0
      
    # used to record the time at which we processed current frame 
    new_frame_time = 0

    #pour timer
    once = 0
    t = 10
    start_time = time.time()
    
    #pour pagayeur
    lastp1 = 0
    lastp2 = 0 #les deux derniers coordonnées stockées
    nbEnvoip = 1 #nb de renvois depuis le dernier top
    
    #pour batteur
    lastb1 = 0
    lastb2 = 0 #les deux derniers coordonnées stockées
    nbEnvoib = 1 #nb de renvois depuis le dernier top

    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open camera")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    #flip the camera
    frame = cv2.flip(frame, 1)
    if not ok:
        print ("Cannot read camera frame")
        sys.exit()
    
    # Define an initial bounding box
    #bbox1 = (80, 30, 50, 50)
    bbox2 = (185, 190, 30, 30)

    # Select boxes
    bboxes = []
    #bboxes.append(bbox1)       
    bboxes.append(bbox2)  
    
    # Create MultiTracker object
    multiTracker = cv2.MultiTracker_create()

    p1 = (0,0)
    # Initialize tracker with first frame and bounding box
    #ok = tracker.init(frame, bbox)   


    ########################################################################################################################################################

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        #flip the camera
        frame = cv2.flip(frame, 1)

        #get frame size
        height, width, depth = frame.shape  

        # get updated location of objects in subsequent frames
        ok, boxes = multiTracker.update(frame)
        
        #timer
        if time.time() - start_time <= t:
            src1 = cv2.resize(src1,(width, height))
            cv2.addWeighted( src1, 0.5, frame, 0.5, 0.0, frame);
            for box in bboxes:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Display Timer on console
            times = t - int(time.time() - start_time)
            mins, secs = divmod(times, 60) 
            timer = '{:02d}:{:02d}'.format(mins, secs) 

            # Display Timer on frame
            cv2.putText(frame, "TIMER : " + str(timer), (300,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
            print(timer, end="\r") 
            
        # The tracking start once the timer end
        if int(time.time() - start_time) == t and once == 0:
            once = 1
            for bbox in bboxes:
                tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
                multiTracker.add(tracker, frame, bbox)

            ########################### attendre le start ##########################
            message = 'ready'
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            # send message
            client_socket.send(message_header + message)

            while start != 'y':
                tmp = receive_message(client_socket)
                if tmp != False:
                    start = tmp['data'].decode('utf-8')  


        # time when we finish processing for this frame 
        new_frame_time = time.time() 

        # Calculating the fps 

        # fps will be number of frame processed in given time frame 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
        

        # draw tracked objects
        for box in boxes:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Get the position of the center of the box
        if len(boxes) != 0:
            (x, y, w, h) = [int(v) for v in boxes[0]]
            p1 = (int(x + w/2), int(y + h/2))

            #(x, y, w, h) = [int(v) for v in boxes[1]]
            #p2 = (int(x + w/2), int(y + h/2))

            #cv2.line(frame, p1, p2, (255, 0, 0), 5)
            print("p1 : ", p1)

        # Display tracker type on frame
        cv2.putText(frame, "CSRT Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
    
        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

        # Top si la pagaie est vers l'arrière 
        if my_role == 'p' and p1[0] < lastp1 and lastp1 >= lastp2 and nbEnvoip>6:
            print('TOP  ', 'Vitesse =', fps/nbEnvoip, ' coup de rame/seconde')
            message = 'TOP'
            # Encode message to bytes, prepare header and convert to bytes,  then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            # send message
            client_socket.send(message_header + message)
            #time.sleep(2)
            nbEnvoi = 1
        lastp2 = lastp1
        lastp1 = p1[0]
        nbEnvoip = nbEnvoip + 1
        #time.sleep(0.04)

        # Top si le batteur tape sur le tambour
        if my_role == 'b' and p1[1] < lastb1 and lastb1 >= lastb2 and nbEnvoib>6:
            print('TOP  ', 'Vitesse =', fps/nbEnvoib, ' coup de rame/seconde')
            message = 'TOP'
            # Encode message to bytes, prepare header and convert to bytes,  then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            # send message
            client_socket.send(message_header + message)
            #time.sleep(2)
            nbEnvoi = 1
        lastb2 = lastb1
        lastb1 = p1[1]
        nbEnvoib = nbEnvoib + 1
        #time.sleep(0.04)

        # show frame
        cv2.imshow('MultiTracker', frame)


        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break

        # pour choisir soi-même la taille et possition du tracker en appuyent sur "s"
        if k == ord("s") :  
            bboxes.pop(0)      
            while True:
                # draw bounding boxes over objects
                # selectROI's default behaviour is to draw box starting from the center
                # when fromCenter is set to false, you can draw box starting from top left corner
                bbox = cv2.selectROI('MultiTracker', frame)
                bboxes.append(bbox)
                print("Press q to quit selecting boxes and start tracking")
                print("Press any other key to select next object")
                k = cv2.waitKey(0) & 0xFF
                if (k == 113):  # q is pressed
                    break

            # Initialize MultiTracker 
            for bbox in bboxes:
                tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
                multiTracker.add(tracker, frame, bbox)

    
    # After the loop release the cap object 
    video.release() 

    # Destroy all the windows 
    cv2.destroyAllWindows()         