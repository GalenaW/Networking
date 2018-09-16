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
    
def extract_request(pac):
    string = pac.decode()
    end_pos = string.index("\x00\x00", 0, len(string)-1)
    
    return int.from_bytes(pac[0:2], byteorder = "big"), pac[2:end_pos]
    
def TCPServer():
    serverPort = 12002
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
            file = open(filename, 'rb')
            
            # send data package with block # 1
            file_s = os.path.getsize(filename)
            end_file = round(file_s/512)
            
            if end_file == 0:
                end_file=1
                
            data = file.read(512)
            pack = packets.DATA_packet(data, 1)
            prevdata = data
            connectionSocket.send(pack)
            
            for i in range (2, end_file):
                data = file.read(512)
                ack = connectionSocket.recv(4)
                pack = packets.DATA_packet(data, i)
                if ack[2:] == i-1:
                    connectionSocket.send(pack)
                else:
                    connectionSocket.send(prevdata)
                
                    
            file.close()
            # TO DO:
            # wait for ACK
            # if error is sent - resend the last data package
            
        # if a WRQ request is initiated
        if opcode == 2:
            ack_pack=packets.ACK_packet((0).to_bytes(2, byteorder = "big"))
            connectionSocket.send(ack_pack)
            
            # receive data package
            file = open(filename, "wb") 
            
            while True:
                pack = connectionSocket.recv(516)
                if not pack:
                    break
                ack_pack=packets.ACK_packet(pack[2:4])
                connectionSocket.send(ack_pack)
                file.write(pack[4:])
            
            file.close()    
            
        connectionSocket.close()
    
TCPServer()