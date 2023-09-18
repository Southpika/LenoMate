# -*- coding: UTF-8 -*-
import socket
import threading
import queue
from transformers import AutoTokenizer, AutoModel
from utils.search_doc_faiss import faiss_corpus
import torch
import operation.operation_server as operation
import argparse
from peft import PeftModel
from operation.hello import bot_hello 
import chat_mode
import os
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--k', default=1)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--index_location', default='./data/test.index')
    parser.add_argument('--search', default=1)

    parser.add_argument('--glm-work-dir',default=r"./tzh_model/lenomate_hi")
    # parser.add_argument('--model-dir',default=r"model\model_chatglm2")
    parser.add_argument('--glm-model-dir',default=r"D:\tzh\model_chatglm2")
    # parser.add_argument('--simmodel-dir',default=r"model\models--GanymedeNil--text2vec-large-chinese")
    parser.add_argument('--simmodel-dir',default="GanymedeNil/text2vec-large-chinese")
    parser.add_argument('--qw-model-dir',default=r"C:\Users\admin\Desktop\qw\qwen")
    
    
    # parser.add_argument('--simmodel-dir',default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    parser.add_argument('--temperature',default=0.95)
    # parser.add_argument('--model-dir',default=r"/home/tzh/model_dir_cache/models--THUDM--chatglm-6b")
    config = parser.parse_args()      
    return config
args = get_parser()
# args.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),args.model_dir)
# args.simmodel_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),args.simmodel_dir)
# code 0 聊天  1 中间变量传输 2 文件 3 网页 4功能 5 蓝屏 6绘画
def load_and_run_model():
    global input_queue,output_queue
    print("模型加载中...")

    # model = AutoModel.from_pretrained(args.model_dir, load_in_8bit=True, trust_remote_code=True, device_map='auto')
    model = AutoModel.from_pretrained(args.model_dir,  trust_remote_code=True).cuda()
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir,trust_remote_code=True)
    model = PeftModel.from_pretrained(model, args.work_dir)
    model.is_parallelizable = True
    model.model_parallel = True
    model.eval()
    model_sim =  AutoModel.from_pretrained(args.simmodel_dir).to('cuda')
    tokenizer_sim = AutoTokenizer.from_pretrained(args.simmodel_dir)
    # tokenizer_sim.eos_token = 
    corpus = faiss_corpus(args=args,model = model_sim, tokenizer=tokenizer_sim)
    bot = chat_mode.chat_bot(model,tokenizer)    
    opr = chat_mode.operation_bot(model,tokenizer,model_sim,tokenizer_sim,corpus)
    print("模型加载完成")

    while True: 
        data_client = input_queue.get() 
        torch.cuda.empty_cache()
        if data_client['state_code'] == 4 or data_client['state_code'] == 1:
            result = opr.fit(data_client)
            output_queue.put(str(result))
            print("模型输出：", result)

        else:
            answer_dict = eval(f"bot.mode{data_client['state_code']}")(data_client)
            output_queue.put(str(answer_dict))

class LenoMate:
    def __init__(self,model_type,args=args):
        if model_type == 'glm':
            print("模型加载中...")
            self.model = AutoModel.from_pretrained(args.glm_model_dir,  trust_remote_code=True).cuda()
            self.tokenizer = AutoTokenizer.from_pretrained(args.glm_model_dir,trust_remote_code=True)
            self.model = PeftModel.from_pretrained(self.model, args.glm_work_dir)
        
        if model_type == 'qw':
            self.model = AutoModel.from_pretrained(args.qw_model_dir,  trust_remote_code=True, bf16=True).cuda()
            self.tokenizer = AutoTokenizer.from_pretrained(args.qw_model_dir,trust_remote_code=True)            

        self.model.is_parallelizable = True
        self.model.model_parallel = True       
        self.model_sim =  AutoModel.from_pretrained(args.simmodel_dir).to('cuda')
        self.tokenizer_sim = AutoTokenizer.from_pretrained(args.simmodel_dir)
        corpus = faiss_corpus(args=args,model = self.model_sim, tokenizer=self.tokenizer_sim)
        self.bot = chat_mode.chat_bot(self.model,self.tokenizer)
        self.opr = chat_mode.operation_bot(self.model,self.tokenizer,self.model_sim,self.tokenizer_sim,corpus)
        print("模型加载完成")
    
    def process(self,data_client):
        torch.cuda.empty_cache()
        if data_client['state_code'] == 4 or data_client['state_code'] == 1:
            result = self.opr.fit(data_client)
            print("模型输出：", result)
            return str(result)
        else:
            answer_dict = eval(f"self.bot.mode{data_client['state_code']}")(data_client)
            return str(answer_dict)

def handle_client(client_socket, client_address, lenomate):
    global input_queue,output_queue
    print(f"已与{client_address[0]}:{client_address[1]}建立连接")
    hello_state = bot_hello()
    client_socket.send(str(hello_state.hello(ast = False)).encode('utf-8'))
    while True:
        try:
            # 接收客户端消息
            data = client_socket.recv(102400).decode('utf-8')
            if data:
                print(f"收到{client_address[0]}:{client_address[1]}的消息：{data}")
                # 广播消息给所有连接的客户端
                send_data = lenomate.process(eval(data))

                client_socket.send(send_data.encode('utf-8'))
                print(f"回复{client_address[0]}:{client_address[1]}的消息：{send_data}")
        except Exception as e:
            print(e)
            print(f"与{client_address[0]}:{client_address[1]}的连接已断开")
            client_socket.close()
            break

def chat_server(ip='192.168.137.1'):
    print('*'*50)
    print(f"您现在的IP地址为{ip}，请客户端按照此IP地址连接")
    print('*'*50)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 监听端口
    server_socket.bind((ip, 8888))
    server_socket.listen(5)
    print("服务器已启动，等待连接...")
    lenomate = LenoMate('glm',args=args)
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
    chat_server()
    # print(os.path.abspath(__file__))
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)),args.model_dir))