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
from transformers import StoppingCriteriaList,StoppingCriteria
import operation.prompt as prompt
import operation.operation_server as operation
from stop_criterion import StopWordsCriteria
import argparse
from peft import PeftModel
import re
from utils.web_search import web_searcher
from operation.hello import bot_hello 
import chat_mode

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--k', default=1)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--index_location', default='./data/test.index')
    parser.add_argument('--search', default=1)

    parser.add_argument('--work-dir',default=r"./tzh_model/lenomate_hi")
    parser.add_argument('--model-dir',default=r"C:\Users\89721\Desktop\model_chatglm2")
    # parser.add_argument('--simmodel-dir',default=r"C:\Users\89721\Desktop\models--GanymedeNil--text2vec-large-chinese")
    parser.add_argument('--simmodel-dir',default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    parser.add_argument('--temperature',default=0.95)
    # parser.add_argument('--model-dir',default=r"/home/tzh/model_dir_cache/models--THUDM--chatglm-6b")
    config = parser.parse_args()      
    return config
args = get_parser()

def sys(result):
    synthesis.main(result)
    play.play()

# code 0 聊天  1 中间变量传输 2 文件 3 网页 4功能
def load_and_run_model():
    global input_queue,output_queue
    print("模型加载中...")

    model = AutoModel.from_pretrained(args.model_dir, load_in_8bit=True, trust_remote_code=True, device_map='auto')
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir,trust_remote_code=True)
    model = PeftModel.from_pretrained(model, args.work_dir)
    model.is_parallelizable = True
    model.model_parallel = True
    model.eval()
    model_sim =  AutoModel.from_pretrained(args.simmodel_dir).to('cuda')
    tokenizer_sim = AutoTokenizer.from_pretrained(args.simmodel_dir)
    corpus = faiss_corpus(args=args,model = model_sim, tokenizer=tokenizer_sim)
    bot = chat_mode.chat_bot(model,tokenizer)    
    print("模型加载完成")

    while True: 
        data_client = input_queue.get() 

        
        if data_client['state_code'] == 4:
            input_statement = data_client['inputs']
            # if not data_client['mode']:
            print("当前为命令模式...")
            try:
                selected_idx, score = corpus.search(query=input_statement, verbose=True)
                if selected_idx in [0,1,4,5]:
                    command = f"python operation/operation_client.py --select-idx {selected_idx}"
                    client_data = {}
                    client_data['command']=command
                    client_data['state_code']=1
                    output_queue.put(str(client_data))
                    
                else:
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
                continue
            
        elif data_client['state_code'] == 1:
            context = data_client['inputs']
            torch.cuda.empty_cache()
            if selected_idx == 5:
                opt = eval(f"operation.Operation{selected_idx}")(input_statement,context,model_sim,tokenizer_sim)
            else:
                opt = eval(f"operation.Operation{selected_idx}")(input_statement,context)
            result = opt.fit(model, tokenizer)

            output_queue.put(result)
            print("模型输出：", result)
        else:
            torch.cuda.empty_cache()
            answer_dict = eval(f"bot.mode{data_client['state_code']}")(data_client)
            output_queue.put(str(answer_dict))
           


def handle_client(client_socket, client_address):
    global input_queue,output_queue
    input_queue_client = queue.Queue()
    output_queue_client = queue.Queue()
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    hello_state = bot_hello()
    client_socket.send(str(hello_state.hello(ast = True)).encode('utf-8'))
    while True:
        try:
            # 接收客户端消息
            data = client_socket.recv(102400).decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                input_queue_client.put(eval(data))    
                data_temp = input_queue_client.get()
                input_queue.put(data_temp) 
                send_data = output_queue.get()
                output_queue_client.put(send_data)
                client_socket.send(str(output_queue_client.get()).encode('utf-8'))
                print(f"回复{client_address[0]}:{client_address[1]}的消息：{send_data}")
        except Exception as e:
            print(e)
            print(f"与{client_address[0]}:{client_address[1]}的连接已断开")
            client_socket.close()
            break



input_queue,output_queue = queue.Queue(),queue.Queue()
model_thread = threading.Thread(target=load_and_run_model)
model_thread.daemon = True
model_thread.start()



def chat_server(ip='192.168.137.1'):
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

if __name__ == '__main__':
    chat_server()