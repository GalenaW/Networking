
def ACK_packet(blc_number):
    op_code = (4).to_bytes(2, byteorder="big")
    
    return op_code+blc_number
    
def DATA_packet(data, blck_number):
    op_code = (3).to_bytes(2, byteorder="big")
    blck = blck_number.to_bytes(2, byteorder="big")
    
    return op_code+blck+data
    
def RD_WR_packet(input, filename):

    if input == "rd":
        opcode = (1).to_bytes(2, byteorder = "big")
    else:  
        opcode = (2).to_bytes(2, byteorder = "big")
    filename = filename.encode()
    mode = ("octet").encode()
    zero = (0).to_bytes(2, byteorder = "big")
    
    return opcode+filename+zero+mode+zero

