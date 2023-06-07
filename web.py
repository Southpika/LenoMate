# -*- coding: UTF-8 -*-

from typing import Dict
from fastapi import FastAPI, File, UploadFile, Form
import uvicorn
import main
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
import main
import maintext
import audio.play as play
import audio.synthesis as synthesis
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
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许进行跨域请求的来源列表，*作为通配符
    allow_credentials=True,  # 跨域请求支持cookie，默认为否
    allow_methods=["*"],  # 允许跨域请求的HTTP方法
    allow_headers=["*"],  # 允许跨域请求的HTTP头列表
)

app.add_middleware(GZipMiddleware)

running = True

output_queue = queue.Queue()


# lock = threading.Lock()
# 模拟加载和运行模型的函数
def load_and_run_model(input_queue):
    # 模型加载过程，可以根据实际情况进行编写
    # global lock
    # lock.acquire()
    print("模型加载中...")
    # 模型加载完成

    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    corpus = faiss_corpus()

    print("模型加载完成")
    # lock.release()
    global running
    while running:
        try:

            input_statement = input_queue.get()
            try:
                input_statement = input_statement
                selected_idx, score = corpus.search(query=input_statement, verbose=False)
                torch.cuda.empty_cache()
                opt = eval(f"operation.Operation{selected_idx}")(input_statement)
                result = opt.fit(model, tokenizer)
                output_queue.put(result)
                # 处理完成后，可以将结果返回给主线程，或者进行其他操作
                print("模型输出：", result)
            except:
                running = False
                break
        except KeyboardInterrupt:
            running = False
            break


# 创建一个输入队列
input_queue = queue.Queue()

# 创建一个线程，用于加载和运行模型
model_thread = threading.Thread(target=load_and_run_model, args=(input_queue,))
model_thread.daemon = True
# 启动线程
model_thread.start()


@app.post("/text")
async def text(data: Dict):
    input_queue.put(data.get("userInput"))
    return output_queue.get()


@app.post("/")
async def start(data: Dict):
    start = "你好，我是LenoMate，请问有什么可以帮您"
    synthesis.main(start)
    play.play()


@app.post("/audio")
async def audio(audioData: bytes = File(...)):
    with open('./voice1.wav', 'wb') as f:
        f.write(audioData)
    f.close()

    os.system('ffmpeg -y -i voice1.wav -ac 1 -ar 16000 voice.wav')
    text = main.main()
    # os.system('rm ./voice.wav')
    return text


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8081)
    # start = "你好，我是LenoMate，请问有什么可以帮您"
    # synthesis.main(start)
    # play.play()
