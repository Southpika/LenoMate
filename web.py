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
import synthesis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许进行跨域请求的来源列表，*作为通配符
    allow_credentials=True,#跨域请求支持cookie，默认为否
    allow_methods=["*"],#允许跨域请求的HTTP方法
    allow_headers=["*"],#允许跨域请求的HTTP头列表
)

app.add_middleware(GZipMiddleware)



@app.post("/text")
async def text(data: Dict):

    return maintext.main(data.get("userInput"))

@app.post("/")
async def start(data: Dict):
    start = "你好，我是LenoMate，请问有什么可以帮您"
    synthesis.main(start)
    play.play()

@app.post("/audio")
async def audio(audioData: bytes = File(...)):

    with open('./voice1.wav','wb') as f:
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