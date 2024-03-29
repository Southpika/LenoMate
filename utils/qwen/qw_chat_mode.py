"""
File_name: qw_chat_mode.py
author: tanzhehao
version: /

Overview:
此Python文件为对话模型和操作模型的实际操作层。通过`LenoMate`类，初始化和管理各种模型和组件以及处理不同模式的客户端请求。

Notes:
- operation bot的mode数字源于模型匹配，如果需要加入新的操作类功能，先需更新 data/document_corpus.txt 此文件中的modex的x需与此txt文件的index匹配，同时还需要更新faiss向量库
- chat bot主要为文字类内容，除了operation bot的功能全部在此之下，modeX的X数字参照state code，在lenomate.py中调用
- statecode为1用于处理需要回传的内容，比如调节屏幕亮度需要先获取用户当前屏幕亮度
"""

import sys,os,torch,re,argparse
# print(os.path.dirname(os.path.abspath('__file__')))
sys.path.append(os.path.dirname(os.path.abspath('__file__')))
from utils.qwen.stop_criterion import StopWordsLogitsProcessor
from utils.vol_select import judge
from typing import TYPE_CHECKING, Optional, Tuple, Union, Callable, List, Any, Generator
from utils.web_search import web_searcher
import operation.qw_prompt as prompt
import operation.operation_server_qw as operation
from transformers.generation import GenerationConfig
from operation.open_app import search_tool
import numpy as np
from transformers.generation import LogitsProcessor,LogitsProcessorList

def make_context(
    tokenizer,
    query: str,
    history,
    system: str = "",
    max_window_size: int = 6144,
    chat_format: str = "chatml",
):
    if history is None:
        history = []

    if chat_format == "chatml":
        im_start, im_end = "<|im_start|>", "<|im_end|>"
        im_start_tokens = [tokenizer.im_start_id]
        im_end_tokens = [tokenizer.im_end_id]
        nl_tokens = tokenizer.encode("\n")

        def _tokenize_str(role, content):
            return f"{role}\n{content}", tokenizer.encode(
                role, allowed_special=set()
            ) + nl_tokens + tokenizer.encode(content, allowed_special=set())

        system_text, system_tokens_part = _tokenize_str("system", system)
        system_tokens = im_start_tokens + system_tokens_part + im_end_tokens

        raw_text = ""
        context_tokens = []

        for turn_query, turn_response in reversed(history):
            query_text, query_tokens_part = _tokenize_str("user", turn_query)
            query_tokens = im_start_tokens + query_tokens_part + im_end_tokens
            response_text, response_tokens_part = _tokenize_str(
                "assistant", turn_response
            )
            response_tokens = im_start_tokens + response_tokens_part + im_end_tokens

            next_context_tokens = nl_tokens + query_tokens + nl_tokens + response_tokens
            prev_chat = (
                f"\n{im_start}{query_text}{im_end}\n{im_start}{response_text}{im_end}"
            )

            current_context_size = (
                len(system_tokens) + len(next_context_tokens) + len(context_tokens)
            )
            if current_context_size < max_window_size:
                context_tokens = next_context_tokens + context_tokens
                raw_text = prev_chat + raw_text
            else:
                break

        context_tokens = system_tokens + context_tokens
        raw_text = f"{im_start}{system_text}{im_end}" + raw_text
        context_tokens += (
            nl_tokens
            + im_start_tokens
            + _tokenize_str("user", query)[1]
            + im_end_tokens
            + nl_tokens
            + im_start_tokens
            + tokenizer.encode("assistant")
            + nl_tokens
        )
        raw_text += f"\n{im_start}user\n{query}{im_end}\n{im_start}assistant\n"

    elif chat_format == "raw":
        raw_text = query
        context_tokens = tokenizer.encode(raw_text)
    else:
        raise NotImplementedError(f"Unknown chat format {chat_format!r}")

    return raw_text, context_tokens

