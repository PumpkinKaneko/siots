# coding:utf-8

from Crypto.PublicKey import RSA
from Crypto.Util import randpool
import hashlib
import json

"""
Change dictionary to string
"""
def dic_to_str(dic):
    text = json.dumps(dic)
    return text

"""
Change string to dictionary
"""
def str_to_dic(string):
    dic = json.loads(string)
    return dic


"""
Get address from textfile
"""
def get_address(address_file):
    address_book = open(address_file, "r")
    address = address_book.readlines()
    address_book.close()
    for num in range(len(address)):
        address[num] = address[num].rstrip("\n")
    return address

"""
Write text to file
"""
def write_ledger(contents):
    openledger = open("ledger.txt", "a")
    openledger.write(contents + "\n")
    openledger.close()

"""
Check signature to judgement whether transaction have been rewritten
"""
def cer_add(tra, sig, mod):

    dec_sig = hex(decrypt(sig, mod))
    hash_tra = "0x" + hashlib.sha256(tra.encode("utf-8")).hexdigest()
    if dec_sig == hash_tra:
        return True
    else:
        return False

"""
RSA-encrypt with key and modulo number
"""
def encrypt(num, key, mod):
    enc_num = pow(num, key, mod)
    return enc_num

"""
RSA-decrypt with modulo number
"""
def decrypt(num, mod):
    dec_num = pow(num, 65537, mod)
    return dec_num

"""
Make RSA-keys
"""
def make_keys():
    pool = randpool.RandomPool()
    rsa = RSA.generate(1024, pool.get_bytes)
    keys = {"key":rsa.d, "mod":rsa.n}
    return keys
