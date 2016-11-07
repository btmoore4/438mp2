#File Containing Helper Functions

def synMess(seq): 
    return formatMess(seq, 0, 1, 0, "")

def synackMess(seq, ack_num): 
    return formatMess(seq, ack_num+1, 1, 0, "")

def ackMess(ack_num): 
    return formatMess(0, ack_num+1, 1, 0, "")

def finMess(ack_num): 
    return formatMess(0, ack_num, 0, 1, "")

def formatMess(seq_num, ack_num, syn, fin, data):
    message = ",".join([str(seq_num), str(ack_num), str(syn), str(fin), str(data)])
    return message

def decodeMess(mess):
    message = mess.split(',')
    for i in xrange(0,4):
        message[i] = int(message[i])
    return message



