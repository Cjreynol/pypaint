# PyPaint

An application that enables collaborative drawing over a network.  It only 
supports a peer-to-peer connection between two clients.

## To Run 

Tested on Python version 3.6, but it should work on any recent version of 
Python 3.  

To start the application, run `python main.py` from the command line.  
This will bring up the setup window where you can enter an IP address and port 
number.  Only the port number is required for "Host", both IP and port are 
needed for "Connect", and neither is required for "Offline".  

### Example Running Two Clients Locally

![Host setup](https://user-images.githubusercontent.com/4585721/40438151-f110c910-5e7c-11e8-8c9f-a745b9474794.png "Host setup")  
Pick a port for the host, and hit the "Host" button.  
![Waiting for connection](https://user-images.githubusercontent.com/4585721/40438153-f1289c34-5e7c-11e8-8576-3df815538666.png "Waiting for connection")  
The GUI will visually hang with the button pressed down, but it is waiting 
for a connection in the background.  
![Peer connection](https://user-images.githubusercontent.com/4585721/40438154-f13ca314-5e7c-11e8-9c8c-e22004d10423.png "Peer connection")  
Enter the host port and their ip address then hit the "Connect" button.  
![Paint window](https://user-images.githubusercontent.com/4585721/40438155-f14ef74e-5e7c-11e8-916f-a8e169051f45.png "Paint window")  
Then both setup windows will become paint windows, and drawing in one will be mirrored in the others.  


### Known Bug

On Windows, Tkinter has a bug in its circle drawing that leaves artifacts on 
the canvas when the mouse motion event is moving left.  This persists even 
when the canvas is cleared but does clear when dragging another shape over 
the area.
