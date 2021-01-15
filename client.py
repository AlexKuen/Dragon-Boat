import socket
import select
import errno
import time

HEADER_LENGTH = 10

IP = input("adresse IP du serveur : ")
PORT = int(input("PORT du serveur : "))
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



################################################################# code à modifier ######################################################################

# nombre d'envoi de données par seconde afin de calculer la vitesse
EPS = int(input("Entrez le nombre d'envoi de coordonnées par seconde : "))

# Coordonnés arbitraires pour l'instant
coords = [[260,160],[270,153],[395,146],[330,139],[365,133],[395,126],[420,120],[450,111],[478,100],[505,95],[530,98],[555,107],[580,115],[600,120],[566,124],[532,128],[498,132],[464,136],[430,140],[396,144],[362,148],[284,155]]

i = 0
last1 = 0
last2 = 0   # les deux dernieres coordonnées stockées
nbEnvoi = 0 # nb de renvois depuis le dernier top

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
        print("5")
        time.sleep(1)
        print("4")
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        print("PARTEZ!")


########################################################################

if my_role == 'p':
    while True:

        for i in range (len(coords)):
            print(coords[i][0], coords[i][1], sep=",")
            if coords[i][1] > last1 and last1 < last2 and nbEnvoi > 6:
                print('TOP  ', 'Vitesse =', EPS/nbEnvoi, ' coup de rame/seconde')
                message = 'TOP'
                # Encode message to bytes, prepare header and convert to bytes,  then send
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                # send message
                client_socket.send(message_header + message)
                nbEnvoi = 0
            last2 = last1
            last1 = coords[i][1]
            nbEnvoi = nbEnvoi + 1
            time.sleep(0.04)

else:
    # code pour le batteur
    while True:

        for i in range (len(coords)):
            print(coords[i][0], coords[i][1], sep=",")
            if coords[i][1] > last1 and last1 < last2 and nbEnvoi > 6:
                print('TOP  ', 'Vitesse =', EPS/nbEnvoi, ' coup de rame/seconde')
                message = 'TOP'
                # Encode message to bytes, prepare header and convert to bytes,  then send
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                # send message
                client_socket.send(message_header + message)
                nbEnvoi = 0
            last2 = last1
            last1 = coords[i][1]
            nbEnvoi = nbEnvoi + 1
            time.sleep(0.04)

########################################################################################################################################################