
# Simple Network Application

## Application overview
### Tracker
A centralized tracker keeps
- track of which peers are connected and storing what files
- history version of every file of all peers
### Peer
- Through tracker protocol, a peer informs the tracker as to what files and their encoded data are contained in its local repository.
- When a peer requires a file that does not belong to its repository, a request is sent to the tracker. The tracker sends a response to that peer which other peers keep the required file. Then the peer can directly connect to another peer to get the data of the file.
- Multiple peers could be downloading different files from a target peer at a given point in time.
- A peer can check the history of each file and can reset a file to a specific version.

## How to use
The Tracker and Peer has different GUI, each GUI has many buttons. 

If user wants to do a task, fill in the corresponding information entry (if needed) and then press a button.
### Tracker 
- **help**: List the buttons of Tracker 
- **list**: List all peer with files
- **update**: Update files in local repository of all peers
- **quit**: Shut down tracker socket, use this command before closing the terminal
### Peer
- **help**: List the buttons of Peer 
- **list**: List all peers in the application
- **publish** - Send information of all files to tracker
- **fetch** *fname* - Send a fetch request to tracker to fetch file with name at fname
- **history** *fname* - Get all the history version of a file
- **reset** *fname version* - Get the data of a file in a specific version
- **block/unblock** *peer* - Block/Unblock a peer
- **quit** - Shut down peer socket.

## Command
Using python3.9
### Tracker 
1. cd tracker
2. python3.9 tracker.py
### Peer
1. cd peer1 (or peer2, peer3)
2. python3.9 peer.py


