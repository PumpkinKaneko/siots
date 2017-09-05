# coding:utf-8

import random

def expect(json_file, way="random"):
    if json_file["contents"] == "dice":
        if way == "random":
            expect = str(random.randint(1, 6))
            print ("expect:" + expect)
            return expect

def run(json_file, que_con):
    if que_con["contents"] == "dice":
        answer = str(random.randint(1, 6))
        print ("answer:" + answer)
        return answer
