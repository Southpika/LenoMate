# -*- coding: UTF-8 -*-

from typing import Dict
from fastapi import FastAPI, File, UploadFile, Form
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
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
import json

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
mode = True  # 聊天为True


def load_and_run_model(input_queue):
    print("模型加载中...")
    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    corpus = faiss_corpus()
    print("模型加载完成")

    global running
    while running:
        input_statement = input_queue.get()
        if not mode:
            print("当前为命令模式...")
            try:
                selected_idx, score = corpus.search(query=input_statement, verbose=False)
                torch.cuda.empty_cache()
                opt = eval(f"operation.Operation{selected_idx}")(input_statement)
                result = opt.fit(model, tokenizer)
                output_queue.put(result)
                print("模型输出：", result)
            except:
                running = False
                break
        if mode:
            print("当前为聊天模式...")
            prompt_chat = f"""<用户>：{input_statement}
            <ChatGLM-6B>："""
            model.eval()
            with torch.no_grad():
                input_ids = tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
                out = model.generate(
                    input_ids=input_ids,
                    max_length=200,
                    temperature=0.9,
                    top_p=0.95,
                )
            answer = tokenizer.decode(out[0]).split('<ChatGLM-6B>:')[1].strip('\n').strip()
            output_queue.put(answer)


# 创建一个输入队列
input_queue = queue.Queue()
output_queue = queue.Queue()
# 创建一个线程，用于加载和运行模型
model_thread = threading.Thread(target=load_and_run_model, args=(input_queue,))
model_thread.daemon = True
# 启动线程
model_thread.start()


@app.post("/text")
async def text(data: Dict):
    input_queue.put(data.get("userInput"))
    result = output_queue.get()
    thred = threading.Thread(target=sys_thred, args=(result,))
    thred.start()
    return result


@app.post("/text2")  # 切换按钮
async def text(data: Dict):
    global mode
    mode = not mode
    res = '已切换成聊天模式' if mode else '已切换成功能模式'
    thred = threading.Thread(target=sys_thred, args=(res,))
    thred.start()
    return res


@app.post("/text3")  # 识别和合成
async def text(data: Dict):
    res = data.get("userInput")
    thred = threading.Thread(target=sys_thred, args=(res,))
    thred.start()
    return res


@app.post("/")
async def start(data: Dict):
    start = "你好，我是LenoMate，请问有什么可以帮您"
    synthesis.main(start)
    play.play()


@app.options("/")
async def start(data: Dict):
    start = "你好，我是LenoMate，请问有什么可以帮您"
    synthesis.main(start)
    play.play()


def sys_thred(result):
    synthesis.main(result)
    play.play()


@app.post("/audio")
async def audio(audioData: bytes = File(...)):
    with open('data/voice1.wav', 'wb') as f:
        f.write(audioData)
    f.close()
    os.system('ffmpeg -y -i data/voice1.wav -ac 1 -ar 16000 data/voice.wav')
    input_statement = recognition.main()
    return input_statement


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8081)
    # start = "你好，我是LenoMate，请问有什么可以帮您"
    # synthesis.main(start)
    # play.play()
