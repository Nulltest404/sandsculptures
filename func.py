# coding=utf-8
from datetime import datetime
import os


# 生成名字(最多传一个参数）
def random_name(*args):
    nowTime = datetime.now()
    random = os.urandom(24)
    if args:
        for arg in args:
            name = str(arg) + str(nowTime) + str(random)
    else:
        name = str(nowTime) + str(random)
    return name