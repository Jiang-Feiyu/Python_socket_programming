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
responses = [[],[],[],[],[],[],[],[],[],[]] #Global variable: 1D containing the response from client
result = [] #Global variable: array[number_of_room] containing the random result generated

judging_lock = threading.Lock() #mutex lock for judging who is the winner

for i in range(0, number_of_room): #initialize all the arrays
	number_of_player_in_room.append(0)
	result.append("null")
 
class ServerThread(threading.Thread):
    room_number = 0
    count = 0
     
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
        responses[room_number-1] = []
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
                    self.msg_send("1001 Authentication successful")
                    return 1
            userInfoFile.close()
            match = 1
        
        self.msg_send("1002 Authentication failed")
        print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has failed to authenticate")
        return 0
	            
    def enter(self, client_comment):
        # check if its a blank command
        if client_comment.strip() == "/enter":
            self.msg_send("4002 Unrecognized message")
            return 4002
        # check whether the room exists
        try:
            num = int(client_comment.split()[1])
            if (num < 1) or  (num > 10):
                print("NUM: ", num)
                self.msg_send("4002 Unrecognized message")
                return 4002
        except ValueError:
            self.msg_send("4002 Unrecognized message")
            return 4002
        # check whether there are people in the room player chose
        self.acquire_lock("NUM")
        self.room_number = num
        match number_of_player_in_room[num-1]:
            case 0 | 1: # this means the room is avaliable
                number_of_player_in_room[num-1] += 1
                self.release_lock("NUM")
                print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has enter room " + str(num-1))
                if  number_of_player_in_room[num-1] == 1:
                    self.msg_send("3011 Wait")
                while number_of_player_in_room[num-1] == 1: # if there is only one person in the room, he need to wait another player orn quit the room
                    try:
                        self.connSocket.send(b"")
                        time.sleep(0.1)
                    except ConnectionResetError: #player himself has disconnected
                        print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has disconnected unexpectedly while waiting for another player to enter")
                        self.connSocket.close()
                        self.clear_room(num) #one player only, safe to run
                        self.waiting = 0
                        sys.exit(1)
                self.msg_send("3012 Game started. Please guess true or false")
                return 3012
            case 2:
                print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" failed to enter room " + str(num - 1) + " because it is full")
                self.msg_send("3013 The room is full")
                self.release_lock("NUM")
                return 3013
            case _:
                self.msg_send("4002 Unrecognized message")
                return 4002
    
    def guess(self, client_commend,room_number,player_name):
        # handle the situation whith wrong command
        # check if its a blank command
        if client_commend.strip() == "/guess":
            self.msg_send("4002 Unrecognized message")
            return 4002
        # check if its a boolean value
        try:
            guess = client_commend.split()[1]
            if guess == "true":
                guess = True
            elif guess == "false":
                guess = False
            else:
                self.msg_send("4002 Unrecognized message")
                return 4002
        except ValueError:
            self.msg_send("4002 Unrecognized message")
            return 4002
        
        responses[room_number-1].append([player_name, guess])
        
        first_player = ''
        if len(responses[room_number-1]) == 1:
            first_player = player_name
        print("first_player1", first_player)
        
        while len(responses[room_number-1]) == 1: # if there is only one person in the room, he need to wait another player orn quit the room
            try:
                self.connSocket.send(b"")
                time.sleep(0.1)
            except ConnectionResetError: #player himself has disconnected
                self.connSocket.close()
                self.waiting = 0
                sys.exit(1)
        
        # Playing the game
        self.acquire_lock("RES")
        win = bool(random.getrandbits(1)) #generate result
        if win == 1:
            win = True
        else:
            win = False
        self.release_lock("RES")
        
        print("responses[room_number-1]",responses[room_number-1])
        print("win",win)
        # self.acquire_lock("JUD")
        print("responses[room_number-1][0][1]: ",responses[room_number-1][0][1])
        print("responses[room_number-1][1][1]: ",responses[room_number-1][1][1])
        if responses[room_number-1][0][1] == responses[room_number-1][1][1]:
            # self.clear_room(room_number) #safe to run coz one thread only
            print("3023 The result is a tie")
            self.msg_send("3023 The result is a tie")
        else:
            if responses[room_number-1][0][0] == player_name:
                if responses[room_number-1][0][1] == win:
                    self.msg_send("3021 You are the winner")
                else:
                    self.msg_send("3022 You lost this game")
            else:
                if responses[room_number-1][1][1] == win:
                    self.msg_send("3021 You are the winner")
                else:
                    self.msg_send("3022 You lost this game")
                    
        if player_name == first_player:
            self.clear_room(room_number) 
        # self.release_lock("JUD")   
        
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
            client_command = self.msg_receive() # recieve the command from client
            print(client_command)
            try:
                command = client_command.split()[0]
            except ValueError:
                self.msg_send("4002 Unrecognized message")
                sys.exit(1)
            match command:
                # 2-1 list command
                case "/list":
                    self.acquire_lock("NUM")
                    #Assemble the message
                    message = "3001 " + str(number_of_room)
                    for i in number_of_player_in_room:
                        message = message + " " + str(i)
                    self.msg_send(message)
                    self.release_lock("NUM")
                # 2-2 enter the game hall
                case "/enter":
                    client_state = self.enter(client_command)
                # 3 play the game
                case "/guess":
                    client_state = self.guess(client_command, self.room_number,self.username)
                # 4 Exit from the System
                case "/exit":
                    client_state = 4001
                    self.msg_send("4001 Bye bye")
                    print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has disconnected")
                    self.connSocket.close()
                # 5 incorrect message format
                case _:
                    self.msg_send("4002 Unrecognized message")

# main function:
print("Please input in this format: \n python3 GameServer.py <listening port> <path to UserInfo.txt>")
print("example: python3 GameServer.py 1001 UserInfo.txt")
if len(sys.argv) != 3:
    print("Error, please input arguments again!")
    sys.exit(1)
    
#check whether the port number is an int and in the right range
if (sys.argv[1].isdigit() == True):
    serverPort = int(sys.argv[1])
    if (serverPort < 0 or serverPort > 65535):
        print("Error: The server port number is not within 0 and 65535")
        sys.exit(1)
else:
    print("Error: The server port number is not an integer")
    sys.exit(1)
	
#check whether the Userinfo.txt exists, I assume it's in the same folder with GameServer.py
file = sys.argv[2]
if os.path.exists(file):
    sz = os.path.getsize(file)
    # check whether the database is empty
    if not sz:
        print(file, " is empty!")
    else:
        print("Successfully connect to database!")
else:
    print("Error: \"" + sys.argv[2] + "\" does not exist")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind( ("", serverPort) )
serverSocket.listen(5)
print("The server is ready to receive  (Press control/command + C to kill the process)")
    
#accept client and create a thread for that socket
while True:
    client = serverSocket.accept()
    newthd = ServerThread(client, sys.argv[2])
    newthd.start()