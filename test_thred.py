import operation.prompt as prompt
import operation.operation as operation
import torch
from transformers import AutoTokenizer, AutoModel
import warnings
from utils.search_doc_faiss import faiss_corpus
from data.map import instruction_prompt_map
import audio.recognition as recognition, audio.synthesis as synthesis, audio.play as play, audio.record as record
import threading
import queue

running = True
# 模拟加载和运行模型的函数
def load_and_run_model(input_queue):
    # 模型加载过程，可以根据实际情况进行编写
    print("模型加载中...")
    # 模型加载完成
    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4",trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    corpus = faiss_corpus()
    
    print("模型加载完成")
    global running, lock
    lock.acquire()
    while running:
        try:

            input_statement = input_queue.get()
            try:
                input_statement = input_statement
                selected_idx,score = corpus.search(query = input_statement,verbose=False)
                torch.cuda.empty_cache()

                # 将结果转换为字符串
                opt = eval(f"operation.Operation{selected_idx}")(input_statement)
                result = opt.fit(model,tokenizer)

                # 处理完成后，可以将结果返回给主线程，或者进行其他操作
                print("模型输出：", result)
            except:
                running = False
                break
        except KeyboardInterrupt:
            running = False
            break
    lock.release()

# 创建一个输入队列
input_queue = queue.Queue()

lock = threading.Lock()

# 创建一个线程，用于加载和运行模型
model_thread = threading.Thread(target=load_and_run_model, args=(input_queue,))
# 设置线程为后台线程，使程序可以退出
model_thread.daemon = True
# 启动线程
model_thread.start()

lock.acquire()
try:
    while True:
        # 接收用户输入
        input_data = input("请输入数据（输入exit退出）：")
        # 将输入数据放入输入队列
        if input_data == "exit":
            running = False
            input_queue.put(None)
            break
        input_queue.put(input_data)
except KeyboardInterrupt:
    pass
lock.release()

input_queue.put(None)  # 发送终止信号给模型线程
# 退出程序时，清空输入队列并等待模型线程结束
input_queue.join()
