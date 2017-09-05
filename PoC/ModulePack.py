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
Write json to file
"""
def write_json(json_file):
    openjson = open("record.json", "a")
    json.dump(json_file, openjson, indent = 4)
    openjson.write("\n")
    openjson.close()

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

"""
Generate signature
"""
def gen_sig(transaction, key, mod):
    hash_transaction = int(hashlib.sha256(transaction.encode("utf-8")).hexdigest(), 16)
    signature = encrypt(hash_transaction, key, mod)
    return signature

"""
Input question
"""
def make_question(questionID, keys):
    print ("If you want to finish, input \"finish\"")
    print ("contents:", end="")
    contents = input()
    print ("deadline:", end="")
    deadline = int(input())
    signature = gen_sig(contents+questionID, keys["key"], keys["mod"])
    return {"title":"question", "questionID":questionID, "contents":contents, "signature":signature, "deadline":deadline}

"""
Calcurate each choice's weight
"""
def sum_weight(nodes, expects):
    table = {}
    for core in expects.keys():
        for leaf in expects[core].keys():
            if expects[core][leaf] in table:
                table[expects[core][leaf]] += nodes[core][leaf]["weight"]
            else:
                table[expects[core][leaf]] = nodes[core][leaf]["weight"]
    for choice in table:
        return table

"""
Calcurate new weight
"""
def cal_weight(result, expects, weight = 1.0):
    weight_table = {}
    for core in expects.keys():
        weight_table[core] = {}
        for leaf in expects[core].keys():
            weight_table[core][leaf] = 0
            if expects[core][leaf] == result:
                weight_table[core][leaf] += weight
    return weight_table
