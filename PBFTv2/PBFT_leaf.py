# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time
import hashlib

"""
Called when core node contact
"""
def new_client(client, server):
    print (client["address"][0] + " contacted")

"""
Define websocket server
"""
def wsserver(address):
    server = WebsocketServer(9998, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

"""
Called when server receive message
"""
def msg_reaction(client, server, rec_msg):
    rec_json = MP.str_to_dic(rec_msg)
    react_func(rec_json)

"""
Define reaction to message
"""
def react_func(json_file):
    print(json_file["result"])

"""
Send json file to opponent
"""
def ws_transmission(ws, json_file):
    sendmsg = MP.dic_to_str(json_file)
    ws.send(sendmsg)

"""
Run server on sub thread
"""
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
        print ("input transaction data.")
        print ("input \"end\" if you finish")
        input_data = input()
        if input_data == "end":
            break
        else:
            keys = MP.make_keys()
            hash_tra = hashlib.sha256(input_data.encode("utf-8")).hexdigest()
            enc_hash = MP.encrypt(int(hash_tra, 16), keys["key"], keys["mod"])
            tra_data = {}
            tra_data["title"] = "transaction"
            tra_data["requestID"] = address[0] + ":" + str(request_num)
            tra_data["mod"] = keys["mod"]
            tra_data["contents"] = input_data
            tra_data["signature"] = enc_hash
            ws_transmission(ws_core, tra_data)
            request_num += 1
    serverthread.stop()
