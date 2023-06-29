# -*- coding: UTF-8 -*-
import socket
import threading
import queue
import os
from transformers import AutoTokenizer, AutoModel
from utils.search_doc_faiss import faiss_corpus
import torch
import audio.play as play
import audio.synthesis as synthesis

def sys(result):
    synthesis.main(result)
    play.play()

def load_and_run_model():
    global input_queue,output_queue
    print("模型加载中...")
    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    # model = AutoModel.from_pretrained(r"C:\Users\Opti7080\Desktop\models--THUDM--chatglm-6b", trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    model_sim =  AutoModel.from_pretrained("GanymedeNil/text2vec-large-chinese").to('cuda')
    tokenizer_sim = AutoTokenizer.from_pretrained("GanymedeNil/text2vec-large-chinese")
    corpus = faiss_corpus(model = model_sim, tokenizer=tokenizer_sim)
    print("模型加载完成")

    while True: 
        data_client = input_queue.get() # load data from client mode = 0是命令模式
        if data_client['state_code'] == 0:
            if not data_client['mode']:
                print("当前为命令模式...")
                input_statement = data_client['inputs']
                try:
                    selected_idx, score = corpus.search(query=input_statement, verbose=True)
                    if selected_idx in [0,1,4,5]:
                        output_queue.put
                    torch.cuda.empty_cache()
                    if selected_idx == 5:
                        opt = eval(f"operation.Operation{selected_idx}")(input_statement,model_sim,tokenizer_sim)
                    else:
                        opt = eval(f"operation.Operation{selected_idx}")(input_statement)
                    result = opt.fit(model, tokenizer)
                    output_queue.put((result, True))
                    print("模型输出：", result)
                except Exception as e:
                    print('#' * 50)
                    print('error info', e)
                    break
            if data_client['mode']:
                print("当前为聊天模式...")
                prompt_chat = f"""<用户>：{input_statement}
                <ChatGLM-6B>："""
                model.eval()
                with torch.no_grad():
                    input_ids = tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
                    out = model.generate(
                        input_ids=input_ids,
                        max_length=300,
                        temperature=0.9,
                        top_p=0.95,
                    )
                answer = tokenizer.decode(out[0]).split('<ChatGLM-6B>:')[1].strip('\n').strip()
                output_queue.put((answer, True))



def handle_client(client_socket, client_address):
    global input_queue,output_queue
    input_queue_client = queue.Queue()
    output_queue_client = queue.Queue()
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    temp_data = "{'command':'START chrome.exe http://localhost:8081/'}"
    client_socket.send(temp_data.encode('utf-8'))
    while True:
        try:
            # 接收客户端消息
            data = client_socket.recv(10240).decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                
                input_queue_client.put(eval(data))  
                
                data_temp = input_queue_client.get()
                input_queue.put(data_temp) # put data into input_queue
                # input_queue.put(input_queue_client.get()

                send_data = output_queue.get()
                output_queue_client.put()
                client_socket.send(output_queue_client.get().encode('utf-8'))
                print(f"回复{client_address[0]}:{client_address[1]}的消息：{data}")
        except Exception as e:
            print(e)
            print(f"与{client_address[0]}:{client_address[1]}的连接已断开")
            client_socket.close()
            break



def main(ip='192.168.137.1'):
# 创建套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 监听端口
    server_socket.bind((ip, 8888))
    server_socket.listen(5)
    print("服务器已启动，等待连接...")
    while True:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()
        # 创建线程处理客户端连接
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
