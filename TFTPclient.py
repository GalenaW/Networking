#****************************************************************
# TFTPClient.py
# Author: Galena Wilson
# Purpose: This is the client code for a TFTP client/server application
# using TCP 
# Arguments: The arguments taken by the script are optional: one int for the 
# destination port, one string for the server name, one int with the request 
# to the server, and one string with the filename for the file to be 
# sent/received.
#****************************************************************
from socket import *
import argparse
import os
import ntpath
from helper import Packets
from pathlib import Path
 
     
def main(): 
    parser = argparse.ArgumentParser()
     
    parser.add_argument('-dp', type = int, default = 50000, help = 'Destination port')
    parser.add_argument('-srv', type = str, default = "127.0.0.1", help = 'Server Address')
    parser.add_argument('-wrt', action = "store_true", help = "Send file to server")
    parser.add_argument('-rd', action = "store_true", help = "Read from server")
    parser.add_argument('-fn', type = str, default = "unknown", help = "Filename")
    
    args = parser.parse_args()
    
    
    serverPort = args.dp
    serverName = args.srv
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    filename = args.fn
    packet = Packets(clientSocket)

    if args.rd == True:
        # Initiate RRQ
        rd_pack = packet.RD_WR_packet("rd", filename) # Create request packet
        clientSocket.send(rd_pack)                         # Send the packet
        
        packet.writeData(filename)                       # Write the data
    
    #initiate WRQ
    if args.wrt == True: 
        if os.path.isfile(filename):
            wrt_packet = packet.RD_WR_packet("wrt", filename) # Create request packet
            clientSocket.send(wrt_packet)                            # Send the packet
            ack = clientSocket.recv(4)                         # Get ACK
            packet.sendData(filename)  # read data from file and send it to server
        else:
            print("File {0} does not exist!".format(filename))   # Check if the file to be read exists
            err_packet = packet.ERROR_packet(1, "File not found.")
            clientSocket.send(err_packet)
    
        clientSocket.close()
    
main()
    
