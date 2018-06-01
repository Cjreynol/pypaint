# PyPaint

An application that enables collaborative drawing between two peers over a 
network.

## To Run 

Tested on Python version 3.6, but it should work on any recent version of 
Python 3.  

To start the application, run `python main.py` from the command line.  
This will bring up the setup window where you can enter an IP address and port 
number.  Only the port number is required for "Host", both IP and port are 
needed for "Connect", and neither is required for "Offline".  

### Example Running Two Clients Locally

![Host setup](https://user-images.githubusercontent.com/4585721/40455655-9e9560b0-5eb3-11e8-890c-a7e8bebfb090.png "Host setup")  
Pick a port for the host, and hit the "Host" button.  

![Waiting for connection](https://user-images.githubusercontent.com/4585721/40455656-9ea91dda-5eb3-11e8-99f2-60d55947fa18.png "Waiting for connection")  
The GUI will visually hang with the button pressed down, but it is waiting 
for a connection in the background.  

![Peer connection](https://user-images.githubusercontent.com/4585721/40455657-9ebd89f0-5eb3-11e8-9d9a-59d0cb5a2af6.png "Peer connection")  
Enter the host port and ip address in the other client then hit the "Connect" button.  

![Paint window](https://user-images.githubusercontent.com/4585721/40455658-9ecc88b0-5eb3-11e8-8d44-7a06b71e38d7.png "Paint window")  
Both setup windows will become paint windows, and drawings in one client will show in the other.


### Known Bug

On Windows, Tkinter has a bug in its circle drawing that leaves artifacts on 
the canvas when the mouse motion event is moving left.  This persists even 
when the canvas is cleared, but dragging over it(like with an oval or rect) 
does remove them from the canvas.
