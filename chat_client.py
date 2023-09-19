# -*- coding: UTF-8 -*-
import os
import queue
import socket
import threading
from typing import Dict

import pythoncom
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import audio.speech_recognition as recognition
import audio.speech_synthesis as synthesis
import operation.read_file as rd
import utils.blue_screen as bs

app = FastAPI()
app.mount("/svg", StaticFiles(directory="svg"), name="svg")
app.mount("/web", StaticFiles(directory="web"), name="web")

root_path = os.path.dirname(os.path.abspath(__file__))


@app.post("/data")
async def upload_file(file: UploadFile):
    # 执行你的文件处理逻辑，例如保存文件到磁盘或进行其他操作
    contents = await file.read()
    file_extension = os.path.splitext(file.filename)[1]
    global file_type
    file_type = file_extension
    name = "./data/tempfile" + file_extension
    with open(name, "wb") as f:
        f.write(contents)
    global file_content, mode
    mode = 2
    reader = rd.read_file(name)
    file_content = reader.fit(trucation=10)
    threading.Thread(target=sys, args=("文件已上传，文件分析模式开启",)).start()
    return JSONResponse(
        content={"filename": file.filename, "message": f"文件'{file.filename}'已成功上传，文件分析模式开启"})


@app.delete("/data/{filename}")
def delete_file(filename: str):
    file_extension = os.path.splitext(filename)[1]
    name = "./data/tempfile" + file_extension
    if os.path.exists(name):
        os.remove(name)
        global mode
        mode = 0
        threading.Thread(target=sys, args=("文件已删除，文件分析模式关闭",)).start()
        return JSONResponse(content={"message": f"文件 '{filename}' 已成功删除，文件分析模式关闭"})
    else:
        raise HTTPException(status_code=404, detail=f"文件 '{filename}' 不存在")


