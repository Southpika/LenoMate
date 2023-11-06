# -*- coding: UTF-8 -*-
import os
import platform
import queue
import re
import socket
import threading
import time
from typing import Dict

import pythoncom
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from audio.speech_synthesis import speech_synthesis as sys

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
    threading.Thread(target=sys, args=("请稍等",)).start()
    message = {"inputs": data.get("userInput"), "state_code": mode}
    if mode == 2:
        type_doc = 'PDF' if file_type == '.pdf' else 'PPT'
        message["type_doc"] = type_doc
        message["content"] = file_content
    client_socket.sendall(str(message).encode("utf-8") + b'__end_of_socket__')


def remove_cached():
    try:
        for file in os.listdir('./svg'):
            if file.endswith('png'):
                os.remove(os.path.join('./svg', file))
        print('Finish cached clean')
    except Exception as e:
        print(e)


@app.post("/text2")  # 切换按钮ge
def text2(data: Dict):
    global mode
    mode = data["switch"]
    print(mode)
    res = memo[mode]
    remove_cached()
    threading.Thread(target=sys, args=(res,)).start()
    return res


def get_basecount():
    base_count = 0
    for file in os.listdir('./svg'):
        if file.endswith('png'):
            # print(file)
            base_count += 1
    return base_count


@app.post("/audio")  # 显示server返回消息
def audio(data: Dict):
    data, bot = output_queue.get()
    image_num = get_basecount() + 1
    image_filename = "svg/{image_num}.png"
    images_path = []
    if 'image' in data.keys():
        for image_io in data['image']:
            with open(image_filename.format(image_num=image_num), 'wb') as file:
                file.write(image_io)
                images_path.append(image_filename.format(image_num=image_num))
            image_num += 1
        # images_path:"["svg/1.png","svg/2.png","svg/3.png","svg/4.png"]"
        # print(images_path)
        threading.Thread(target=flag_join).start()
        return JSONResponse(content={"location": images_path, "bot": bot})
    else:
        result = data['chat']
        sentences = re.split(r'[.!?。！？]', result)
        sentences.pop()
        global last_audio
        n, m = len(last_audio), len(sentences)
        if n < m:
            for i in range(n, m):
                print(f'put: {sentences[i]}')
                audio_queue.put(sentences[i])
            last_audio = sentences
        if 'end' in data:
            last_audio = []
            threading.Thread(target=flag_join).start()
        if 'follow' in data:
            return JSONResponse(content={"result": result.strip('\n'), "bot": bot, "follow": data['follow']})
        else:
            return JSONResponse(content={"result": result.strip('\n'), "bot": bot})


def flag_join():
    audio_queue.join()
    function_finished_flag.set()


@app.post("/image")
def wallpaper_set(data: Dict):
    from utils.wallpaper import main
    # data
    path = data['wall_path'].replace('http://localhost:8081/', '')
    # print(os.path.join(root_path, path))
    main(os.path.join(root_path, path))


def evaluate(content):
    global eval_content
    pythoncom.CoInitialize()
    eval_content = eval(content)
    pythoncom.CoUninitialize()


def handle(**kwargs):
    if "command" in kwargs.keys():
        # temp = subprocess.check_output(kwargs["command"], shell=True)
        # temp = eval(kwargs["command"])
        # 勿删，功能模式eval
        eval_thred = threading.Thread(target=evaluate, args=(kwargs["command"],))
        eval_thred.start()
        eval_thred.join()
        global eval_content
        if "chat" not in kwargs.keys():
            client_socket.sendall(str({"inputs": eval_content, "state_code": 1}).encode("utf-8") + b'__end_of_socket__')
    if "chat" in kwargs.keys():
        # kwargs['location'] = r"svg/2.png" #测试用
        output_queue.put((kwargs, True))
    elif 'image' in kwargs.keys():
        # print(kwargs)
        output_queue.put((kwargs, True))


