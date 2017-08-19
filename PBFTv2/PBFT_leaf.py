# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time
import json

def new_client(client, server):
    print (client["address"][0] + " contacted")
def wsserver(address):
    server = WebsocketServer(9998, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

def msg_reaction(client, server, rec_msg):
    rec_json = MP.msg_to_dict(rec_msg)
    react_func(rec_json)

def react_func(json_file):
    print(json_file["result"])

def ws_transmission(ws, json_file):
    sendmsg = MP.dict_to_msg(json_file)
    ws.send(sendmsg)

class PBFTServer(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)
        self.address = address
    def stop(self):
        self.stop_event.set()
    def run(self):
        wsserver(self.address)

if __name__ == "__main__":
    address = MP.get_address("leaf_address.txt")
    serverthread = PBFTServer(address[0])
    serverthread.start()
    time.sleep(0.1)
    print ("If you are ready, input \"ok\"")
    while True:
        ready = input()
        if ready == "ok":
            break
    request_num = 0
    ws_core = create_connection("ws://" + address[1] + ":9999/")
    while True:
        input_data = MP.input_transmission_data()
        if input_data["contents"] == "end":
            break
        else:
            N1 = MP.make_prime_num(input_data["num1"])
            N2 = MP.make_prime_num(input_data["num2"])
            keys = MP.make_keys(N1, N2, input_data["pub_low_lim"])
            print (keys)
            pri_key = keys["pri_key"]
            pub_key = keys["pub_key"]
            mod_num = keys["mod_num"]
            con = "From" + str(pub_key) + ":" + input_data["contents"]
            print (con)
            enc_con = MP.encrypt(con, pri_key, mod_num)
            tra_data = {}
            tra_data["title"] = "transaction"
            tra_data["requestID"] = address[0] + ":" + str(request_num)
            tra_data["key"] = str(pub_key)
            tra_data["mod_num"] = str(mod_num)
            tra_data["contents"] = enc_con
            ws_transmission(ws_core, tra_data)
            request_num += 1
    serverthread.stop()
