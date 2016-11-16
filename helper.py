#File Containing Helper Functions
DELIMITER = ";+"

def synMess(seq): 
    return formatMess(seq, 0, 1, 0, 0,"")

def synackMess(seq, ack_num): 
    return formatMess(seq, ack_num+1, 1, 0, 0,"")

def ackMess(ack_num): 
    return formatMess(0, ack_num+1, 1, 0, 0,"")

def finMess(seq_num): 
    return formatMess(seq_num, 0, 0, 1, 0,"")

def dataMess(data, seq): 
    return formatMess(seq, 0, 0, 0, len(data), data)

def ackDataMess(seq_num, ack_num): 
    return formatMess(seq_num, ack_num, 0, 0, 0, "")

def formatMess(seq_num, ack_num, syn, fin, len_data, data):
    message = DELIMITER.join([str(seq_num), str(ack_num), str(syn), str(fin), str(len_data), str(data)])
    return message

def decodeMess(mess):
    message = mess.split(DELIMITER)
    for i in xrange(0,5):
        message[i] = int(message[i])
    return message

