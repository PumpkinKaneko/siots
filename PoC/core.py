# coding:utf-8

from websocket_server import WebsocketServer
from websocket import create_connection
import ModulePack as MP
import threading
import time

def new_client(client, server):
    print (client["address"][0] + " joined")

def wsserver(address):
    server = WebsocketServer(9999, host=address)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(msg_reaction)
    server.run_forever()

def msg_reaction(client, server, rec_msg):
    rec_json = MP.str_to_dic(rec_msg)
    react_func(rec_json, client["address"][0])

def react_func(json_file, sender_add):
    if json_file["title"] == "leaf_join":
        ws_leaf_add(sender_add, json_file["key"])
    elif json_file["title"] == "new_leaf":
        add_leaf_info(sender_add, json_file["address"], json_file["key"])
    elif json_file["title"] == "question":
        request = json_file
        request["title"] = "request"
        request["creater"] = sender_add
        ws_broadcast(request)
    elif json_file["title"] == "request":
        question = {}
        question["questionID"] = json_file["questionID"]
        question["contents"] = json_file["contents"]
        question["deadline"] = json_file["deadline"]
        question["creater"] = json_file["creater"]
        question["core"] = sender_add
        question["req_per"] = False
        question["req_per_num"] = 0
        question["req_den_num"] = 0
        question["leaf_expects"] = {}
        question["sum_expects"] = {}
        question["res_per"] = False
        question["res_per_num"] = 0
        question["res_den_num"] = 0
        question["sum_per"] = False
        question["sum_per_num"] = 0
        question["sum_den_num"] = 0
        question_data[json_file["questionID"]] = question
        time.sleep(0.1)
        con = json_file["contents"] + json_file["questionID"]
        sig = json_file["signature"]
        mod = node_info[sender_add][json_file["creater"]]["key"]
        if MP.cer_add(con, sig, mod):
            permission = {"title":"req_per", "questionID":json_file["questionID"], "permission":True}
            ws_broadcast(permission)
        else:
            permission = {"title":"req_per", "questionID":json_file["questionID"], "permission":False}
            ws_broadcast(permission)
    elif json_file["title"] == "req_per":
        if json_file["permission"] == True:
            question_data[json_file["questionID"]]["req_per_num"] += 1
            if question_data[json_file["questionID"]]["req_per_num"] >= ws_per_rate and question_data[json_file["questionID"]]["req_per"] == False:
                question_data[json_file["questionID"]]["req_per"] = True
                questionID = json_file["questionID"]
                contents = question_data[json_file["questionID"]]["contents"]
                deadline = question_data[json_file["questionID"]]["deadline"]
                req_to_leaf = {"title":"req_to_leaf", "questionID":questionID, "contents":contents, "deadline":deadline}
                leaf_broadcast(req_to_leaf)
                time.sleep(question_data[json_file["questionID"]]["deadline"] + 0.3)
                leaf_expects = {"title":"leaf_expects", "questionID":json_file["questionID"], "contents":question_data[json_file["questionID"]]["leaf_expects"]}
                ws_broadcast(leaf_expects)
                if core_address[0] == question_data[json_file["questionID"]]["core"]:
                    time.sleep(0.5)
                    sum_start = {"title":"sum_start", "questionID":json_file["questionID"]}
                    ws_transmission(core_list[core_address[0]], sum_start)
        else:
            question_data[json_file["questionID"]]["req_den_num"] += 1
            if question_data[json_file["questionID"]]["req_den_num"] > ws_den_rate and question_data[json_file["questionID"]]["req_per"] == False:
                question_data[json_file["questionID"]]["req_per"] = True
                denied = {"title":"denied", "questionID":json_file["questionID"], "contents":"req_per"}
                ws_transmission(core_list[question_data[json_file["questionID"]]["core"]], denied)
    elif json_file["title"] == "leaf_expect":
        leaf_expect = {"contents":json_file["contents"], "signature":json_file["signature"]}
        question_data[json_file["questionID"]]["leaf_expects"][sender_add] = leaf_expect
    elif json_file["title"] == "leaf_expects":
        checked_expect = {}
        for address in json_file["contents"].keys():
            con = json_file["contents"][address]["contents"] + json_file["questionID"]
            sig = json_file["contents"][address]["signature"]
            mod = node_info[sender_add][address]["key"]
            if MP.cer_add(con, sig, mod):
                checked_expect[address] = json_file["contents"][address]["contents"]
        question_data[json_file["questionID"]]["sum_expects"][sender_add] = checked_expect
    elif json_file["title"] == "sum_start":
        sum_expects = {"title":"sum_expects", "questionID":json_file["questionID"], "contents":question_data[json_file["questionID"]]["sum_expects"]}
        ws_broadcast(sum_expects)
    elif json_file["title"] == "sum_expects":
        if json_file["contents"] == question_data[json_file["questionID"]]["sum_expects"]:
            sum_per = {"title":"sum_per", "questionID":json_file["questionID"], "permission":True}
            ws_transmission(core_list[sender_add], sum_per)
        else:
            sum_per = {"title":"sum_per", "questionID":json_file["questionID"], "permission":False}
            ws_transmission(core_list[sender_add], sum_per)
    elif json_file["title"] == "sum_per":
        if json_file["permission"] == True:
            question_data[json_file["questionID"]]["sum_per_num"] += 1
            if question_data[json_file["questionID"]]["sum_per_num"] >= ws_per_rate and question_data[json_file["questionID"]]["sum_per"] == False:
                question_data[json_file["questionID"]]["sum_per"] = True
                sum_wei = MP.sum_weight(node_info, question_data[json_file["questionID"]]["sum_expects"])
                expect_result = {"title":"expect_result", "questionID":json_file["questionID"], "contents":sum_wei}
                ws_transmission(leaf_list[question_data[json_file["questionID"]]["creater"]], expect_result)
        else:
            question_data[json_file["questionID"]]["sum_den_num"] += 1
            if question_data[json_file["questionID"]]["sum_den_num"] > ws_den_rate and question_data[json_file["questionID"]]["sum_per"] == False:
                question_data[json_file["questionID"]]["sum_per"] = True
                denied = {"title":"denied", "questionID":json_file["questionID"], "contents":"sum_per"}
                ws_transmission(leaf_list[question_data[json_file["questionID"]]["creater"]], denied)
    elif json_file["title"] == "run_result":
        new_weight = MP.cal_weight(json_file["contents"], question_data[json_file["questionID"]]["sum_expects"])
        result = {"title":"result", "questionID":json_file["questionID"], "contents":json_file["contents"], "signature":json_file["signature"], "new_weight":new_weight}
        ws_broadcast(result)
    elif json_file["title"] == "result":
        question_data[json_file["questionID"]]["new_weight"] = json_file["new_weight"]
        question_data[json_file["questionID"]]["result"] = json_file["contents"]
        con = json_file["contents"]
        sig = json_file["signature"]
        mod = node_info[sender_add][question_data[json_file["questionID"]]["creater"]]["key"]
        if MP.cer_add(con, sig, mod):
            print(0)
            check_weight = MP.cal_weight(json_file["contents"], question_data[json_file["questionID"]]["sum_expects"])
            if check_weight == json_file["new_weight"]:
                print(1)
                wei_per = {"title":"wei_per", "questionID":json_file["questionID"], "permission":True}
                ws_broadcast(wei_per)
            else:
                wei_per = {"title":"wei_per", "questionID":json_file["questionID"], "permission":False}
                ws_broadcast(wei_per)
        else:
            print(3)
            print(json_file["signature"])
            wei_per = {"title":"wei_per", "questionID":json_file["questionID"], "permission":False}
            ws_broadcast(wei_per)
    elif json_file["title"] == "wei_per":
        if json_file["permission"] == True:
            question_data[json_file["questionID"]]["res_per_num"] += 1
            if question_data[json_file["questionID"]]["res_per_num"] >= ws_per_rate and question_data[json_file["questionID"]]["res_per"] == False:
                question_data[json_file["questionID"]]["res_per"] = True
                update_weight(question_data[json_file["questionID"]]["new_weight"])
                MP.write_json(question_data[json_file["questionID"]])
                MP.write_json(node_info)
        else:
            question_data[json_file["questionID"]]["res_den_num"] += 1
            if question_data[json_file["questionID"]]["res_den_num"] > ws_den_rate and question_data[json_file["questionID"]]["res_per"] == False:
                question_data[json_file["questionID"]]["res_per"] = True
                denied = {"title":"denied", "questionID":json_file["questionID"], "contents":"wei_per"}
                ws_transmission(core_list[question_data[json_file["questionID"]]["core"]], denied)
    elif json_file["title"] == "denied":
        que_den = json_file
        que_den["address"] = sender_add
        ws_transmission(leaf_list[question_data[json_file["questionID"]]["creater"]], que_den)
    elif json_file["title"] == "nodeinfo":
        ws_transmission(leaf_list[sender_add], {"title":"nodeinfo", "contents":nodeifo})

