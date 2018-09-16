from socket import *
import argparse
import os
import sys
import pickle
import packets

parser = argparse.ArgumentParser(description= 'Enter IP address, Server request ("rd" for read and "wrt" for write.)')

#parser.add_argument('hostname', type = str, help = 'IP address of destination')
parser.add_argument('request', type = str, help = 'request to server')
parser.add_argument('filename', type = str, help = 'the file to be sent or received')
args = parser.parse_args()

#hostname = args.hostname
request = args.request
filename = args.filename


def client():    
    serverPort = 12345
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
        file = open(filename, "wb") 
        
        while True:
            pack = clientSocket.recv(516)
            if not pack:
                break
            file.write(pack[4:])
           
        file.close()    
            
        # send ACK
        # if # of blocks is not next in the row: send error
       
    if request == "wrt":   
        # To do: implement write request
        # send request
        # get ACK
        wrt_packet = packets.RD_WR_packet(request, filename)
        clientSocket.send(wrt_packet)
        
        ack = clientSocket.recv(4)
        #read data from file
        file = open(filename, 'rb')
        
        # send data package with block # 1
        file_s = os.path.getsize(filename)
        end_file = round(file_s/512)
        
        if end_file == 0:
            end_file= 1
            
        for i in range (0, end_file):
            data = file.read(512)
            pack = packets.DATA_packet(data, i)
            clientSocket.send(pack)

        file.close()

  
    
    clientSocket.close()

client()