@app.get("/")  # 显示首页
def start():
    with open("index.html", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/text")  # 文本框交互
def text(data: Dict):
    thred = threading.Thread(target=sys, args=("请稍等",))
    thred.start()
    message = {"inputs": data.get("userInput"), "state_code": mode}
    if mode == 2:
        type_doc = 'PDF' if file_type == '.pdf' else 'PPT'
        message["type_doc"] = type_doc
        message["content"] = file_content
    client_socket.send(str(message).encode("utf-8"))


@app.post("/text2")  # 切换按钮
def text2(data: Dict):
    global mode
    mode = data["switch"]
    print(mode)
    res = memo[mode]
    threading.Thread(target=sys, args=(res,)).start()
    return res


@app.post("/audio")  # 显示server返回消息
def audio(data: Dict):
    data, bot = output_queue.get()

    if 'image' in data.keys():
        with open('svg/1.png', 'wb') as file:
            file.write(data['image'])
        return JSONResponse(content={"location": 'svg/1.png', "bot": bot})
    else:
        result = data['chat']
        if bot:
            threading.Thread(target=sys, args=(result,)).start()

        return JSONResponse(content={"result": result.strip('\n'), "bot": bot})


@app.post("/image")
def wallpaper_set(data: Dict):
    from utils.wallpaper import main
    # data
    path = data['wall_path'].replace('http://localhost:8081/', '')
    print(os.path.join(root_path, path))
    main(os.path.join(root_path, path))


def sys(result):
    synthesis.speech_synthesis(result)
    function_finished_flag.set()


def evaluate(content):
    global eval_content
    pythoncom.CoInitialize()
    eval_content = eval(content)
    pythoncom.CoUninitialize()


def handle(**kwargs):
    if "command" in kwargs.keys():
        # temp = subprocess.check_output(kwargs["command"], shell=True)
        # temp = eval(kwargs["command"])
        eval_thred = threading.Thread(target=evaluate, args=(kwargs["command"],))
        eval_thred.start()
        eval_thred.join()
        global eval_content
        if "chat" not in kwargs.keys():
            client_socket.send(
                # str({"inputs": temp.decode("gbk").replace("\r\n\x1b[0m", ''), "state_code": 1}).encode("utf-8"))
                str({"inputs": eval_content, "state_code": 1}).encode("utf-8"))
    if "chat" in kwargs.keys():
        # kwargs['location'] = r"svg/2.png" #测试用

        output_queue.put((kwargs, True))
    elif 'image' in kwargs.keys():
        print(kwargs)
        output_queue.put((kwargs, True))


def receive_messages():
    print("已与服务器建立连接")
    while True:
        try:
            socket_data = b''
            while True:
                data = client_socket.recv(10240)
                if data.endswith(b'__end_of_socket__'):
                    socket_data += data[:-len(b'__end_of_socket__')]
                    break
                socket_data += data
            data = eval(socket_data.decode('utf-8'))
            print(f"收到服务器的消息：{data}")
            handle(**data)
        except Exception as e:
            print(e)
            print("与服务器的连接已断开")
            client_socket.close()
            break


def load_and_run_audio():
    while True:
        print("处于待唤醒状态")
        try:
            # # 使用麦克风录制音频
            # with sr.Microphone(sample_rate=8000) as source:
            #     r = sr.Recognizer()
            #     audio_frame = r.listen(source, phrase_time_limit=5)
            #
            # # 使用语音识别器解析音频
            # # result = r.recognize_google(audio_frame, language="zh-CN")
            # result = recognition.main2(audio_frame.frame_data)
            # print("识别结果：", result)
            result = recognition.recognize_from_microphone()
            # 根据指令执行相应的操作
            if "小诺" in result or "想弄" in result or "小鹿" in result or "小洛" in result:
                # 执行您的程序代码
                sys("我在听")
                while True:
                    print("处于已唤醒状态")
                    try:
                        # # 使用麦克风录制音频
                        # with sr.Microphone(sample_rate=8000) as source:
                        #     r = sr.Recognizer()
                        #     audio_frame = r.listen(source, timeout=3)
                        # # 使用语音识别器解析音频
                        # # result = r.recognize_google(audio_frame, language="zh-CN")
                        # result = recognition.main2(audio_frame.frame_data)
                        # print("识别结果：", result)
                        result = recognition.recognize_from_microphone()
                        # 根据指令执行相应的操作
                        if not result.strip():
                            sys("你好像没有说话，试试说小诺小诺唤醒我")
                            break
                        else:
                            output_queue.put((result, False))
                            sys("请稍等")
                            message = {"inputs": result, "state_code": mode}
                            if mode == 2:
                                type_doc = 'PDF' if file_type == '.pdf' else 'PPT'
                                message["type_doc"] = type_doc
                                message["content"] = file_content
                            client_socket.send(str(message).encode("utf-8"))
                            function_finished_flag.clear()
                            function_finished_flag.wait()
                    except:
                        sys("你好像没有说话，试试说小诺小诺唤醒我")
                        break
        except:
            print("无法识别语音")


def dmp_analysis():
    bs_check_c = bs.bs_check_client()
    if bs_check_c.is_file_created_today_with(dmp_addr):
        test = bs.bs_check()
        client_socket.send(str({"inputs": test.analyze('blue_sceen.txt'), 'state_code': 5}).encode('utf-8'))


if __name__ == '__main__':
    server_addr = input('请设置服务器地址，默认为“192.168.137.1”：')
    if not server_addr:
        server_addr = "192.168.137.1"
    dmp_addr = input('请设置dmp文件地址，默认为“C:/Users/Tzu-cheng Chang/Desktop/GLM”：')
    if not dmp_addr:
        dmp_addr = "C:/Users/Tzu-cheng Chang/Desktop/GLM"
    is_audio = input('是否开启语音功能， 默认为“否”：')
    if not is_audio:
        is_audio = "否"
    # 聊天模式为0
    memo = {
        0: "当前为聊天模式",
        1: "当前为回传模式",
        2: "当前为分析模式",
        3: "当前为联网模式",
        4: "当前为功能模式",
        5: "当前为蓝屏模式",
        6: "当前为壁纸模式",
    }
    mode, file_content, file_type, eval_content = 0, '', '', ''
    function_finished_flag = threading.Event()
    # 创建一个显示队列
    output_queue = queue.Queue()
    # 创建套接字F
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务器
    client_socket.connect((server_addr, 8888))
    # 创建线程接收消息
    threading.Thread(target=receive_messages).start()
    threading.Thread(target=dmp_analysis).start()
    # 创建一个线程，用于加载和运行语音识别和合成
    if is_audio == "是":
        threading.Thread(target=load_and_run_audio).start()
    # 启动前端
    uvicorn.run(app, host="127.0.0.1", port=8081)
