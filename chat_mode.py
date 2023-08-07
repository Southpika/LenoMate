import torch
from stop_criterion import StopWordsCriteria
from transformers import StoppingCriteriaList,StoppingCriteria
import re
from utils.web_search import web_searcher

class chat_bot:
    def __init__(self,model,tokenizer) -> None:
        self.tokenizer = tokenizer
        self.model = model
        self.chat_history = ''
        self.pattern = r'<[^>]+>[:：]?'
        self.web_search = web_searcher(web_num=5)
        
    def infer(self,prompt_chat,max_length,stop_words=['<User>','<LenoMate>','<用户>','<Brother>'],temperature=0.9,top_p=0.95):
        
        stop_criteria = StopWordsCriteria(self.tokenizer, stop_words, stream_callback=None)
        with torch.no_grad():
            input_ids = self.tokenizer.encode(prompt_chat, return_tensors='pt').to('cuda')
            out = self.model.generate(
                input_ids=input_ids,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                stopping_criteria = StoppingCriteriaList([stop_criteria])
            )
        return out
    
    def mode0(self,data,conversation=False):
        """
        mode0: 聊天模式
        Args:
            prompt_chat (str): The input of Users
        """
        print("当前为聊天模式...")
        input_statement = data['inputs']
        self.chat_history += f"<用户>:{input_statement}\n<LenoMate>:"            

        if conversation:
            prompt_chat = self.chat_history
            output = self.infer(prompt_chat=prompt_chat, max_length=6000)
            
        else:
            prompt_chat = f"<用户>:{input_statement}\n<LenoMate>:"        
            output = self.infer(prompt_chat=prompt_chat, max_length=1000)
        answer = self.tokenizer.decode(output[0]).split('<LenoMate>:')[-1].strip('\n').strip()
        answer = re.sub(self.pattern,"",answer)
        self.chat_history += f"{answer}\n"
        return {'chat':answer}
    
    def mode2(self,data):
        """
        mode2: 文档模式
        Args:
            data (dict): 需要用到的属性
                inputs:用户问题
                content：文档内容
                type_doc：文档类型
        """
        print("当前为分析模式...")
        query = data['inputs']
        content = data['content']
        type_doc = data['type_doc']
        prompt_chat = f"""基于以下{type_doc}的内容，简洁和专业的来回答用户关于此{type_doc}的问题。
## {type_doc}内容:
{content}
## 问题:
{query}
## 回答：
"""     
        output = self.infer(prompt_chat,max_length=8000,stop_words= ['##'])

        answer = self.tokenizer.decode(output[0]).split('## 回答：')[1]
        return {'chat':answer}

    def mode3(self,data):
        """
        mode3: 联网模式
        Args:
            data (dict): 需要用到的属性
                inputs:用户问题
        """
        print("当前联网模式...")
        query = data['inputs']
        
        web_contents = self.web_search.search_main(query)
        content = ''
        for item in web_contents[1]:
            content += item
            content += '\n'
        print('[网页搜索]',content)
        prompt_chat = f"""基于以下的内容，详细和专业的来回答用户的问题。
## 内容:
{content}
## 问题:
{query}
## 回答：
"""
        output = self.infer(prompt_chat,max_length=8000,stop_words= ['##'])
        answer = self.tokenizer.decode(output[0]).split('## 回答：')[1]
        return {'chat':answer}
  
        

    def mode4(self,input_statement):
        """
        mode4: 功能模式
        Args:
            prompt_chat (str): The input of Users
        """
        print("当前为命令模式...")
        

        