def ws_core_connect(core_add):
    ws_connect_dict = {}
    for add in core_add:
        ws_connect_dict[add] = create_connection("ws://" + add + ":9999/")
    return ws_connect_dict

def make_core_info(add_list):
    info = {}
    for core in add_list:
        info[core] = {}
    return info

def add_leaf_info(core, address, key):
    node_info[core][address] = {"key":key, "weight":1.0}

def ws_leaf_add(address, key):
    leaf_list[address] = create_connection("ws://" + address + ":9998/")
    new_leaf = {"title":"new_leaf", "address":address, "key":key}
    ws_broadcast(new_leaf)

def ws_transmission(ws, json_file):
    sendmsg = MP.dic_to_str(json_file)
    ws.send(sendmsg)

def ws_broadcast(json_file):
    for add in core_list.keys():
        ws_transmission(core_list[add], json_file)

def leaf_broadcast(json_file):
    for add in leaf_list.keys():
        ws_transmission(leaf_list[add], json_file)

def update_weight(new_weight):
    for core in new_weight.keys():
        for leaf in new_weight[core].keys():
            node_info[core][leaf]["weight"] += new_weight[core][leaf]

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
    question_data = {}
    core_address = MP.get_address("core_address.txt")
    node_info = make_core_info(core_address)
    serverthread = PBFTServer(core_address[0])
    serverthread.start()
    print ("If your servers are ready, input \"ok\"")
    while True:
        ready = input()
        if ready == "ok":
            break
    core_list = ws_core_connect(core_address)
    leaf_list = {}
    ws_per_rate = len(core_list) * 2 / 3
    ws_den_rate = len(core_list) / 3
    while True:
        print ("If you want to finish, input \"finish\"")
        print ("If you want to know nodes, input \"node\"")
        finish = input()
        if finish == "node":
            print (node_info)
        elif finish == "finish":
            break
    serverthread.stop()
