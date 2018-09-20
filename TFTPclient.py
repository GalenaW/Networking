#****************************************************************
# TFTPClient.py
# Author: Galena Wilson
# Purpose: This is the client code for a TFTP client/server application
# using TCP
# 
#****************************************************************
from socket import *
import argparse
import os
import ntpath
from helper import Packets
from pathlib import Path
 
     
def main(): 
    parser = argparse.ArgumentParser(description = 'Source port, Destination port, Server request, Filename')
    
    parser.add_argument('host_port', type = int, help = 'Host port')
    parser.add_argument('destination_port', type = int, help = 'Destination port')
    parser.add_argument('request', type = str, help = 'Request to server ("rd" or "wrt")')
    parser.add_argument('filename', type = str, help = 'The file to be sent or received')
    args = parser.parse_args()
    
    source_port = args.host_port
    dest_port = args.destination_port
    request = args.request
    filename = args.filename
    
    
    serverPort = dest_port
    serverName = "127.0.0.1"
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    packet = Packets(source_port, dest_port, clientSocket)
    
    if request == "rd":
        # To do: implement read request
        # send request to read
 
        rd_pack = packet.RD_WR_packet(request, filename)
        dgram = packet.makeDatagram(rd_pack)
        clientSocket.send(dgram)
        
        packet.writeData(filename)
    
    #initiate a write request      
    if request == "wrt":                               
        if os.path.isfile(filename):
            wrt_packet = packet.RD_WR_packet(request, filename)
            dgram = packet.makeDatagram(wrt_packet)
            clientSocket.send(dgram)  
            ack = clientSocket.recv(12)
            packet.sendData(filename)  # read data from file and send it to server
        else:
            print("File {0} does not exist!".format(filename))
            err_packet = packet.ERROR_packet(1, "File not found.")
            dgram = packet.makeDatagram(err_packet)
            clientSocket.send(dgram)
    
    clientSocket.close()
    
main()
    