class chat_bot:
    def __init__(self,model,tokenizer,generation_config) -> None:
        self.tokenizer = tokenizer
        self.model = model

        self.web_search = web_searcher(web_num=3)
        self.roles = {"user": "<|im_start|>user", "assistant": "<|im_start|>assistant"}
        self.im_start = self.tokenizer.im_start_id
        self.im_end = self.tokenizer.im_end_id
        self.nl_tokens = self.tokenizer('\n').input_ids
        _system = self.tokenizer('system').input_ids + self.nl_tokens
        self.system_message: str = "You are a helpful assistant named LenoMate from Lenovo."
        self.history = []
        self.generation_config = generation_config
        self.history_doc = []
        self.file_content = None
        self.history_web = []
        stop_words_ids = [[self.tokenizer.im_end_id], [self.tokenizer.im_start_id]]

        if stop_words_ids is not None:
            self.stop_words_logits_processor = StopWordsLogitsProcessor(
                stop_words_ids=stop_words_ids,
                eos_token_id=generation_config.eos_token_id,
            )

    def chat(self,
             query,
             generation_config: Optional[GenerationConfig],
             history=None,
            ):
        if history is None:
            history = []
        
        prompts,input_ids = make_context(
            self.tokenizer,
            query = query,
            history = history,
            system = self.system_message,
            max_window_size = generation_config.max_window_size,
            chat_format=generation_config.chat_format,
        )
        # input_ids = self.tokenizer(
        #     prompts, return_tensors="pt", add_special_tokens=False
        # ).input_ids.to("cuda:0")
        logits_processor = LogitsProcessorList([self.stop_words_logits_processor])
        input_ids = torch.tensor([input_ids]).to('cuda')
        response_ids = self.model.generate(
                                    input_ids,
                                    # seed = -1,
                                    generation_config = generation_config,
                                    do_stream=False,
                                    logits_processor=logits_processor,    
                                    )
        self.im_end = self.tokenizer.im_end_id
        for eod_token_idx in range(len(input_ids[0]), len(response_ids[0])):
            if response_ids[0][eod_token_idx] in [self.im_start, self.im_end]:
                self.end_reason = f"Gen {self.tokenizer.decode([response_ids[0][eod_token_idx]])!r}"
                break
        response = self.tokenizer.decode(response_ids[0][:eod_token_idx])[len(prompts):]
        history.append((query, response))
        return response, history

    def chat_stream(self,
             query,
             generation_config: Optional[GenerationConfig],
             history=None,
            ):
        if history is None:
            history = []

        logits_processor = LogitsProcessorList([self.stop_words_logits_processor])
        prompts,input_ids = make_context(
            self.tokenizer,
            query = query,
            history = history,
            system = self.system_message,
            max_window_size = generation_config.max_window_size,
            chat_format=generation_config.chat_format,
        )
        # print(prompts)
        input_ids = torch.tensor([input_ids]).to('cuda')
        generator = self.model.generate(
                                    input_ids,
                                    seed = -1,
                                    do_sample=True,
                                    generation_config = generation_config,
                                    logits_processor=logits_processor,    
                                    )
        outputs = []
        for token in generator:
            
            outputs.append(token.item())
            word = self.tokenizer.decode(outputs,skip_special_tokens=True,errors='ignore')
            new_history = history + [(query,word)]
            yield word, new_history

    def mode0(self,data,history):
        """
        mode0: 聊天模式
        Args:
            prompt_chat (str): The input of Users
        """
        print("当前为聊天模式...")
        self.system_message: str = "You are a helpful assistant named LenoMate from Lenovo."
        response = self.chat_stream(data['inputs'], self.generation_config, history = history)
        return {'chat':response}
    
    def mode2(self,data,history):
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
        self.system_message = f"You are a helpful file analysis assistant. Please answer the user's question based on the following {data['type_doc']} document."
        if self.file_content != data['content']:
            self.file_content = data['content']
            
            REACT_PROMPT = """Answer the following questions as best and brief as you can. You have access to the {filetype} file.:

Document:
{content}

Question: {query}"""
            print(REACT_PROMPT.format(filetype = data['type_doc'], content = self.file_content, query = query))
        
            response = self.chat_stream(REACT_PROMPT.format(filetype = data['type_doc'], content = self.file_content, query = query),self.generation_config,history = history)
        else:
            response = self.chat_stream(query,self.generation_config,history = history)
        return {'chat':response}


    def mode3(self,data,history):
        """
        mode3: 联网模式
        Args:
            data (dict): 需要用到的属性
                inputs:用户问题
        """
        print("当前联网模式...")
        query = data['inputs']
        search_prompt = "Give a brief search prompt in Chinese according to the input and history.\nHistory: {History}\n\nInput: {DESCRIPTION}\nOutput:"
        search_query = self.chat(search_prompt.format(DESCRIPTION=query,History = None),self.generation_config,history=None)[0].strip().strip('"')
        self.system_message: str = "You are a helpful assistant."
        web_contents = self.web_search.search_main(search_query)
        content = ''
        for item in web_contents[1]:
            if item != "None":
                content += item
                content += '\n'
        
        print('[网页搜索]',content)
        print('='*50)
        # self.system_message = f"<|im_start|>system\nYou are a helpful file analysis assistant.Please answer the user's question based on the following text.\nDocument:{content}\n<|im_end|>\n<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n"
        REACT_PROMPT = """Answer the following questions as best and brief as you can. You have access to the following resources:

Resources:    
{documents}

Question: {query}"""
        answer = self.chat_stream(REACT_PROMPT.format(documents=content,query=query),self.generation_config,history = history)
       
        return {'chat':answer}

    def mode5(self,data,history):
        """
        mode5: 蓝屏分析模式
        Args:
            data (dict):
            需要用到的属性
                inputs:用户问题
        """
        print("当前蓝屏分析模式...")
        context = data['inputs']
        
        REACT_PROMPT = f"""Answer the following questions as best you can. You have access to the following documents about BUG ANALYSIS DOCUMENTATION:

BUG ANALYSIS DOCUMENTATION:
{context}

Question: Please summarize the blue screen bug analysis."""
        
        answer = self.chat_stream(REACT_PROMPT.format(context=context),self.generation_config,history = None)
        
        
        return {'chat':answer}
    
    def mode7(self,data,history):
        """
        mode7: 邮件分析模式
        Args:
            data (dict): 
            需要用到的属性
            inputs:邮件内容
        """
        prompt_email = prompt.Prompt7(data['inputs']).prompt
        answer = self.chat_stream(prompt_email, self.generation_config, history = None)
        return {'chat':answer}

