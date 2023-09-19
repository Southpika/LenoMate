import sys
import os
# print(os.path.dirname(os.path.abspath('__file__')))
sys.path.append(os.path.dirname(os.path.abspath('__file__')))
import torch
from utils.glm.stop_criterion import StopWordsCriteria
from transformers import StoppingCriteriaList,StoppingCriteria
import re
from utils.web_search import web_searcher
from utils.search_doc_faiss import faiss_corpus
import operation.prompt as prompt
import operation.operation_server_glm as operation

class chat_bot:
    def __init__(self,model,tokenizer) -> None:
        self.tokenizer = tokenizer
        self.model = model
        self.chat_history = ''
        self.pattern = r'<[^>]+>[:：]?'
        self.web_search = web_searcher(web_num=5)
        
    def chat(self,prompt_chat,max_length,stop_words=['<User>','<LenoMate>','<用户>','<Brother>'],temperature=0.9,top_p=0.95):
        
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
            output = self.chat(prompt_chat=prompt_chat, max_length=6000)
            
        else:
            prompt_chat = f"<用户>:{input_statement}\n<LenoMate>:"   
            # print(prompt_chat)     
            output = self.chat(prompt_chat=prompt_chat, max_length=1000)
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
        output = self.chat(prompt_chat,max_length=8000,stop_words= ['##'])

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
        output = self.chat(prompt_chat,max_length=8000,stop_words= ['##'])
        answer = self.tokenizer.decode(output[0]).split('## 回答：')[1]
        return {'chat':answer}
  
        

    def mode4(self,input_statement):
        """
        mode4: 功能模式
        Args:
            prompt_chat (str): The input of Users
        """
        print("当前为命令模式...")

    def mode5(self,data):
        """
        mode5: 蓝屏分析模式
        Args:
            data (dict): 需要用到的属性
                inputs:用户问题
        """
        print("当前蓝屏分析模式...")
        context = data['inputs']
        
        prompt_chat = f"""基于以下BUG分析文档的内容，详细和专业的来回答用户关于此文档的问题。
## 内容:
{context}
## 问题:
请帮我总结分析一下这次的蓝屏信息。
## 回答：
"""
        output = self.chat(prompt_chat,max_length=8000,stop_words= ['##'])
        answer = self.tokenizer.decode(output[0]).split('## 回答：')[1]
        
        answer = '发现您今天发生了蓝屏' + answer
        return {'chat':answer}

    def mode6(self,data):
        """
        mode6: 壁纸模式
        Args:
            data (dict): 需要用到的属性
            inputs:用户问题
        """
        # from utils.wallpaper_generate import sdmodels
        # from utils.wallpaper_generate import args as wallpaper_args
        # sd = sdmodels(wallpaper_args)
        print("当前壁纸模式...")
#         context = data['inputs']
        
#         prompt_chat = f"""<用户>：现在我给你一句话，请你用英语提取出中间的实体。
# ##句子：
# {context}
# <LenoMate>："""
#         output = self.infer(prompt_chat,max_length=8000)
#         answer = self.tokenizer.decode(output[0]).split('<LenoMate>：')[1]
#         pic_path = sd.inference(answer)
        path = r"C:\Users\admin\Desktop\sd\sd_tzh\outputs\txt2img-samples\samples\00112.png"
        with open(path, 'rb') as file:
            image_data = file.read()
        # 发送图像数据给客户端
        return {'image':image_data}
    
class operation_bot():
    def __init__(self,model,tokenizer,model_sim,tokenizer_sim,corpus) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.model_sim = model_sim
        self.tokenizer_sim = tokenizer_sim
        self.corpus = corpus
    
    def fit(self,data):
        # self.input_statement = data['inputs']
        print("当前为命令模式...")
                
        if data['state_code'] == 4:
            self.input_statement = data['inputs']
            # if not data_client['mode']:
            # try:
            self.selected_idx, score = self.corpus.search(query=self.input_statement, verbose=True)
            if self.selected_idx in [0,1,4,5]:
                command = f"operation.operation_client.Operation{self.selected_idx}().fit()"
                client_data = {}
                client_data['command']=command
                client_data['state_code']=1
                return client_data         
            else:
                opt = eval(f"operation.Operation{self.selected_idx}")(self.input_statement)
                if self.selected_idx == 3:
                    result = opt.fit(self.model_sim,self.tokenizer_sim)
                else:
                    result = opt.fit(self.model, self.tokenizer) 
                return result
            
        elif data['state_code'] == 1:
            context = data['inputs']
            
            torch.cuda.empty_cache()
            if self.selected_idx in [5,0]:
                opt = eval(f"operation.Operation{self.selected_idx}")(self.input_statement,context,self.model_sim,self.tokenizer_sim)
            else:
                opt = eval(f"operation.Operation{self.selected_idx}")(self.input_statement,context)
            result = opt.fit(self.model, self.tokenizer)
            return result
        
        elif data['state_code'] == 6:

            path = r"C:\Users\admin\Desktop\sd\sd_tzh\outputs\txt2img-samples\samples\00112.png"
            with open(path, 'rb') as file:
                image_data = file.read()
            # 发送图像数据给客户端
            return {'image':image_data}

            
            
                


        

        