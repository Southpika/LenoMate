# -*- coding: UTF-8 -*-
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse,JSONResponse
import audio.play as play
import audio.synthesis as synthesis
import audio.recognition as recognition
import torch
from transformers import AutoTokenizer, AutoModel
from utils.search_doc_faiss import faiss_corpus
import threading
import queue
import speech_recognition as sr
from typing import Dict

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许进行跨域请求的来源列表，*作为通配符
    allow_credentials=True,  # 跨域请求支持cookie，默认为否
    allow_methods=["*"],  # 允许跨域请求的HTTP方法
    allow_headers=["*"],  # 允许跨域请求的HTTP头列表
)
app.add_middleware(GZipMiddleware)

mode = True  # 聊天为True


def load_and_run_model():
    print("模型加载中...")
    # model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    
    model = AutoModel.from_pretrained(r"C:\Users\89721\Desktop\models--THUDM--chatglm2-6b-int4", trust_remote_code=True).cuda()
    # model = AutoModel.from_pretrained(r"C:\Users\Opti7080\Desktop\models--THUDM--chatglm-6b", trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained(r"C:\Users\89721\Desktop\models--THUDM--chatglm2-6b-int4", trust_remote_code=True)
    model_sim =  AutoModel.from_pretrained("GanymedeNil/text2vec-large-chinese").to('cuda')
    tokenizer_sim = AutoTokenizer.from_pretrained("GanymedeNil/text2vec-large-chinese")
    corpus = faiss_corpus(model = model_sim, tokenizer=tokenizer_sim)
    print("模型加载完成")

    while True:
        input_statement, switch = input_queue.get()
        if not mode:
            print("当前为命令模式...")
            try:
                selected_idx, score = corpus.search(query=input_statement, verbose=True)
                torch.cuda.empty_cache()
                if selected_idx == 5:
                    opt = eval(f"operation.Operation{selected_idx}")(input_statement,model_sim,tokenizer_sim)
                else:
                    opt = eval(f"operation.Operation{selected_idx}")(input_statement)
                result = opt.fit(model, tokenizer)
                if switch:
                    output_queue.put((result, True))
                    sys(result)
                else:
                    output_queue2.put(result)
                print("模型输出：", result)
            except Exception as e:
                print('#' * 50)
                print('error info', e)
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
                    max_length=300,
                    temperature=0.9,
                    top_p=0.95,
                )
            answer = tokenizer.decode(out[0]).split('<ChatGLM-6B>：')[1].strip('\n').strip()
            if switch:
                output_queue.put((answer, True))
                sys(answer)
            else:
                output_queue2.put(answer)


def load_and_run_audio():
    while True:
        print("处于待唤醒状态")
        try:
            # 使用麦克风录制音频
            with sr.Microphone(sample_rate=8000) as source:
                r = sr.Recognizer()
                audio_frame = r.listen(source)

            # 使用语音识别器解析音频
            # result = r.recognize_google(audio, language="zh-CN")
            result = recognition.main2(audio_frame.frame_data)
            print("识别结果：", result)

            # 根据指令执行相应的操作
            if "小诺" in result or "想诺" in result:
                # 执行您的程序代码
                sys("我在听")
                while True:
                    print("处于已唤醒状态")
                    try:
                        # 使用麦克风录制音频
                        with sr.Microphone(sample_rate=8000) as source:
                            r = sr.Recognizer()
                            audio_frame = r.listen(source, 3)
                        # 使用语音识别器解析音频
                        # result = r.recognize_google(audio, language="zh-CN")
                        result = recognition.main2(audio_frame.frame_data)
                        print("识别结果：", result)

                        # 根据指令执行相应的操作
                        if not result.strip():
                            sys("你好像没有说话，试试说小诺小诺唤醒我")
                            break
                        else:
                            output_queue.put((result, False))
                            input_queue.put((result, False))
                            sys("请稍等")
                            temp = output_queue2.get()
                            output_queue.put((temp, True))
                            print(output_queue.queue)
                            sys(temp)


                    except sr.RequestError as e:
                        print("无法连接", str(e))
                        sys("你好像没有说话，试试说小诺小诺唤醒我")
                        break
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        sys("你好像没有说话，试试说小诺小诺唤醒我")
                        break

        except sr.RequestError as e:
            print("无法连接", str(e))
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            print("无法识别语音。")


# 创建一个输入队列
input_queue = queue.Queue()
output_queue = queue.Queue()
output_queue2 = queue.Queue()
# 创建一个线程，用于加载和运行模型
model_thread = threading.Thread(target=load_and_run_model)
model_thread2 = threading.Thread(target=load_and_run_audio)
model_thread.daemon = model_thread2.daemon = True
# 启动线程
model_thread.start()
model_thread2.start()


@app.get("/")
def start():
    with open("QA.html", encoding="utf-8") as file:
        html_content = file.read()
    thred = threading.Thread(target=sys, args=("你好，我是LenoMate，可以叫我小诺，请问有什么可以帮您？",))
    thred.start()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/text")
def text(data: Dict):
    thred = threading.Thread(target=sys, args=("请稍等",))
    thred.start()
    input_queue.put((data.get("userInput"), True))


@app.post("/text2")  # 切换按钮
def text2(data: Dict):
    global mode
    mode = not mode
    res = '当前为聊天模式' if mode else '当前为功能模式'
    thred = threading.Thread(target=sys, args=(res,))
    thred.start()
    return res


def sys(result):
    synthesis.main(result)
    play.play()


@app.post("/audio")
def audio(data: Dict):
    result, bot = output_queue.get()
    print(output_queue.queue)
    return JSONResponse(content={"result": result, "bot": bot})


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8081)
