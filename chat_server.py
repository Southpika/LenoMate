# -*- coding: UTF-8 -*-
"""
File_name: chat_server.py
author: tanzhehao
version: /

Overview:
这个Python文件为服务端的后端，主要包含了一个聊天服务器，用于与客户端建立连接并进行聊天。服务器利用LenoMate和bot_hello（打招呼开头语）来处理客户端的请求，并提供多种功能。

Usage:
- 运行该文件以启动聊天服务器，等待客户端连接。
- 客户端连接后，服务器将发送欢迎消息，并可以进行聊天、文件传输、网页请求、功能执行等操作。

Dependencies:
- Python 3.10
- 使用了来自'operation'、'utils'、'lenomate'（模型主文件）等模块的自定义代码。

Notes:
- 请确保所有依赖库都已正确安装。
- 客户端应按照服务器的IP地址连接（本地局域网，如果不是本地请参照内网穿透平台的ip）。
- 服务器在接收到客户端消息后，会使用LenoMate来处理请求。
"""

from operation.hello import bot_hello
from lenomate import LenoMate
import os, sys, platform, threading, socket, argparse
from utils.history_record import save_history


def _clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")
    if 'ipykernel' in sys.modules:
        from IPython.display import clear_output as clear
        clear()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--k', default=1)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--index_location', default='./data/test.index')
    parser.add_argument('--search', default=1)

    parser.add_argument('--glm-work-dir', default=r"./tzh_model/lenomate_hi")
    # parser.add_argument('--model-dir',default=r"model\model_chatglm2")
    # parser.add_argument('--glm-model-dir', default=r"D:\tzh\model_chatglm2")
    # parser.add_argument('--simmodel-dir',default=r"model\models--GanymedeNil--text2vec-large-chinese")
    # parser.add_argument('--simmodel-dir', default="GanymedeNil/text2vec-large-chinese")
    parser.add_argument('--simmodel-dir', default="./models/models--GanymedeNil--text2vec-large-chinese")
    # parser.add_argument('--qw-model-dir', default=r"C:\Users\admin\Desktop\qw\qwen")
    # parser.add_argument('--qw-model-dir', default=r"C:\Users\admin\Desktop\新建文件夹\glm_train\merged_model")
    parser.add_argument('--qw-model-dir', default=r"./models/merged_model")

    # parser.add_argument('--simmodel-dir',default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    parser.add_argument('--temperature', default=0.95)
    # parser.add_argument('--model-dir',default=r"/home/tzh/model_dir_cache/models--THUDM--chatglm-6b")
    config = parser.parse_args()
    return config


args = get_parser()


# args.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),args.model_dir)
# args.simmodel_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),args.simmodel_dir)
# code 0 聊天  1 中间变量传输 2 文件 3 网页 4功能 5 蓝屏 6绘画 7邮件


def handle_client(client_socket, client_address, lenomate):
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    data = client_socket.recv(1024)
    data = data.decode('utf-8')
    hello_state = bot_hello(system=data, language='ch')
    client_socket.sendall(str(hello_state.hello(ast=False)).encode('utf-8') + b'__end_of_socket__')
    print('欢迎语已发送')
    history_record = {}
    while True:
        try:
            # 接收客户端消息
            socket_data = b''
            while True:
                data = client_socket.recv(10240)
                if data.endswith(b'__end_of_socket__'):
                    socket_data += data[:-len(b'__end_of_socket__')]
                    break
                socket_data += data
            socket_data = socket_data.split(b'__end_of_socket__')[-1]
            data = socket_data.decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                send_data = lenomate.process(eval(data), history_record.get(eval(data)['state_code']))
                if eval(data)['state_code'] in [0, 3, 2, 5, 7]:
                    start = True
                    for res, history in send_data['chat']:
                        send_data = {'chat': res, 'follow': start}
                        client_socket.sendall(str(send_data).encode('utf-8') + b'__end_of_socket__')
                        start = False
                    end_data = {'chat': res, 'follow': False, 'end': True}
                    client_socket.sendall(str(end_data).encode('utf-8') + b'__end_of_socket__')
                    if eval(data)['state_code'] != 7:
                        history_record[eval(data)['state_code']] = history
                    else:
                        history_record[0] = history_record.get(0,[]) + history
                    save_history(client_address[1], history_record)
                else:
                    client_socket.sendall(str(send_data).encode('utf-8') + b'__end_of_socket__')
                if eval(data)['state_code'] != 6:
                    print(f"回复{client_address[0]}:{client_address[1]}的消息：{send_data}")
        except Exception as e:
            print(e)
            print(f"与{client_address[0]}:{client_address[1]}的连接已断开")
            client_socket.close()
            break


def chat_server(ip='192.168.137.1'):
    print('*' * 50)
    print(f"您现在的IP地址为{ip}，请客户端按照此IP地址连接")
    print('*' * 50)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 监听端口
    server_socket.bind((ip, 8888))
    server_socket.listen(5)
    print("服务器已启动，等待连接...")
    lenomate = LenoMate('qw', args=args)
    while True:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()
        # 创建线程处理客户端连接
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, lenomate))
        client_thread.start()


if __name__ == '__main__':
    import socket

    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    chat_server(ip)
    # print(os.path.abspath(__file__))
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)),args.model_dir))
