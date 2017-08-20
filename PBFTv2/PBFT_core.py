# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time
import json

def new_client(client, server):
    if server_ready == True:
        print (client["address"][0] + " joined")
def wsserver(address):
    server = WebsocketServer(9999, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

def msg_reaction(client, server, rec_msg):
    rec_json = MP.msg_to_dict(rec_msg)
    react_func(rec_json, client["address"][0])

def react_func(json_file, sender_add):
    title = json_file["title"]
    requestID = json_file["requestID"]
    if title == "request":
        contents = json_file["contents"]
        key = int(json_file["key"])
        mod_num = int(json_file["mod_num"])
        dec_con = MP.decrypt(contents, key, mod_num)
        request_data[requestID] = {"num_per":0, "num_den":0, "sender_add":json_file["sender_add"], "contents":dec_con}
        time.sleep(0.1)
        if MP.cer_add(contents, key, mod_num):
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"permited"})
        else:
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"denied"})
    elif title == "react" and requestID in request_data:
        if json_file["permission"] == "permited":
            request_data[requestID]["num_per"] += 1
            if request_data[requestID]["num_per"] >= ws_per_rate:
                MP.write_ledger(request_data[requestID]["contents"])
                ws_to_leaf(request_data[requestID]["sender_add"], "Transaction_was_written")
                del(request_data[requestID])
        elif json_file["permission"] == "denied":
            request_data[requestID]["num_den"] += 1
            if request_data[requestID]["num_den"] > ws_den_rate:
                ws_to_leaf(request_data[requestID]["sender_add"], "Transaction_was_not_written")
                del(request_data[requestID])
    elif title == "transaction":
        tra_data = {}
        tra_data["title"] = "request"
        tra_data["sender_add"] = sender_add
        tra_data["requestID"] = requestID
        tra_data["contents"] = json_file["contents"]
        tra_data["key"] = json_file["key"]
        tra_data["mod_num"] = json_file["mod_num"]
        ws_broadcast(ws_list, tra_data)


def ws_core_connect(address):
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

def ws_to_leaf(address, msg):
    ws_to_leaf = create_connection("ws://" + address + ":9998/")
    ws_transmission(ws_to_leaf, {"result":msg})
    ws_to_leaf.close()

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
    server_ready = False
    address = MP.get_address("core_address.txt")
    serverthread = PBFTServer(address[0])
    serverthread.start()
    request_data = {}
    time.sleep(0.1)
    print ("If you are ready, input \"ok\"")
    while True:
        ready = input()
        if ready == "ok":
            break
    ws_list = ws_core_connect(address)
    ws_per_rate = len(ws_list) * 2 / 3
    ws_den_rate = len(ws_list) / 3
    ws_leaf = {}
    server_ready = True
    while True:
        print ("If you want to finish, input \"finish\"")
        finish = input()
        if finish == "finish":
            break
    serverthread.stop()
