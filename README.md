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

### Known Bug

On Windows, Tkinter has a bug in its circle drawing that leaves artifacts on 
the canvas when the mouse motion event is moving left.  This persists even 
when the canvas is cleared but does clear when dragging another shape over 
the area.
