# Author: Jiang Feiyu
# UID: 3035770800
# Comp3234 Assignment1
import socket
import sys
import os
import threading
import time
import random

def thd_func(client):
    #for receiving message and handle exception
     connectionSocket, addr = client

def msg_receive(self): 
    #for sending message and handle exception
	try:
		msg = self.connSocket.recv(10000).decode('ascii') #receive client message
		return msg
	except socket.error as emsg:
		print("Thread: User \"" + self.username + "\" with IP \"" + self.connAddr[0] + "\" has disconnected unexpectedly")			
        self.connSocket.close()
		sys.exit(1)

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
        newthd = threading.Thread(target=thd_func, args=(client, argv[2]))
        newthd.start()
    
if __name__ == '__main__':
    print("Please input in this format: \n python3 GameServer.py <listening port> <path to UserInfo.txt>")
    print("example: python3 GameServer.py 1001 UserInfo.txt")
    if len(sys.argv) != 3:
        print("Error, please input arguments again!")
        sys.exit(1)
    
    main(sys.argv)