import pynvml
import screen_brightness_control as sbc
import time
import os
import argparse

class Prompt:
    def fit(self):
        raise NotImplementedError

class Prompt0(Prompt):
    def __init__(self,inp,context) -> None:
        self.prompt = f"""<用户>：假设你可以直接控制电脑，我将给你两个例子，请按照例子的形式进行回答。
例子：
已知电脑当前屏幕亮度为30，用户需要“帮我调高屏幕亮度”，则直接回答“您现在电脑当前亮度为30%，已调至60%”
已知电脑当前屏幕亮度为50，用户需要“帮我调低屏幕亮度”，则直接回答“您现在电脑当前亮度为50%，已调至20%”
问题：已知{context}，用户需求“{inp}”，请模仿"“您现在电脑当前亮度为X%，已调至Y%”"进行回答：
<bot>:"""
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
        self.prompt = f"""基于以下已知信息，简洁和专业的总结以下已知内容到5个字以内，总结中不要含任何标点
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
        
class Prompt4(Prompt):
    def __init__(self,inp,context) -> None:
        # Example
        # context = """电脑当前音量为70"""
        # inp = '帮我调低音量到20'
        self.prompt = f"""<用户>：假设你可以直接控制电脑，我将给你两个例子，请按照例子的形式进行回答。
例子：
已知电脑当前音量为20，用户需要“帮我稍微调低一点音量”，则直接回答“您现在电脑当前音量为20%，已调至10%”
已知电脑当前音量为50，用户需要“帮我稍微调高一点音量”，则直接回答“您现在电脑当前音量为50%，已调至60%”
问题：已知{context}，用户需求“{inp}”，请模仿"“您现在电脑当前音量为X%，已调至Y%”"进行回答：
<bot>:"""