def receive_messages():
    print("已与服务器建立连接")
    system = platform.system()
    client_socket.sendall(str(system).encode("utf-8"))
    while True:
        try:
            socket_data = b''
            while True:
                data = client_socket.recv(10240)
                if data.endswith(b'__end_of_socket__'):
                    socket_data += data[:-len(b'__end_of_socket__')]
                    break
                socket_data += data
            socket_data = socket_data.split(b'__end_of_socket__')[-1]
            data = eval(socket_data.decode('utf-8'))
            if 'image' not in data:
                if 'end' in data:
                    print(f"收到服务器的消息：{data}")
            else:
                print(f"图片收取中...")
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
            result = recognition.recognize_from_microphone()
            # 根据指令执行相应的操作
            if "小诺" in result or "想弄" in result or "小鹿" in result or "小洛" in result or "小娜" in result:
                # 执行您的程序代码
                sys("我在听")
                while True:
                    print("处于已唤醒状态")
                    try:
                        result = recognition.recognize_from_microphone()
                        # 根据指令执行相应的操作
                        if not result.strip():
                            sys("你好像没有说话，试试说小诺小诺唤醒我")
                            break
                        else:
                            output_queue.put(({"chat": result}, False))
                            sys("请稍等")
                            message = {"inputs": result, "state_code": mode}
                            if mode == 2:
                                type_doc = 'PDF' if file_type == '.pdf' else 'PPT'
                                message["type_doc"] = type_doc
                                message["content"] = file_content
                            client_socket.sendall(str(message).encode("utf-8") + b'__end_of_socket__')
                            function_finished_flag.clear()
                            function_finished_flag.wait()
                    except:
                        sys("你好像没有说话，试试说小诺小诺唤醒我")
                        break
        except:
            print("无法识别语音")


def load_and_run_sys():
    while True:
        sentence = audio_queue.get()
        print(f'get: {sentence}')
        sys(sentence)


def load_and_run_email():
    while True:
        email = tzh.get_email()
        print(f'已收到邮件信息：{email}')
        if email:
            global history
            if email != history:
                print(f'已发送邮件信息：{email}')
                client_socket.sendall(str({"inputs": email, "state_code": 7}).encode("utf-8") + b'__end_of_socket__')
                history = email
        time.sleep(6)


def dmp_analysis():
    bs_check_c = bs.bs_check_client()
    if bs_check_c.is_file_created_today_with(dmp_addr):
        test = bs.bs_check()
        client_socket.sendall(
            str({"inputs": test.analyze('blue_sceen.txt'), 'state_code': 5}).encode('utf-8') + b'__end_of_socket__')


if __name__ == '__main__':
    server_addr_default = "n81595194d.zicp.fun"
    server_port_default = 13964
    dmp_addr_default = "C:/Users/Tzu-cheng Chang/Desktop/GLM"
    IMAP_SERVER_default = 'imap.qq.com'
    EMAIL_ADDRESS_default = '513923576@qq.com'
    EMAIL_PASSWORD_default = 'wektfdfmtxcgbgce'
    server_addr = input(f'请设置服务器地址，默认为{server_addr_default}：')
    server_port = input(f'请设置服务器端口，默认为{server_port_default}：')
    dmp_addr = input(f'请设置dmp文件地址，默认为{dmp_addr_default}：')
    IMAP_SERVER = input(f'请设置邮件服务器，默认为{IMAP_SERVER_default}：')
    EMAIL_ADDRESS = input(f'请设置邮件地址，默认为{EMAIL_ADDRESS_default}：')
    EMAIL_PASSWORD = input(f'请设置邮件验证码，默认为{len(EMAIL_PASSWORD_default) * "*"}：')
    mode_select = input('请选择要打开的模式， 默认为 0 1 2 3 (0：聊天 1：功能 2：文件分析 3：壁纸 4: 语音)')
    if not server_addr:
        server_addr = server_addr_default
    if not server_port:
        server_port = server_port_default
    if not dmp_addr:
        dmp_addr = dmp_addr_default
    if not IMAP_SERVER:
        IMAP_SERVER = IMAP_SERVER_default
    if not EMAIL_PASSWORD:
        EMAIL_PASSWORD = EMAIL_PASSWORD_default
    if not EMAIL_ADDRESS:
        EMAIL_ADDRESS = EMAIL_ADDRESS_default
    if not mode_select:
        mode_select = [0, 1, 2, 3]
    else:
        mode_select = list(map(int, mode_select.split()))
    # 聊天模式为0
    if 1 in mode_select:
        import utils.blue_screen as bs
        from utils.email_get import email_reciever

        tzh = email_reciever(EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER)
        history = ''
        #  勿删，功能模式使用
        import operation
    if 2 in mode_select:
        import operation.read_file as rd
    if 4 in mode_select:
        import audio.speech_recognition as recognition

        threading.Thread(target=load_and_run_audio).start()
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
    last_audio = []
    # 创建一个显示队列
    output_queue = queue.Queue()
    audio_queue = queue.Queue()
    # 创建套接字F
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务器
    client_socket.connect((server_addr, int(server_port)))
    # 创建线程接收消息
    threading.Thread(target=load_and_run_email).start()
    threading.Thread(target=dmp_analysis).start()
    threading.Thread(target=load_and_run_sys).start()
    threading.Thread(target=receive_messages).start()
    # 启动前端
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level='warning')
