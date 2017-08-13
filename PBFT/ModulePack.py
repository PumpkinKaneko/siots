# coding:utf-8

def dict_to_msg(dict):
    msg = ""
    for key in dict.keys():
        msg += key + ":" + dict[key] + ","
    msg += "."
    return msg

def msg_to_dict(message):
    dict = {}
    m_pointer = 0
    while True:
        att = ""
        val_str = ""
        while True:
            if message[m_pointer] == ":":
                m_pointer += 1
                break
            att += message[m_pointer]
            m_pointer += 1
        while True:
            if message[m_pointer] == ",":
                m_pointer += 1
                break
            val_str += message[m_pointer]
            m_pointer += 1
        val_int = val_str
        dict[att] = val_int
        if message[m_pointer] == ".":
            break
    return dict

def input_transmission_data():
    data = {}
    data["title"] = "request"
    print ("If you want to stop, type \"end\"")
    print ("contents:", end="")
    data["contents"] = input()
    return data

def get_address(address_file):
    address_book = open(address_file, "r")
    address = address_book.readlines()
    address_book.close()
    for num in range(len(address)):
        address[num] = address[num].rstrip("\n")
    return address


def write_ledger(contents):
    openledger = open("ledger.txt", "a")
    openledger.write(contents + "\n")
    openledger.close()
