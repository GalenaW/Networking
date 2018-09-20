#****************************************************************
# TFTPServer.py
# Author: Galena Wilson
# Purpose: This is the server code for a TFTP client/server application
# using TCP
# 
#****************************************************************

from socket import *
import packets
import os
import ntpath
from helper import *
import argparse


def main():
    parser = argparse.ArgumentParser(description = 'Server Port')
    parser.add_argument('server_port', type = int, help = 'server port')
    args = parser.parse_args()
    
    
    serverPort = args.server_port
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    
    print('The server is ready to receive.')
    
    help = Utility()
    
    while True:
        connectionSocket, addr = serverSocket.accept()
        
        req = connectionSocket.recv(1024)
        source = help.to_int(req[0:2])
        dest = help.to_int(req[2:4])
        packet = Packets(source, dest, connectionSocket)
    
        opcode, filename = help.extract_request(req)
        # if a RRQ is initiated:
        if opcode == 1:
            if os.path.isfile(filename):
                packet.sendData(filename)
            else: 
                err_packet = packet.ERROR_packet(1, "File not found.")
                dgram = packet.makeDatagram(err_packet)
                connectionSocket.send(dgram)
    
        # if a WRQ request is initiated
        if opcode == 2:
            # send acknowledgement with block number 0
            
            ack_pack = packet.ACK_packet((0).to_bytes(2, byteorder="big"))
            dgram = packet.makeDatagram(ack_pack)
            connectionSocket.send(dgram)
            
            packet.writeData(filename)
            
        connectionSocket.close()


main()