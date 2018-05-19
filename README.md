# PyPaint

An application that enables collaborative drawing over a network.  It 
currently supports only a direct connection between two clients.  

## To Run 

Tested on Python version 3.6, but it should work on any recent version of 
Python 3.  

To start the application, run `python main.py` from the command line with the 
appropriate arguments.  See the `main.py` script for details.  This will not 
be a command-line interface in the future once the design has settled.  

Example for running two clients locally on the same computer(need to be run 
in separate shell instances, or in the background):  
host - `python main.py True 50001`  
peer - `python main.py '' 50001 localhost`
