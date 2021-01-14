import socket
import select
import time
import sys

HEADER_LENGTH = 10

IP = input("adresse IP du serveur : ")
PORT = int(input("PORT du serveur : "))

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}
# Tableau contenant les username
username = {}
# Tableau contenant l'equipe de la personne
team = {}
# Tableau contenant le role de la personne
role = {}
# Tableau contenant la position de la personne
rolePosition = {}
# Tableau team 1
team1 = []
# Tableau team 2
team2 = []

TOP_tab = []
TOP_bat = 0

size_team = 1
start = 'n'

tmp = False


FacteurVitesse = 0.167  #Conversion Coup de pagaie/minutes > km/heure
ReductionPagayeur = 0.05  #réduction de la vitesse par pagayeur absent (10 pagayeur de base)
ToléranceSyncro = 0.05  #seuil de syncro au dessus duquel on a des malus
FacteurPerteSyncro = 1  #importance de la syncro


#index coordination qui compte le nombre de TOP reçu dans un cycle (toutes les personnes ont fait un TOP)
z = 0
zMAX = int(input("Nombre de personne dans l'equipe (batteur inclu) : "))

vitesseFinale = 0
VitBatteur = 1

deltaTOT = 0
deltaMoyen = 0
decalage = 0

distanceAParcourir = int(input("Distance à parcourir(en mètres) : ")) # distance en mètres
distanceParcourue = 0

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
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

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            ####################################################### INITIALISATION DONNEES ################################################################
            
            # Also save username and username header
            clients[client_socket] = user
            # sauvegarder le username en clair
            username[client_socket] = user['data'].decode('utf-8')
            # sauvegarder l'equipe
            team[client_socket] = username[client_socket][0]
            # sauvegarder le role
            role[client_socket] = username[client_socket][2]
            # sauvegarder la position
            rolePosition[client_socket] = username[client_socket][3]

            if team[client_socket] == 1:
                team1.append(client_socket)
            else:
                team2.append(client_socket)

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            ###############################################################################################################################################

        # Else existing socket is sending a message
        else:

            ###################### message de start #########################

            tmp = receive_message(notified_socket)
            
            if tmp['data'].decode('utf-8') == 'ready':
                start = input("start? (y) : ")
                tmp = False

                # If message is not empty - send it
                if start:

                    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                    start = start.encode('utf-8')
                    start_header = f"{len(start):<{HEADER_LENGTH}}".encode('utf-8')

                    # Iterate over connected clients and broadcast message
                    for client_socket in clients:

                        # Send message
                        client_socket.send(start_header + start)

            ##################################################################

            # Receive message
            message = receive_message(notified_socket)


            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]
                del username[notified_socket]
                del team[notified_socket]
                del role[notified_socket]
                del rolePosition[notified_socket]
                #for i in team1:
                #    if team1[i] == notified_socket:
                #        del team1[i]
                #for j in team2:
                #    if team2[j] == notified_socket:
                #        del team2[j]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            ############################# coordination pagayeurs/batteur ###################################

            vitesseFinale = (1/VitBatteur) * 60 * 0.167 * (1-ReductionPagayeur*(11-zMAX))    #vitesse avant changement

            # on stocke le moment où le batteur fait un TOP
            if role[notified_socket] == 'b':
                TOP_bat = time.time()
                z+=1

            # on stocke le moment où les pagayeurs font un TOP
            else: 
                TOP_tab.append(time.time())
                z+=1

            # quand tout le monde a fait un TOP on calcule l'écart total
            if z == zMAX:
                for h in TOP_tab:
                    deltaTOT += abs(h - TOP_bat)
                # utiliser deltaTOT pour calculer la vitesse
                print("deltaTOP = ", deltaTOT)
                deltaMoyen = deltaTOT/(zMAX-1)
                decalage = deltaMoyen/VitBatteur
                if decalage>0.05:
                    vitesseFinale = vitesseFinale*(1-(decalage*FacteurPerteSyncro))
                    #if vitesseFinale < 0:
                    #    vitesseFinale = 0
                print("Vitesse Finale (km/h) = ", vitesseFinale)
                distanceParcourue += VitBatteur * (vitesseFinale/3.6)
                print("Distance parcourue = ", distanceParcourue, " / ", distanceAParcourir)
                if distanceParcourue >= distanceAParcourir:
                    print("FINISH!")
                    time.sleep(10)
                    sys.exit()
                # reset des variables
                z = 0
                deltaTOT = 0
                TOP_tab.clear()


            #################################################################################################


