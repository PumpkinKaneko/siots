# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time
import hashlib

"""
Called when new client entry
"""
def new_client(client, server):
    if server_ready == True:
        print (client["address"][0] + " joined")

"""
Define websocket server
"""
def wsserver(address):
    server = WebsocketServer(9999, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

"""
Called when server receive message
"""
def msg_reaction(client, server, rec_msg):
    rec_json = MP.str_to_dic(rec_msg)
    react_func(rec_json, client["address"][0])

"""
Define reaction to message
"""
def react_func(json_file, sender_add):
    title = json_file["title"]
    requestID = json_file["requestID"]
    if title == "request":
        contents = json_file["contents"]
        mod = int(json_file["mod"])
        sig = json_file["signature"]
        request_data[requestID] = {"num_per":0, "num_den":0, "sender_add":json_file["sender_add"], "contents":contents}
        time.sleep(0.1)
        if MP.cer_add(contents, sig, mod):
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"permited"})
        else:
            ws_broadcast(ws_list, {"title":"react", "requestID":requestID, "permission":"denied"})
    elif title == "react" and requestID in request_data:
        if json_file["permission"] == "permited":
            request_data[requestID]["num_per"] += 1
            if request_data[requestID]["num_per"] >= ws_per_rate:
                written_con = request_data[requestID]["contents"]
                tra_cre = request_data[requestID]["sender_add"]
                MP.write_ledger(written_con)
                ws_to_leaf(tra_cre, "Transaction_was_written")
                del(request_data[requestID])
        elif json_file["permission"] == "denied":
            request_data[requestID]["num_den"] += 1
            if request_data[requestID]["num_den"] > ws_den_rate:
                tra_cre = request_data[requestID]["sender_add"]
                del(request_data[requestID])
                ws_to_leaf(tra_cre, "Transaction_was_not_written")
    elif title == "transaction":
        print ("Received transaction from " + sender_add)
        tra_data = {}
        tra_data["title"] = "request"
        tra_data["sender_add"] = sender_add
        tra_data["requestID"] = requestID
        tra_data["contents"] = json_file["contents"]
        tra_data["mod"] = json_file["mod"]
        tra_data["signature"] = json_file["signature"]
        ws_broadcast(ws_list, tra_data)

"""
Make websocket connection and list of server
"""
def ws_core_connect(address):
    ws_connect_list = []
    for num_add in range(len(address) - 1):
        ws_connect_list.append(create_connection("ws://" + address[num_add + 1] + ":9999/"))
    return ws_connect_list

"""
Send json file to opponent
"""
def ws_transmission(ws, json_file):
    sendmsg = MP.dic_to_str(json_file)
    ws.send(sendmsg)

"""
Send json file to participants
"""
def ws_broadcast(ws_list, json_file):
    for num_add in range(len(ws_list)):
        ws_transmission(ws_list[num_add - 1], json_file)

"""
Send message to leaf node
"""
def ws_to_leaf(address, msg):
    ws_leaf = create_connection("ws://" + address + ":9998/")
    ws_transmission(ws_leaf, {"result":msg})
    ws_leaf.close()

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
    server_ready = True
    while True:
        print ("If you want to finish, input \"finish\"")
        finish = input()
        if finish == "finish":
            break
    serverthread.stop()
