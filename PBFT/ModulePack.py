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
    print ("If you want to stop, type \"end\"")
    print ("contents:", end="")
    data["contents"] = input()
    if data["contents"] == "end":
        return data
    print ("type random 2 numbers")
    data["num1"] = int(input())
    data["num2"] = int(input())
    print ("type low_limit of pub_key")
    data["pub_low_lim"] = int(input())
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

def cer_add(text, key, mod_num):
    decrypted_text = decrypt(text, key, mod_num)
    if decrypted_text.startswith("From" + str(key) + ":"):
        return True
    else:
        return False

def encrypt(text, key, mod_num):
    text_int = []
    for char in text:
        text_int.append(ord(char))
    enc_text_int = []
    for num in text_int:
        enc_text_int.append(pow(num, key, mod_num))
    enc_text_int_str = []
    for enc_num in enc_text_int:
        enc_text_int_str.append(str(enc_num))
    enc_text = " ".join(enc_text_int_str)
    return enc_text

def decrypt(text, key, mod_num):
    text_int_str = text.split(" ")
    text_int = []
    for num_str in text_int_str:
        text_int.append(int(num_str))
    dec_text_int = []
    for num in text_int:
        dec_text_int.append(pow(num, key, mod_num))
    dec_text_list = []
    for dec_num in dec_text_int:
        dec_text_list.append(chr(dec_num))
    dec_text = "".join(dec_text_list)
    return dec_text

def make_keys(p, q, pub_low_lim):
    from math import gcd
    mod_num = p * q
    L = ((p - 1) * (q - 1)) // gcd(p - 1, q - 1)
    for i in range(2, L):
        if gcd(i, L) == 1 and i >= pub_low_lim:
            pub_key = i
            break
    for i in range(2, L):
        if (pub_key * i) % L == 1:
            pri_key = i
            break
    return {"pri_key":pri_key, "pub_key":pub_key, "mod_num":mod_num}

def make_prime_num(low_lim):
    if low_lim == 2:
        return 2
    import math
    p = low_lim
    if (p % 2) == 0:
        p += 1
    while True:
        s = 1
        q = int(math.sqrt(p))
        for r in range(3, q + 1):
            if (p % r) == 0:
                s = 0
                break
        if s == 1:
            break
        p += 2
    return p
