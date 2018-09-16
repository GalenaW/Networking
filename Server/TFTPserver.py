#****************************************************************
# 
#
#
#
#
#****************************************************************
from socket import *
import packets
import os
import ntpath
    
def extract_request(pac):
    string = pac.decode()
    end_pos = string.index("\x00\x00", 0, len(string)-1)
    
    return int.from_bytes(pac[0:2], byteorder = "big"), pac[2:end_pos]
    
def to_int(binary):
    return int.from_bytes(binary, byteorder = "big")
    
def get_fname(file):
    head, tail = ntpath.split(file)
    return tail or ntpath.basename(head)   
    
serverPort = 12000
serverSocket =  socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready do receive on port 12000')

    
while True:
    connectionSocket, addr = serverSocket.accept()
    packet = connectionSocket.recv(1024)
    opcode, filename = extract_request(packet)
    
    
    #if a RRQ is initiated:
    if opcode == 1:
        #read data from file
        
        with open(filename, 'rb') as file:
        
            # send data package with block # 1
            file_s = os.path.getsize(filename)
            end_file = round(file_s/512)
            
            if end_file == 0:
                end_file = 1
            
            data = file.read(512)               # read data
            pack = packets.DATA_packet(data, 1) # create data pack
            connectionSocket.send(pack)   
            ack = connectionSocket.recv(4) 
            
            for i in range (2, end_file+1):             # if the previous packet is ackn
                if to_int(ack[2:]) == i-1:
                    data = file.read(512)               # read data
                    pack = packets.DATA_packet(data, i) # create data pack
                    connectionSocket.send(pack)   
                ack = connectionSocket.recv(4)  
            file.close()
                    
        # TO DO:
        # if error is sent - resend the last data package?
        
    # if a WRQ request is initiated
    if opcode == 2:
        #send acknowledgement with block number 0
        ack_pack=packets.ACK_packet((0).to_bytes(2, byteorder = "big"))
        connectionSocket.send(ack_pack)
        # receive data package
        with open(get_fname(filename), "wb") as file:
            while True:
                pack = connectionSocket.recv(516)
                ack_pack=packets.ACK_packet(pack[2:4])
                connectionSocket.send(ack_pack)
                if not pack:
                    break
                file.write(pack[4:])
            
                
        file.close()
        
    connectionSocket.close()
