# App info
__app_name__ = "gptshell"
__version__ = "0.1.0"

__waiting_quotes__ = ["热锅上的爆米花", "月亮等待日出", "蜗牛的马拉松", "翘首期盼的猫头鹰", "蜗牛赛跑", "努力中", "焦头烂额中", "倒计时的炸弹","焦急等待，像等快递","像等电影开场","末班车还没到","正在拼命","春天来了吗"]

import random

def _get_waiting_quotes():
    # randomly get a quote
    return random.choice(__waiting_quotes__)
