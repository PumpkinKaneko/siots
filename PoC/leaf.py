# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import hashlib
import APP
import time

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
    react_func(rec_json, client["address"][0])

"""
Define reaction to message
"""
def react_func(json_file, sender_add):
    if json_file["title"] == "req_to_leaf":
        expect_data = APP.expect(json_file, way="bias_6")
        signature = MP.gen_sig(expect_data + json_file["questionID"], keys["key"], keys["mod"])
        leaf_expect = {"title":"leaf_expect", "questionID":json_file["questionID"], "contents":expect_data, "signature":signature}
        ws_transmission(ws_core, leaf_expect)
    elif json_file["title"] == "expect_result":
        print (json_file["contents"])
        run = APP.run(json_file, question_list[json_file["questionID"]])
        con = run + json_file["questionID"]
        signature = MP.gen_sig(run, keys["key"], keys["mod"])
        run_result = {"title":"run_result", "questionID":json_file["questionID"], "contents":run, "signature":signature}
        ws_transmission(ws_core, run_result)
    else:
        print (json_file)

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
    keys_str = MP.make_keys()
    keys = {"key":int(keys_str["key"]), "mod":int(keys_str["mod"])}
    serverthread = PBFTServer(address[0])
    serverthread.start()
    print ("If you are ready, input \"ok\"")
    while True:
        ready = input()
        if ready == "ok":
            break
    run_rate = 1.0
    ws_core = create_connection("ws://" + address[1] + ":9999/")
    tra_data = {"title":"leaf_join", "key":keys["mod"]}
    ws_transmission(ws_core, tra_data)
    ID = 0
    question_list = {}
    while True:
        time.sleep(3)
        question = MP.make_question(address[0]+"_"+str(ID), keys)
        if question["contents"] == "finish":
            break
        if question["contents"] == "nodeinfo":
            ws_transmission(ws_core, {"title":"nodeinfo"})
            continue
        question_list[question["questionID"]] = question
        ws_transmission(ws_core, question)
        ID += 1
    serverthread.stop()
