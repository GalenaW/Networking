#****************************************************************
# helper.py
# Author: Galena Wilson
# Purpose: Helper classes for the TFTP client an server
# Preconditions: The methods of the class get called by the server/client
#****************************************************************
from socket import *
import os

class Packets:

    def __init__(self, socket):
        self.socket = socket
    '''
        Purpose: Creates an acknoledgment packet.
        Arguments: The block number for the acknowledged data packet.
    '''
    def ACK_packet(self, blc_number):
        # OP_CODE | BLCK_NUMBER
        op_code = (4).to_bytes(2, byteorder="big")

        return op_code+blc_number
    
    '''
        Purpose: Creates a data packet.
        Arguments: The block of data to be sent along with its number.
    '''    
    def DATA_packet(self, data, blck_number):
        # OP_CODE | BLCK_NUMBER | DATA
        op_code = (3).to_bytes(2, byteorder="big")
        blck = blck_number.to_bytes(2, byteorder="big")
        
        return op_code+blck+data
    '''
        Purpose: Creates Reard or Write packet.
        Arguments: The request given form the user and the filename of the file to be sent/received.
    '''
    def RD_WR_packet(self, input, filename):
        # OP_CODE | FILENAME | 0 | MODE | 0
        if input == "rd":
            opcode = (1).to_bytes(2, byteorder = "big")
        else:  
            opcode = (2).to_bytes(2, byteorder = "big")
            
        filename = filename.encode()
        mode = ("netascii").encode()
        zero = (0).to_bytes(1, byteorder = "big")
        
        return opcode+filename+zero+mode+zero
    '''
        Purpose: Creates an error packet
        Arguments: An error code and error message.
    '''
    def ERROR_packet(self, code, msg):
        # OP_CODE | ERRCODE| ERRMESSAGE | 0
        opcode = (5).to_bytes(2, byteorder = "big")
        errcode = (code).to_bytes(2, byteorder = "big")
        errmsg = msg.encode()
        zero = (0).to_bytes(1, byteorder = "big")
        
        return opcode+errcode+errmsg+zero
    
    '''
        Purpose: 
        Arguments: 
    '''
    def sendData(self, filename):
        # send data package with block # 1
        with open(filename, 'rb') as file:
            file_s = os.path.getsize(filename)
            end_file = round(file_s/512)

            if end_file == 0:
                end_file= 1
            
            for i in range (1, end_file+1):            # if the previous packet is ackn
                data = file.read(512)                  # read data
                pack = self.DATA_packet(data, i)       # create data pack
                self.socket.send(pack)   
                ack = self.socket.recv(4)
                if int.from_bytes(ack[0:2], byteorder = "big") == 5:
                    break
        print("File sent")            
        file.close()
    '''
        Purpose: 
        Arguments: 
    '''
    def writeData(self, filename):                     
        filename = "copy_" + filename
        # receive data package
        
        if os.path.isfile(filename):
            err = self.ERROR_packet(6, "File already exists!")
            print("File {0} exists.".format(filename))
            self.socket.send(err)
            self.socket.close()
        
        else:
            with open(filename, "wb") as file:
            
                while True:
                    pack = self.socket.recv(516)
                    if int.from_bytes(pack[0:2], byteorder = "big") == 5:
                        print("File {0} does not exist!".format(filename))
                        os.remove(filename)
                        break
                        
                    ack_pack=self.ACK_packet(pack[2:4])              
                    self.socket.send(ack_pack)
                    file.write(pack[4:])
                    if len(pack[4:]) < 512:
                        break
            print("File received.")
            file.close()

    '''
        Purpose: 
        Arguments: 
    '''
    def extract_request(self, pac):
        end_pos = pac[2:].find(b"\x00")        
        filename = pac[2:2+end_pos].decode()
        return int.from_bytes(pac[0:2], byteorder = "big"), filename
    '''
        Purpose: 
        Arguments: 
    '''
    def to_int(self, binary):
        return int.from_bytes(binary, byteorder="big")
    