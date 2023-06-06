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
        self.prompt = f"""基于以下已知信息，简洁和专业的来回答用户的问题。
如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
##已知内容:
{context}
##问题:
{inp}
##回答："""

class Prompt2(Prompt):
    def __init__(self,inp) -> None:
        self.prompt = f"""基于以下已知信息，简洁和专业的总结以下文本到5个字以内，总结中不要含任何标点
##已知内容:
{inp}
##总结："""
class Prompt3(Prompt):
    def __init__(self,inp,context) -> None:
        self.prompt = f"""<用户>：请结合input的软件库帮我找到要打开的软件，输出请写[文件.exe]
##input:
{inp}
<ChatGLM-6B>：
"""
