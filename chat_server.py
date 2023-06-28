# -*- coding: UTF-8 -*-
import socket
import threading
import queue
import os

def handle_client(client_socket, client_address):
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    while True:
        try:
            # 接收客户端消息
            data = client_socket.recv(10240).decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                
                input_queue.put(data)
                data_temp = input_queue.get()
                print(eval(data_temp),type(eval(data_temp)))
                temp = 'python operation\get_cominfo.py'
                # output_queue.put(input_queue.get())
                output_queue.put(temp)
                client_socket.send(output_queue.get().encode('utf-8'))
                print(f"回复{client_address[0]}:{client_address[1]}的消息：{data}")
        except Exception as e:
            print(e)
            print(f"与{client_address[0]}:{client_address[1]}的连接已断开")
            client_socket.close()
            break


input_queue = queue.Queue()
output_queue = queue.Queue()
# 创建套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 监听端口
server_socket.bind(('192.168.137.1', 8888))
server_socket.listen(5)
print("服务器已启动，等待连接...")
while True:
    # 接受客户端连接
    client_socket, client_address = server_socket.accept()
    # 创建线程处理客户端连接
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
