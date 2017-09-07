# coding:utf-8

import random

def expect(json_file, way="random"):
    if json_file["contents"] == "dice":
        if way == "random":
            expect = random.randint(1, 6)
            return expect
        elif way == "bias_6":
            one_ten = random.randint(1, 10)
            if one_ten >= 6:
                expect = 6
            else:
                expect = one_ten
        print ("expect:" + str(expect))
        return str(expect)

def run(json_file, que_con):
    if que_con["contents"] == "dice":
        one_ten = random.randint(1, 10)
        if one_ten >= 6:
            answer = 6
        else:
            answer = one_ten
        print ("answer:" + str(answer))
        return str(answer)
