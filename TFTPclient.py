#****************************************************************
# TFTPClient.py
# Author: Galena Wilson
# Purpose:
#****************************************************************
from socket import *
import argparse
import os
import ntpath
import packets
from pathlib import Path

def to_int(binary):
    return int.from_bytes(binary, byteorder = "big")

def get_fname(file):
    head, tail = ntpath.split(file)
    return tail or ntpath.basename(head)   
        

parser = argparse.ArgumentParser(description = 'Enter IP address, Server request ("rd" for read and "wrt" for write.)')

parser.add_argument('host port', type = str, help = 'IP address of destination')
parser.add_argument('destination port', type = str, help = 'IP address of destination')
parser.add_argument('request', type = str, help = 'request to server')
parser.add_argument('filename', type = str, help = 'the file to be sent or received')
args = parser.parse_args()

#hostname = args.hostname
request = args.request
filename = args.filename

   
serverPort = 12018
serverName = "127.0.0.1"
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#initiate read request
   
if request == "rd":
    #To do: implement read request
    
    # send request to read
    rd_packet = packets.RD_WR_packet(request, filename)
    dgram = packets.datagramHeader(12001, 12000, rd_packet)
    clientSocket.send(dgram)
    filename = "copy_" + filename
    # receive data package
    
    with open(get_fname(filename), "wb") as file:
    
        while True:
            pack = clientSocket.recv(524)
            ack_pack=packets.ACK_packet(pack[10:12])
            dgram = packets.datagramHeader(12000, 12001, ack_pack)                
            clientSocket.send(dgram)
            file.write(pack[12:])
            if len(pack[12:]) < 512:
                break
           
        file.close()
        
        
    print("File received.")    
    # send ACK
    # if # of blocks is not next in the row: send error
    
if request == "wrt":   
    
    wrt_packet = packets.RD_WR_packet(request, filename)
    dgram = packets.datagramHeader(12001, 12000, wrt_packet)
    clientSocket.send(dgram)
    
    #read data from file
    #if filename.exit
    with open(filename, 'rb') as file:
        
        # send data package with block # 1
        file_s = os.path.getsize(filename)
        end_file = round(file_s/512)
        print(end_file)
        
        if end_file == 0:
            end_file= 1
        
        #ack = clientSocket.recv(4) # ack with block number 0
        ack = clientSocket.recv(12)
        if to_int(ack[8:10]) == 4:
            for i in range (1, end_file+1):             # if the previous packet is ackn
                if to_int(ack[10:]) == i-1:
                    data = file.read(512)               # read data
                    pack = packets.DATA_packet(data, i) # create data pack
                    dgram = packets.datagramHeader(12001, 12000, pack)
                    clientSocket.send(dgram)   
                ack = clientSocket.recv(12)        
        print("File sent.")
        file.close()
        
clientSocket.close()