import operation.qw_prompt as prompt
class operation_bot(chat_bot):
    def __init__(self,model,tokenizer,model_sim,tokenizer_sim,corpus,generation_config,sdmodel) -> None:
        super().__init__(model,tokenizer,generation_config)
        self.model_sim = model_sim
        self.tokenizer_sim = tokenizer_sim
        self.corpus = corpus
        self.system_message: str = "You are a helpful assistant."
        self.sdmodel = sdmodel
        
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
                # opt = eval(f"operation.Operation{self.selected_idx}")(self.input_statement)
                if self.selected_idx == 3:
                    result = eval(f"self.opr{self.selected_idx}")(self.input_statement)
                else:
                    result = eval(f"self.opr{self.selected_idx}")(self.input_statement) 
                return result
            
        elif data['state_code'] == 1:
            context = data['inputs']
            
            torch.cuda.empty_cache()
            if self.selected_idx in [5]:
                
                
                result = eval(f"self.opr{self.selected_idx}")(self.input_statement,context,self.model_sim,self.tokenizer_sim)
                
            else:
                
                result = eval(f"self.opr{self.selected_idx}")(self.input_statement,context)
            
            return result

        elif data['state_code'] == 6:
            
            prompt_img = prompt.ImagePrompt(data['inputs']).prompt
            prompt_img,_ = self.chat(prompt_img, self.generation_config, history = [])
            
            paths = self.sdmodel.inference(prompt_img)
            image_list = []
            for path in paths:
                with open(path, 'rb') as file:
                    image_data = file.read()
                    image_list.append(image_data)
                # 发送图像数据给客户端
            return {'image':image_list}


        
    def opr0(self,input_statement,context):
        # 屏幕亮度
        self._extract_info(prompt.Prompt0(input_statement, context).prompt)

        res = {
            # 'chat':self.answer,
            'chat':f"Have already turned to {self.num}",
            'state_code':0,
            'command':f"operation.screen_brightness.operation({self.num}).fit()"
        }
        print(f"[亮度调节]:{self.answer}")
        return res

    def opr2(self,input_statement,context):
        pass  

    def opr5(self,input_statement,context,model_sim,tokenizer_sim):
        # 音量
        
        
        selected = judge(input_statement,model_sim,tokenizer_sim)
        if selected == '静音':
            output = {
                'command':"operation.volumn_control.vol_ctrl().mute_all()",
                # 'chat':'已静音',
                'chat':'Your system have been mute',
            }

            return output
        elif selected == '取消静音':
            output = {
                'command':"operation.volumn_control.vol_ctrl().mute_all(mute = False)",
                # 'chat':'已取消静音'
                'chat':'Mute cancelled',
            }

        else:
            self._extract_info(prompt.Prompt5(input_statement, context).prompt)


            res = {
                'command':f"operation.volumn_control.vol_ctrl().alter({self.num})",
                # 'chat':self.answer,
                'chat':f"Have already turned to {self.num}",
                'state_code':0,
            }
            print(f"[音量调节]:{self.answer}")
        return res


       
    def _extract_info(self, prompt):
        # print('prompt',prompt)
        self.answer,_ = self.chat(prompt, self.generation_config, history = [])
        print('[数字提取]', self.answer)
        self.num = int(re.findall(r"\d+\.?\d*", self.answer)[-1])
    
    def opr1(self,input_statement,context):
        # 配置
        answer,_ = self.chat(prompt.Prompt1(input_statement, context).prompt,self.generation_config, history = [])
        res = {
            'chat': answer,
            'state_code': 0,
        }
        return res
    
    def opr3(self,input_statement):
        # 打开软件
        from utils.search_doc_faiss import faiss_corpus
        from data.map import name_exe_map
        self.tool = search_tool()
        args_app = self._get_parser() 

        corpus = faiss_corpus(args = args_app,model=self.model_sim,tokenizer=self.tokenizer_sim)
        selected_idx,score = corpus.search(query = input_statement,verbose=True)
        app_name = corpus.corpus[selected_idx]
        print(f'find app {app_name}')
        a = 'C:/Users'
        output = {
            'command':f"operation.open_app.search_tool().open_app(a='C:/',b='{name_exe_map[app_name]}')",
            # 'chat':f"已为您打开{app_name}"
            'chat':f"okay"
            
        }
        return output
    
    def _get_parser(self):
        parser = argparse.ArgumentParser('Opening APP')
        parser.add_argument('--new-embed', default=False, type=bool)
        parser.add_argument('--document-embed', default='./data/document_embed.npy')
        parser.add_argument('--k', default=1)
        parser.add_argument('--device', default="cuda")
        parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")
        parser.add_argument('--index_location', default='./data/app_map.index')
        parser.add_argument('--document-corpus', default='./data/app.txt')
        parser.add_argument('--search', default=2)
        args = parser.parse_args()
        return args

    def opr4(self,input_statement,context):
        # 配置
        return self.opr1(input_statement,context)




    

        
