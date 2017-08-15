# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time
import json

def new_client(client, server):
    print (client["address"][0] + " joined")
def wsserver(address):
    server = WebsocketServer(9999, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

def msg_reaction(client, server, rec_msg):
    rec_json = MP.msg_to_dict(rec_msg)
    react_func(rec_json)

def react_func(json_file):
    requestID = json_file["requestID"]
    title = json_file["title"]
    if json_file["title"] == "wrote" and requestID in wait_tra:
        wait_tra[requestID] += 1
    if title == "request":
        contents = json_file["contents"]
        key = int(json_file["key"])
        mod_num = int(json_file["mod_num"])
        dec_con = MP.decrypt(contents, key, mod_num)
        request_data[requestID] = {"num_per":1, "num_den":0, "contents":dec_con}
        time.sleep(0.1)
        if MP.cer_add(contents, key, mod_num):
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"permited"})
        else:
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"denied"})
    if json_file["title"] == "react" and requestID in request_data:
        if json_file["permission"] == "permited":
            request_data[requestID]["num_per"] += 1
            if request_data[requestID]["num_per"] >= int(len(ws_list) * per_rate):
                MP.write_ledger(request_data[requestID]["contents"])
                ws_broadcast(ws_list, {"title":"wrote","requestID":requestID})
                del(request_data[requestID])
        if json_file["permission"] == "denied":
            request_data[requestID]["num_den"] += 1
            if request_data[requestID]["num_den"] >= int(len(ws_list) * (1 - per_rate)):
                del(request_data[requestID])


def ws_connect(address):
    ws_connect_list = []
    for num_add in range(len(address) - 1):
        ws_connect_list.append(create_connection("ws://" + address[num_add + 1] + ":9999/"))
    return ws_connect_list

def ws_transmission(ws, json_file):
    sendmsg = MP.dict_to_msg(json_file)
    ws.send(sendmsg)

def ws_broadcast(ws_list, json_file):
    for num_add in range(len(ws_list)):
        ws_transmission(ws_list[num_add - 1], json_file)

class ChatServer(threading.Thread):
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
    address = MP.get_address("address.txt")
    serverthread = ChatServer(address[0])
    serverthread.start()
    request_data = {}
    wait_tra = {}
    per_rate = 2/3
    wrote_rate = 2/3
    time.sleep(0.1)
    print ("If you are ready, input \"ok\"")
    while True:
        ready = input()
        if ready == "ok":
            break
    ws_list = ws_connect(address)
    request_num = 0
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
            tra_data["title"] = "request"
            tra_data["requestID"] = address[0] + ":" + str(request_num)
            tra_data["key"] = str(pub_key)
            tra_data["mod_num"] = str(mod_num)
            tra_data["contents"] = enc_con
            wait_tra[tra_data["requestID"]] = 0
            ws_broadcast(ws_list, tra_data)
            request_num += 1
            while True:
                time.sleep(0.1)
                if wait_tra[tra_data["requestID"]] >= int(len(ws_list) * wrote_rate):
                    del(wait_tra[tra_data["requestID"]])
                    break
    serverthread.stop()
