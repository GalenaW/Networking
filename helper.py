from socket import *
import os

class Packets:
    
    def __init__(self, srcPort, destPort, socket):
        self.srcPort = srcPort
        self.destPort = destPort
        self.socket = socket
    
    def ACK_packet(self, blc_number):
        # OP_CODE | BLCK_NUMBER
        op_code = (4).to_bytes(2, byteorder="big")
        
        return op_code+blc_number
        
    def DATA_packet(self, data, blck_number):
        # OP_CODE | BLCK_NUMBER | DATA
        op_code = (3).to_bytes(2, byteorder="big")
        blck = blck_number.to_bytes(2, byteorder="big")
        
        return op_code+blck+data
        
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
    
    def ERROR_packet(self, code, msg):
        # OP_CODE | ERRCODE| ERRMESSAGE | 0
        opcode = (5).to_bytes(2, byteorder = "big")
        errcode = (code).to_bytes(2, byteorder = "big")
        errmsg = msg.encode()
        zero = (0).to_bytes(1, byteorder = "big")
        
        return opcode+errcode+errmsg+zero
    
    
    def makeDatagram(self, packet):
        # source port | Destination Port | Length | CheckSUM | 
        source_port = (self.srcPort).to_bytes(2, byteorder="big")
        dest_port = (self.destPort).to_bytes(2, byteorder="big")
        chkSum = (0).to_bytes(2, byteorder="big")
        length = len(packet) + 8
    
        return source_port + dest_port + chkSum + length.to_bytes(2, byteorder = "big") + packet
        
    
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
                dgram = self.makeDatagram(pack)
                self.socket.send(dgram)   
                ack = self.socket.recv(12)
                if int.from_bytes(ack[8:10], byteorder = "big") == 5:
                    break
        file.close()
    
    def writeData(self, filename):
        filename = "copy_" + filename
        # receive data package
        
        if os.path.isfile(filename):
            err = self.ERROR_packet(6, "File already exists!")
            print("File {0} exists.".format(filename))
            dgram = self.makeDatagram(err)
            self.socket.send(dgram)
            self.socket.close()
        
        else:
            with open(filename, "wb") as file:
            
                while True:
                    pack = self.socket.recv(524)
                    if int.from_bytes(pack[8:10], byteorder = "big") == 5:
                        print("File {0} does not exist!".format(filename))
                        os.remove(filename)
                        break
                        
                    ack_pack=self.ACK_packet(pack[10:12])
                    dgram = self.makeDatagram(ack_pack)                
                    self.socket.send(dgram)
                    file.write(pack[12:])
                    if len(pack[12:]) < 512:
                        break
                
            file.close()

class Utility: 
    
    def __init__(self):
        self

    def extract_request(self, pac):
        end_pos = pac[10:].find(b"\x00")
        filename = pac[10:10+end_pos].decode()
        return int.from_bytes(pac[8:10], byteorder = "big"), filename
        
    def to_int(self, binary):
        return int.from_bytes(binary, byteorder="big")
    