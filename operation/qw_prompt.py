## 修改prompt后记得修改max_length以及split的部分
class Prompt:
    def __init__(self):
        self.prompt_template = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{QUERY}<|im_end|>\n<|im_start|>assistant\n"


class Prompt0(Prompt):
    def fit(self, inp, context) -> None:
        query = "Please provide an answer in the required format based on the known information.\n\n\nInfomation:{CONTEXTS}\nInput:如果用户需要“{INPUTS}”，模仿“您现在电脑当前亮度为X%，已调至Y%”进行回答\nOutput:"
        query = query.format(CONTEXTS = context, INPUTS = inp)


class Prompt1(Prompt):
    def __init__(self, inp, context) -> None:
        self.prompt = f"""基于以下已知信息，简洁和专业的来回答用户的问题。
如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
##已知内容:
{context}
##问题:
{inp}
##回答："""


class Prompt2(Prompt):
    def __init__(self, inp) -> None:
        self.prompt = f"""基于以下已知信息，简洁和专业的总结以下已知内容到5个字以内，总结中不要含任何标点
##已知内容:
{inp}
##总结："""


class Prompt3(Prompt):
    def __init__(self, inp, context) -> None:
        self.prompt = f"""<用户>：请结合input的软件库帮我找到要打开的软件，输出请写[文件.exe]
##input:
{inp}
<ChatGLM-6B>：
"""


class Prompt4(Prompt):
    def __init__(self, inp, context) -> None:

        # context = """电脑当前音量为70"""
        # inp = '帮我调低音量到20'
        self.prompt = f"""现在我给你一道简单的数学题，请你精准的回答一个数字。
##例子：
已知电脑当前音量为20%，用户需要“帮我调高音量”，则直接回答“您现在电脑当前音量为20%，已调至40%”
已知电脑当前音量为80%，用户需要“帮我调低音量”，则直接回答“您现在电脑当前音量为80%，已调至50%”
已知电脑当前音量为40%，用户需要“帮我调低音量到30%”，则直接回答“您现在电脑当前音量为40%，已调至30%”
##问题：
已知{inp}，用户需要“{context}”，请模仿"“您现在电脑当前音量为X%，已调至Y%”"进行回答：
##回答："""
#         self.prompt = f"""假设你可以直接控制电脑音量，我将给你几个例子，请按照例子的形式进行回答，如果没有指定数字请按照要求自己联想数字进行回答，如果指定了数字，直接按用户的数字回答。
# ##例子：
# 已知电脑当前音量为20，用户需要“帮我调高音量”，则直接回答“您现在电脑当前音量为20，已调至40”
# 已知电脑当前音量为80，用户需要“帮我调低音量”，则直接回答“您现在电脑当前音量为80，已调至50”
# 已知电脑当前音量为40，用户需要“帮我调低音量到30”，则直接回答“您现在电脑当前音量为40，已调至30”
# ##问题：
# 已知{inp}，用户需要“{context}”，请模仿"“您现在电脑当前音量为X，已调至Y”"进行回答：
# ##回答："""

class ImagePrompt(Prompt):
    def fit(self, inp) -> None:    
        image_prompt = "Give a brief description of the image to generate a drawing prompt in English(No More Than 30 words, noun phrases).\nInput: {DESCRIPTION}\nOutput:"
        query = image_prompt.format(DESCRIPTION = inp)
        self.prompt = self.prompt_template.format(QUERY = query)

