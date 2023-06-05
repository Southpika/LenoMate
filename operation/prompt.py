import pynvml
import screen_brightness_control as sbc
import time
import os
import argparse

class Prompt:
    def fit(self):
        raise NotImplementedError

class Prompt0(Prompt):
    def __init__(self,inp) -> None:
        self.prompt = f"""请你帮我按照instruction的要求提取出关键信息：
##instruction：要求格式为：
- 任务：
- 要求数字（未提及写未知）：
##input：
{inp}
##output:
"""
class Prompt1(Prompt):
    def __init__(self,inp,context) -> None:
        self.prompt = f"""<用户>：请你根据结合以下input内容回答：
{inp}
##input:
{context}
<ChatGLM-6B>：
"""
class Prompt2(Prompt):
    def __init__(self,inp) -> None:
        self.prompt = f"""<用户>：请精简总结以下文本到5个字以内，不要含标点
##input:
{inp}
<ChatGLM-6B>：
"""
class Prompt3(Prompt):
    def __init__(self,inp,context) -> None:
        self.prompt = f"""<用户>：请结合input的软件库帮我找到要打开的软件，输出请写[文件.exe]
##input:
{inp}
<ChatGLM-6B>：
"""
