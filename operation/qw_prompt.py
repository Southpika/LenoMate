## 修改prompt后记得修改max_length以及split的部分
class Prompt:
    def __init__(self):
        self.prompt_template = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{QUERY}<|im_end|>\n<|im_start|>assistant\n"


class Prompt0(Prompt):
    def __init__(self, inp, context) -> None:
        super().__init__()
        query = "Please provide an answer in the required format based on the known information.\n\nInfomation:{CONTEXTS}\n\nInput:如果用户需要“{INPUTS}”，模仿“现在电脑当前亮度为X%，已调至Y%”的样式进行回答。"
        self.prompt = self.prompt_template.format(QUERY = query.format(CONTEXTS = context, INPUTS = inp))


class Prompt1(Prompt):
    def __init__(self, inp, context) -> None:
        super().__init__()
        query = f"""Based on the following known information, please answer the user's question in a concise and professional manner. If there is no answer, please say "According to the known information, it is impossible to answer this question" or "Insufficient information is provided." It is not allowed to add fabricated content in the answer. The answer should be in Chinese.

Information:
{context}

Question:
{inp}
Output:"""
        self.prompt = self.prompt_template.format(QUERY = query)

class Prompt2(Prompt):
    def __init__(self, inp) -> None:
        self.prompt = f"""基于以下已知信息，简洁和专业的总结以下已知内容到5个字以内，总结中不要含任何标点
##已知内容:
{inp}
##总结："""




class Prompt5(Prompt):
    def __init__(self, inp, context) -> None:
        super().__init__()
        query = "Please provide an answer in the required format based on the known information.\n\nInfomation:{CONTEXTS}\n\nInput:如果用户需要“{INPUTS}”，模仿“现在电脑当前音量为X%，已调至Y%”的样式进行回答。"
        self.prompt = self.prompt_template.format(QUERY = query.format(CONTEXTS = context, INPUTS = inp))

class Prompt6(Prompt):
    def __init__(self, inp) -> None:
        super().__init__()
        query = "你是LenoMate，用户的私人助理，请以助理的口吻亲切、简洁地提醒用户邮件的内容（以和用户聊天的形式总结邮件内容）。\n\nInput:\n {DESCRIPTION}.\n\nOutput(Answer in Chinese):"
        self.prompt = self.prompt_template.format(QUERY = query.format(DESCRIPTION = inp))

class ImagePrompt(Prompt):    
    def __init__(self, inp) -> None:    
        super().__init__()
        image_prompt = "Give a brief description of the image to generate a drawing prompt in English(No More Than 30 words, noun phrases).\nInput: {DESCRIPTION}\nOutput:"
        query = image_prompt.format(DESCRIPTION = inp)
        self.prompt = self.prompt_template.format(QUERY = query)

if __name__ == '__main__':
    test = Prompt0(inp='用户需要屏幕亮度调到最大',context='电脑当前亮度为30')
    print(test.prompt)