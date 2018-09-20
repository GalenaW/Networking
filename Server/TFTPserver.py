#****************************************************************
# TFTPServer.py
# Author: Galena Wilson
# Purpose:
#
#****************************************************************

from socket import *
import packets
import os
import ntpath

def extract_request(pac):
    end_pos = pac[10:].find(b"\x00")
    filename = pac[10:10+end_pos].decode()
    return int.from_bytes(pac[8:10], byteorder = "big"), filename


def to_int(binary):
    return int.from_bytes(binary, byteorder="big")


def get_fname(file):
    head, tail = ntpath.split(file)
    return tail or ntpath.basename(head)


serverPort = 12018
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print('The server is ready do receive.')

while True:
    connectionSocket, addr = serverSocket.accept()
    packet = connectionSocket.recv(1024)
   
    opcode, filename = extract_request(packet)
    # if a RRQ is initiated:
    if opcode == 1:
        # read data from file

        with open(filename, 'rb') as file:

            # send data package with block # 1
            file_s = os.path.getsize(filename)
            end_file = round(file_s / 512)
            
            # in case of a small file:
            if end_file == 0:
                end_file = 1
        
            for i in range(1, end_file + 1):            # if the previous packet is ackn
                data = file.read(512)                   # read data
                pack = packets.DATA_packet(data, i)     # create data pack
                dgram = packets.datagramHeader(12001, 12000, pack)
                connectionSocket.send(dgram)
                ack = connectionSocket.recv(12)
                
            file.close()

        # TO DO:

    # if a WRQ request is initiated
    if opcode == 2:
        # send acknowledgement with block number 0
        ack_pack = packets.ACK_packet((0).to_bytes(2, byteorder="big"))
        dgram = packets.datagramHeader(12000, 12001, ack_pack)
        
        connectionSocket.send(dgram)
        # receive data package
        filename = "copy_" + filename 
        with open(get_fname(filename), "wb") as file:
            while True:
                pack = connectionSocket.recv(524)
                ack_pack = packets.ACK_packet(pack[10:12])
                dgram = packets.datagramHeader(12000, 12001, ack_pack)                
                connectionSocket.send(dgram)
                file.write(pack[12:])
                if len(pack[12:])<512:
                    break
                
                

        file.close()

    connectionSocket.close()
