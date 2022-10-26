# Author: Jiang Feiyu
# UID: 3035770800
# Comp3234 Assignment1

#!/usr/bin/python3
import socket
import sys

def msg_send(connSocket, msg):
	try:
		connSocket.send(msg.encode('ascii'))
	except socket.error as emsg:
		print("Server has disconnected unexpectedly")
		connSocket.close()
		sys.exit(1)
	
def msg_receive(connSocket):
	try:
		msg = connSocket.recv(10000).decode('ascii') #receive client authentication info
		return msg
	except socket.error as emsg:
		print("Server has disconnected unexpectedly")
		connSocket.close()
		sys.exit(1)
  
def authentication(connSocket):
    # Get input for username and password
    name = input("Please input your user name:")
    password = input("Please input your password:")
    msg_send(connSocket, "/login " + name + " " + password)
    status = msg_receive(connSocket)
    if status == "1001 Authentication successful":
        return True
    else:
        return False
    
def main(argv):
    #firstly need to check the input  
	#server port not an integer
    login_status = 0
    
    try:
        serverPort = int(argv[2])
    except:
        print("The port number is not an integer")
        sys.exit(1)
    #Try connecting to the server
    try:
        my_socket = socket.socket()
        my_socket.connect((argv[1], int(argv[2])))
    except:
        print("Sever is offline")
        my_socket.close()
        sys.exit(1)
        
    # Get input for username and password
    while login_status == 0:
        status = authentication(my_socket)
        if status == True:
            print("1001 Authentication successful")
            login_status = 1
        else:
            print("1002 Authentication failed")
            
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Input Wrong! \n Input format: python GameClient.py <hostname/IP adress of the server> <Server port>\n Eg:Python3 GameClient.py localhost 22222")
		sys.exit(1)
	main(sys.argv)