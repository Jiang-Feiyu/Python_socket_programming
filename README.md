# Project Description
In this assignment, you will implement a simple game house application using Python socket programming. A game house is an application in which multiple clients connect to a game server, get authorized, and then select a game room to enter and play a game with another player in the same room.</br></br>
The game house application consists of two parts: the server program and the client program. The server program should always be running and use a welcome socket to wait for connection requests from clients. The client programs establish TCP connections with the server program. After a connection is set up, the client needs to send its user name and password to the server, and can enter the game hall after successful authentication. An authenticated user is able to query the status of the game rooms, and then pick a room to enter. To start a game, there should be exactly two players in the same room. Therefore, if the entering player is the first one in the room, the player has to wait; otherwise, the game starts. After the game has started, the server generates a random boolean value and each player is invited to guess the boolean value; the player who guesses the same as the randomly generated value is the winner, and the game results in a tie if the two players’ guesses are the same. After notifying both players the game result, the game is over and both players return to the game hall. A user may leave the system when the user is in the game hall.

# How to start this project
- A sample username and password database is stored in UserInfo.txt.
  </br> Start statement (sample).
  </br> Server: python3 GameServer.py 1001 UserInfo.txt
  </br> Client: python3 GameClient.py localhost 1001

- Thread control:
  </br> Number of people per room
  </br> Guess value per player

- Overall idea
  </br> Establishing a socket connection
  </br> Disassembling by command headers
  </br> Class encapsulation
  </br> Waiting until synchronization for multi-player games

# Summary of States
<img width="454" alt="螢幕截圖 2023-07-26 下午4 27 49" src="https://github.com/Jiang-Feiyu/Python_socket_programming/assets/78698927/1e9b7dfa-f42a-40f6-a730-5d32d64358d8">

# Notes for ref
1. https://docs.python.org/3.8/library/traceback.html: useful for printing out stack trace for debugging purpose.
2. A state variable remembering which state each client is in, in the server thread handling this client’s connection
3. Creating a room member list including players in different game rooms. Multiple server threads may try to access the room member list when processing commands /list, /enter, /guess, and when adding and removing players to and from the list. Python threading lock class useful: https://docs.python.org/3.8/library/threading.html#threading.Lock.
