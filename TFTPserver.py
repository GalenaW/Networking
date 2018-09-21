#****************************************************************
# TFTPServer.py
# Author: Galena Wilson
# Purpose: This is the server code for a TFTP client/server application
# using TCP
# Arguments: It takes optional argument for the server port, the default is set to # 50000
#****************************************************************

from socket import *
import packets
import os
import ntpath
from helper import *
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type = int, default = 50000, help = 'Server port')
    args = parser.parse_args()
    
    serverPort = args.p
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    
    print('The server is ready to receive on port {0}'.format(args.p))
        
    while True:
        connectionSocket, addr = serverSocket.accept()
        
        req = connectionSocket.recv(1024)
        packet = Packets(connectionSocket)
    
        opcode, filename = packet.extract_request(req)
        # if a RRQ is initiated:
        if opcode == 1:
            if os.path.isfile(filename):           # If the file exists: send the data
                packet.sendData(filename) 
            else: 
                err_packet = packet.ERROR_packet(1, "File not found.") # Otherwise : send 
                connectionSocket.send(err_packet)
    
        # if a WRQ request is initiated
        if opcode == 2:
            # send acknowledgement with block number 0
            ack_pack = packet.ACK_packet((0).to_bytes(2, byteorder="big"))
            connectionSocket.send(ack_pack)
            
            packet.writeData(filename)
        
    connectionSocket.close()

main()