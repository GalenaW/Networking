#****************************************************************
# 
#
#
#
#
#****************************************************************
from socket import *
import argparse
import os
import ntpath
import sys
import pickle
import packets

def to_int(binary):
    return int.from_bytes(binary, byteorder = "big")

def get_fname(file):
    head, tail = ntpath.split(file)
    return tail or ntpath.basename(head)   
    

parser = argparse.ArgumentParser(description= 'Enter IP address, Server request ("rd" for read and "wrt" for write.)')

#parser.add_argument('hostname', type = str, help = 'IP address of destination')
parser.add_argument('request', type = str, help = 'request to server')
parser.add_argument('filename', type = str, help = 'the file to be sent or received')
args = parser.parse_args()

#hostname = args.hostname
request = args.request
filename = args.filename


   
serverPort = 12000
serverName = "127.0.0.1"
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#initiate read request
    
if request == "rd":
    #To do: implement read request
    
    # send request to read
    packet = packets.RD_WR_packet(request, filename)
    clientSocket.send(packet)
    
    # receive data package
    with open(get_fname(filename), "wb") as file:
    
        while True:
            pack = clientSocket.recv(516)
            ack_pack=packets.ACK_packet(pack[2:4])
            clientSocket.send(ack_pack)
            
            if not pack:
                break
            file.write(pack[4:])
         
        file.close()
        
    # send ACK
    # if # of blocks is not next in the row: send error
    
if request == "wrt":   
    wrt_packet = packets.RD_WR_packet(request, filename)
    clientSocket.send(wrt_packet)
    
    #read data from file
    with open(filename, 'rb') as file:
    
        # send data package with block # 1
        file_s = os.path.getsize(filename)
        end_file = round(file_s/512)
        
        if end_file == 0:
            end_file= 1
        
        #ack = clientSocket.recv(4) # ack with block number 0
        ack = clientSocket.recv(4)
        if to_int(ack[0:2]) == 4:
            for i in range (1, end_file+1):             # if the previous packet is ackn
                if to_int(ack[2:]) == i-1:
                    data = file.read(512)               # read data
                    pack = packets.DATA_packet(data, i) # create data pack
                    clientSocket.send(pack)   
                ack = clientSocket.recv(4)        
        
        file.close()
        
clientSocket.close()

