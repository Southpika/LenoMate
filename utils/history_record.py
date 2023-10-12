import json
import os
import time

def time_suffix():
    return time.strftime("%Y%m%d", time.localtime(time.time()))

def save_history(user,chat):
    save_dir = r'./data'
    title =  str(user) + '_' + time_suffix() + '.txt'
    save_dir = os.path.join(save_dir,'chat_history',title)
    with open(save_dir, 'w', encoding='utf-8') as write_f:
        json.dump(chat, write_f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    test = {}
    save_history('222041053',save_history)