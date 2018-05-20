# PyPaint

An application that enables collaborative drawing over a network.  It 
currently supports only a direct connection between two clients.  

## To Run 

Tested on Python version 3.6, but it should work on any recent version of 
Python 3.  

To start the application, run `python main.py` from the command line.  This 
will bring up the paint window without a peer connection.  

To host a peer connection, run `python main.py 1 <port-num>` where port-num 
is the desired hosting port.  

To connect to a hosting peer, run `python main.py 0 <port-num> <ip-address>` 
where the port and ip are the hosts' information.  

Example for running two clients locally on the same computer(need to be run 
in separate shell instances, or as background processes):  
host - `python main.py 1 50001`  
peer - `python main.py 0 50001 localhost`  
