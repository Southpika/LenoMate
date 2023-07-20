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

# code 0 聊天  1 中间变量传输 2 文件 3 网页 
def load_and_run_model():
    global input_queue,output_queue
    print("模型加载中...")
    # model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    # tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    model = AutoModel.from_pretrained(args.model_dir, load_in_8bit=True, trust_remote_code=True, device_map='auto')
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir,trust_remote_code=True)
    
    model = PeftModel.from_pretrained(model, args.work_dir)
    model.is_parallelizable = True
    model.model_parallel = True
    model.eval()
    model_sim =  AutoModel.from_pretrained(args.simmodel_dir).to('cuda')
    tokenizer_sim = AutoTokenizer.from_pretrained(args.simmodel_dir)
    corpus = faiss_corpus(args=args,model = model_sim, tokenizer=tokenizer_sim)
    web_search = web_searcher(web_num=5)
    print("模型加载完成")
    pattern = r'<[^>]+>[:：]?'
    while True: 
        data_client = input_queue.get() # load data from client mode = 0是命令模式
        torch.cuda.empty_cache()
        if data_client['state_code'] == 0:
            input_statement = data_client['inputs']
            stop_criteria = StopWordsCriteria(tokenizer, ['<User>','<LenoMate>','<用户>','<Brother>'], stream_callback=None)
            
            if not data_client['mode']:
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

            elif data_client['mode']:
                print("当前为聊天模式...")
                prompt_chat = f"""<用户>：{input_statement}
<LenoMate>:"""
                
                with torch.no_grad():
                    input_ids = tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
                    out = model.generate(
                        input_ids=input_ids,
                        max_length=1000,
                        temperature=0.9,
                        top_p=0.95,
                        stopping_criteria = StoppingCriteriaList([stop_criteria])
                    )
                answer = tokenizer.decode(out[0]).split('<LenoMate>:')[1].strip('\n').strip()
                
                answer= re.sub(pattern,"",answer)
                send_data ={'chat':answer}
                output_queue.put(str(send_data))
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
        elif data_client['state_code'] == 2:
            query = data_client['inputs']
            
            content = data_client['content']
            type_doc = data_client['type_doc']
            prompt_chat = f"""基于以下{type_doc}的内容，简洁和专业的来回答用户关于此{type_doc}的问题。
## {type_doc}内容:
{content}
## 问题:
{query}
## 回答：
"""
            stop_criteria_ppt = StopWordsCriteria(tokenizer, ['##'], stream_callback=None)
            print('[分析功能]模型运行中...')
            with torch.no_grad():
                input_ids = tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
                out = model.generate(
                    input_ids=input_ids,
                    max_length=8000,
                    temperature=0.9,
                    top_p=0.95,
                    stopping_criteria = StoppingCriteriaList([stop_criteria_ppt])
                )
            print(tokenizer.decode(out[0]))
            answer = tokenizer.decode(out[0]).split('## 回答：')[1]
            send_data ={'chat':answer}
            output_queue.put(str(send_data))
        elif data_client['state_code'] == 3:
            query = data_client['inputs']
            
            web_contents = web_search.search_main(query)
            content = ''
            for item in web_contents[1]:
                content += item
                content += '\n'
            prompt_chat = f"""基于以下的内容，简洁和专业的来回答用户的问题。
## 内容:
{content}
## 问题:
{query}
## 回答：
"""
            stop_criteria_ppt = StopWordsCriteria(tokenizer, ['##'], stream_callback=None)
            print('[分析功能]模型运行中...')
            with torch.no_grad():
                input_ids = tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
                out = model.generate(
                    input_ids=input_ids,
                    max_length=8000,
                    temperature=0.9,
                    top_p=0.95,
                    stopping_criteria = StoppingCriteriaList([stop_criteria_ppt])
                )
            print(tokenizer.decode(out[0]))
            answer = tokenizer.decode(out[0]).split('## 回答：')[1]
            send_data ={'chat':answer}
            output_queue.put(str(send_data))            
            



def handle_client(client_socket, client_address):
    global input_queue,output_queue
    input_queue_client = queue.Queue()
    output_queue_client = queue.Queue()
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    temp_data = "{'chat':'你好，我是LenoMate，请问有什么可以帮您','command':'START chrome.exe http://localhost:8081/'}"
    client_socket.send(temp_data.encode('utf-8'))
    while True:
        try:
            # 接收客户端消息
            data = client_socket.recv(102400).decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                input_queue_client.put(eval(data))    
                data_temp = input_queue_client.get()
                input_queue.put(data_temp) # put data into input_queue
                # input_queue.put(input_queue_client.get()
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