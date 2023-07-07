# -*- coding: UTF-8 -*-
import os
import socket
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import audio.play as play
import audio.synthesis as synthesis
import audio.recognition as recognition
import threading
import queue
import speech_recognition as sr
from typing import Dict
import subprocess
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/web", StaticFiles(directory="web"), name="web")


@app.post("/data")
async def upload_file(file: UploadFile):
    # 执行你的文件处理逻辑，例如保存文件到磁盘或进行其他操作
    contents = await file.read()
    file_extension = os.path.splitext(file.filename)[1]
    with open("tempfile" + file_extension, "wb") as f:
        f.write(contents)
    global filemode
    filemode = not filemode
    return {"filename": file.filename}


@app.delete("/data/{filename}")
def delete_file(filename: str):
    file_extension = os.path.splitext(filename)[1]
    name = "tempfile" + file_extension
    if os.path.exists(name):
        os.remove(name)
        global filemode
        filemode = not filemode
        return {"message": f"文件 '{filename}' 已成功删除"}
    else:
        raise HTTPException(status_code=404, detail=f"文件 '{filename}' 不存在")


@app.get("/")  # 显示首页
def start():
    with open("QA.html", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/text")  # 文本框交互
def text(data: Dict):
    thred = threading.Thread(target=sys, args=("请稍等",))
    thred.start()
    client_socket.send(str({"inputs": data.get("userInput"), "mode": int(mode), "state_code": 0}).encode("utf-8"))


@app.post("/text2")  # 切换按钮
def text2(data: Dict):
    global mode
    mode = not mode
    res = "当前为聊天模式" if mode else "当前为功能模式"
    thred = threading.Thread(target=sys, args=(res,))
    thred.start()
    return res


@app.post("/audio")  # 显示返回消息
def audio(data: Dict):
    result, bot = output_queue.get()
    if bot:
        thred = threading.Thread(target=sys, args=(result,))
        thred.start()
    return JSONResponse(content={"result": result, "bot": bot})


def sys(result):
    synthesis.main(result)
    play.play()
    function_finished_flag.set()


def handle(**kwargs):
    if "command" in kwargs.keys():
        temp = subprocess.check_output(kwargs["command"], shell=True)
        if "chat" not in kwargs.keys():
            client_socket.send(
                str({"inputs": temp.decode("utf-8").replace("\r\n\x1b[0m", ''), "mode": int(mode),
                     "state_code": 1}).encode("utf-8"))
    if "chat" in kwargs.keys():
        output_queue.put((kwargs["chat"], True))


def receive_messages():
    print("已与服务器建立连接")
    while True:
        try:
            data = eval(client_socket.recv(10240).decode('utf-8'))
            print(f"收到服务器的消息：{data}")
            handle(**data)
        except Exception as e:
            print(e)
            print("与服务器的连接已断开")
            client_socket.close()
            break


# def load_and_run_audio():
#     global mode
#     while True:
#         print("处于待唤醒状态")
#         try:
#             # 使用麦克风录制音频
#             with sr.Microphone(sample_rate=8000) as source:
#                 r = sr.Recognizer()
#                 audio_frame = r.listen(source, phrase_time_limit=5)
#
#             # 使用语音识别器解析音频
#             # result = r.recognize_google(audio_frame, language="zh-CN")
#             result = recognition.main2(audio_frame.frame_data)
#             print("识别结果：", result)
#
#             # 根据指令执行相应的操作
#             if "小诺" in result or "想诺" in result:
#                 # 执行您的程序代码
#                 sys("我在听")
#                 while True:
#                     print("处于已唤醒状态")
#                     try:
#                         # 使用麦克风录制音频
#                         with sr.Microphone(sample_rate=8000) as source:
#                             r = sr.Recognizer()
#                             audio_frame = r.listen(source, timeout=5)
#                         # 使用语音识别器解析音频
#                         # result = r.recognize_google(audio_frame, language="zh-CN")
#                         result = recognition.main2(audio_frame.frame_data)
#                         print("识别结果：", result)
#
#                         # 根据指令执行相应的操作
#                         if not result.strip():
#                             sys("你好像没有说话，试试说小诺小诺唤醒我")
#                             break
#                         else:
#                             output_queue.put((result, False))
#                             sys("请稍等")
#                             client_socket.send(
#                                 str({"inputs": result, "mode": int(mode), "state_code": 0}).encode(
#                                     "utf-8"))
#                             function_finished_flag.clear()
#                             function_finished_flag.wait()
#
#                     except sr.RequestError as e:
#                         print("无法连接", str(e))
#                         sys("你好像没有说话，试试说小诺小诺唤醒我")
#                         break
#                     except (sr.WaitTimeoutError, sr.UnknownValueError):
#                         sys("你好像没有说话，试试说小诺小诺唤醒我")
#                         break
#
#         except sr.RequestError as e:
#             print("无法连接", str(e))
#         except (sr.WaitTimeoutError, sr.UnknownValueError):
#             print("无法识别语音")


if __name__ == '__main__':
    # 聊天模式为True
    mode, filemode = True, False
    function_finished_flag = threading.Event()
    # 创建一个显示队列
    output_queue = queue.Queue()
    # # 创建套接字
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # # 连接服务器
    # client_socket.connect(('192.168.137.1', 8888))
    # # 创建线程接收消息
    # receive_thread = threading.Thread(target=receive_messages)
    # receive_thread.start()
    # # 创建一个线程，用于加载和运行语音识别和合成
    # model_thread = threading.Thread(target=load_and_run_audio)
    # # 启动线程
    # model_thread.start()
    # 启动前端
    uvicorn.run(app, host="127.0.0.1", port=8081)
