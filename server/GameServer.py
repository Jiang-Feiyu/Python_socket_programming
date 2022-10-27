# Author: Jiang Feiyu
# UID: 3035770800
# Comp3234 Assignment1
import socket
import sys
import os
import threading
import time
import random

num_player_lock = threading.Lock() #mutex lock for modifying number_of_player_in_room array
number_of_room = 10
number_of_player_in_room = [] #Global variable: array[number_of_room] containing the number of players in room

response_lock = threading.Lock() #mutex lock for modifying responses 2D array
responses = [] #Global variable: 2D array[number_of_room][2] containing the response from client
result = [] #Global variable: array[number_of_room] containing the random result generated

judging_lock = threading.Lock() #mutex lock for judging who is the winner

for i in range(0, number_of_room): #initialize all the arrays
	number_of_player_in_room.append(0)
	responses.append(["waiting","waiting"])
	result.append("null")
 
class ServerThread(threading.Thread):
    def __init__(self, client, pathToUserInfo):
        threading.Thread.__init__(self)
        self.client = client
        self.pathToUserInfo = pathToUserInfo
        self.connSocket, self.connAddr = self.client
        
    def msg_send(self, msg): #for sending message and handle exception
        try:
            self.connSocket.send(msg.encode('ascii'))
        except socket.error as emsg:
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has disconnected unexpectedly")
            self.connSocket.close()
            sys.exit(1)
    
    def msg_receive(self): #for recieving message and handle exception
        try:
            msg = self.connSocket.recv(10000).decode('ascii') #receive client message
            return msg
        except socket.error as emsg:
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has disconnected unexpectedly")
            self.connSocket.close()
            sys.exit(1)
    
    def acquire_lock(self, type): #for acquiring the mutex lock, and displaying log in server
        if type == "NUM":
            num_player_lock.acquire()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has acquired NUM lock")
        elif type == "RES":
            response_lock.acquire()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has acquired RES lock")
        elif type == "JUD":
            judging_lock.acquire()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has acquired JUD lock")

    def release_lock(self, type): #for acquiring the mutex lock, and displaying log in server
        if type == "NUM":
            num_player_lock.release()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has released NUM lock")
        elif type == "RES":
            response_lock.release()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has released RES lock")
        elif type == "JUD":
            judging_lock.release()
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has released JUD lock")
            
    def clear_room(self, room_number): #for reseting both arrays for use of next clients, only applicable when both threads has disconnected unexpectedly
        print("Thread: Room " + str(room_number-1) + " begin clean up")
        self.acquire_lock("NUM")
        number_of_player_in_room[room_number-1] = 0
        self.release_lock("NUM")
        
        self.acquire_lock("RES")
        responses[room_number-1][0] = "waiting"
        responses[room_number-1][1] = "waiting"
        result[room_number-1] = "null"
        self.release_lock("RES")
        print("Thread: Room " + str(room_number-1) + " finish clean up")

    def authentication(self,username,password,pathToUserInfo):
        # 1.1 Authentication
        authentication_status = 0
        match = 0
        self.username = username
        while match  == 0:
            # read the user database
            try:
                userInfoFile = open(pathToUserInfo, "r")
            except OSError as emsg:
                print("Thread: OSError: " + str(emsg))
                userInfoFile.close()
                sys.exit(1)
            # match the name and password
            user_auth_to_compare = username + ':' + password
            user_auth_list = userInfoFile.readlines()#put all info into a list
            for line in user_auth_list:
                if user_auth_to_compare == line.strip(): #Matching line
                    match = 1
                    authentication_status = 1
                    break
            userInfoFile.close()
            match = 1
        
        if authentication_status == 1:
            self.msg_send("1001 Authentication successful")
            return 1
        else:
            self.msg_send("1002 Authentication failed")
            print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has failed to authenticate")
			        
    def run(self):
        #login
        pathToUserInfo = self.pathToUserInfo
        client_state = 0 #used to record the status of client
        authentication_status = 0
        while authentication_status == 0:
            msg = self.msg_receive()
            try:
                command, username, password = msg.split(' ')
            except ValueError:
                print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has failed to authenticate")
                self.msg_send("1002 Authentication failed")
        
            if command == "/login":
                if (self.authentication(username, password, pathToUserInfo) == 1):
                    authentication_status = 1
        client_state = 1001

        #In the game hall
        while client_state != 4001:
            client_command = self.msg_receive()
            try:
                command, room_number = client_command.split(" ")
                room_number = int(room_number)
            except ValueError:
                self.msg_send("4002 Unrecognized message")
            # try:
			# 		command, room_number = client_command.split(" ")
			# 		room_number = int(room_number)
			# 	except ValueError: #Room number is not an integer OR command is "/enter(any spaces)" only
			# 		self.msg_send("4002 Unrecognized message")
			# 		continue;
					
			# 	if(room_number < 1 or room_number > number_of_room): #Room number out of range
			# 		self.msg_send("4002 Unrecognized message")
			# 		continue;

def main(argv):
	#check whether the port number is an int and in the right range
    if (argv[1].isdigit() == True):
        serverPort = int(argv[1])
        if (serverPort < 0 or serverPort > 65535):
            print("Error: The server port number is not within 0 and 65535")
            sys.exit(1)
    else:
        print("Error: The server port number is not an integer")
        sys.exit(1)
	
    #check whether the Userinfo.txt exists, I assume it's in the same folder with GameServer.py
    file = argv[2]
    if os.path.exists(file):
        sz = os.path.getsize(file)
        # check whether the database is empty
        if not sz:
            print(file, " is empty!")
        else:
            print("Successfully connect to database!")
    else:
        print("Error: \"" + argv[2] + "\" does not exist")

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind( ("", serverPort) )
    serverSocket.listen(5)
    print("The server is ready to receive  (Press control/command + C to kill the process)")
    
    #accept client and create a thread for that socket
    while True:
        client = serverSocket.accept()
        newthd = ServerThread(client, argv[2])
        newthd.start()
    
if __name__ == '__main__':
    print("Please input in this format: \n python3 GameServer.py <listening port> <path to UserInfo.txt>")
    print("example: python3 GameServer.py 1001 UserInfo.txt")
    if len(sys.argv) != 3:
        print("Error, please input arguments again!")
        sys.exit(1)
    
    main(sys.argv)