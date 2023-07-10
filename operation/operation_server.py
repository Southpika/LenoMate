import pynvml
import screen_brightness_control as sbc
import time
import os
import argparse
import torch
import operation.prompt as prompt
import re
from operation.open_app import search_tool
import numpy as np

class Operation:
    def __init__(self,input_statement,context=None) -> None:
        self.input_statement = input_statement
        self.context = context
    def fit(self):
        raise NotImplementedError

## 放入context给出数值
class Operation0(Operation):
    def fit(self,model,tokenizer):
        self.prompt = prompt.Prompt0(self.input_statement,self.context).prompt
        self._extract_info(self.prompt,model,tokenizer)
        self.brightness = self.num
        res = {
            'chat':self.answer,
            'state_code':0,
            'command':f"python operation\screen_brightness.py --bright {self.num}"
        }
        return res
            
    def _extract_info(self,prompt,model,tokenizer):
        model.eval()
        with torch.no_grad():
            input_ids = tokenizer.encode(prompt, return_tensors='pt').to('cuda')
            out = model.generate(
                    input_ids=input_ids,
                    max_length=200,
                    temperature=0.9,
                    top_p=0.95,
                )
            self.answer = tokenizer.decode(out[0]).split('<bot>:')[1]
            print('[屏幕亮度调节功能]',self.answer)
            self.num = int(re.findall(r"\d+\.?\d*",self.answer)[-1])


class Operation1(Operation):
    def fit(self,model,tokenizer):        
        self.prompt = prompt.Prompt1(self.input_statement,self.context).prompt
        model.eval()
        with torch.no_grad():
            input_ids = tokenizer.encode(self.prompt, return_tensors='pt').to('cuda')
            out = model.generate(
                input_ids=input_ids,
                max_length=400,
                temperature=0.9,
                top_p = 0.95,
            )
            answer = tokenizer.decode(out[0]).split('##回答')[1].strip('：').strip()
            res = {
            'chat':answer,
            'state_code':0,
            }
            return res

default_path = os.path.join(os.path.expanduser("~"), "Desktop") ## desktop_path
def time_suffix():
    return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

class Operation2(Operation):
    def __init__(self,inputs,path=default_path,summary='notebook'):
        self.path = path
        self.inputs = time.strftime("%Y%m%d", time.localtime(time.time()))+':'+inputs
        self.summary = summary
        
    def fit(self,model,tokenizer):
        self.prompt = prompt.Prompt2(self.inputs).prompt
        model.eval()
        with torch.no_grad():
            input_ids = tokenizer.encode(self.prompt, return_tensors='pt').to('cuda')
            out = model.generate(
                input_ids=input_ids,
                max_length=200,
                temperature=0.3,
                top_p = 0.95,
                # repetition_penalty = 1.15,
                # stopping_criteria = StoppingCriteriaList([stop_criteria])
                # do_sample = True
            )
            print('operation3 output',tokenizer.decode(out[0]).split('##总结:'))
            answer = tokenizer.decode(out[0]).split('##总结:')[1].strip()
            
            self.summary = answer.strip('。')

        file_name = 'LenoMate_'+self.summary+'_'+time_suffix()+'.txt'
        file_name = os.path.join(default_path,file_name)
        with open(file_name,'w',encoding='utf-8') as f:
            f.write(self.inputs)
        f.close()
        return f'已完成记录，保存在桌面，文件名称为{file_name}'
    
# def get_parser():
#     parser = argparse.ArgumentParser('Opening APP')
    
#     parser.add_argument('--new-embed', default=False,type=bool)
#     parser.add_argument('--document-embed', default='./data/document_embed.npy')
#     parser.add_argument('--k', default=1)
#     parser.add_argument('--device', default="cuda")
#     parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")

#     parser.add_argument('--index_location', default='./data/app_map.index')
#     parser.add_argument('--document-corpus', default='./data/app.txt')
#     parser.add_argument('--search', default=2)
#     args = parser.parse_args()      
#     return args
# args_app = get_parser()  

class Operation3(Operation):
    def fit(self,model=None,tokenizer=None):
        from utils.search_doc_faiss import faiss_corpus
        from data.map import name_exe_map
        self.tool = search_tool()
        args_app = self.get_parser() 
        corpus = faiss_corpus(args = args_app)
        selected_idx,score = corpus.search(query = self.input_statement,verbose=True)
        app_name = corpus.corpus[selected_idx]
        print(f'find app {app_name}')
        output = {
            'command':f"python operation/open_app.py --a C --b {name_exe_map[app_name]}",
            'chat':f"已为您打开{app_name}"
        }
        return output
    
    def get_parser(self):
        parser = argparse.ArgumentParser('Opening APP')
        parser.add_argument('--new-embed', default=False,type=bool)
        parser.add_argument('--document-embed', default='./data/document_embed.npy')
        parser.add_argument('--k', default=1)
        parser.add_argument('--device', default="cuda")
        parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")
        parser.add_argument('--index_location', default='./data/app_map.index')
        parser.add_argument('--document-corpus', default='./data/app.txt')
        parser.add_argument('--search', default=2)
        args = parser.parse_args()      
        return args
     
    
class Operation4(Operation):
    def fit(self,model,tokenizer):
        self.prompt = prompt.Prompt1(self.input_statement,self.context).prompt
        model.eval()
        with torch.no_grad():
            input_ids = tokenizer.encode(self.prompt, return_tensors='pt').to('cuda')
            out = model.generate(
                input_ids=input_ids,
                max_length=400,
                temperature=0.3,
                top_p = 0.95,
                # stopping_criteria = StoppingCriteriaList([stop_criteria])
            )
            answer = tokenizer.decode(out[0]).split('##回答')[1].strip('：').strip()

            return {'chat':answer}
      
class Operation5():
    def __init__(self,inputs,context,model_sim,tokenizer_sim) -> None:
        # from operation.volumn_control import vol_ctrl
        # self.vol_ctrl = vol_ctrl()
        self.inputs = inputs
        self.model_sim = model_sim
        self.tokenizer_sim = tokenizer_sim
        self.context = context

    def fit(self,model,tokenizer,remote = False):
        self.judge()
        if self.selected=='静音': 
            output = {
                'command':"python operation/volumn_control.py --mute 1",
                'chat':'已静音'
            }
            
            return output
        elif self.selected=='取消静音': 
            output = {
                'command':"python operation/volumn_control.py --mute 0",
                'chat':'已取消静音'
            }
            
        else:
            self.prompt = prompt.Prompt4(self.context,self.inputs).prompt
            self.extract_info(self.prompt,model,tokenizer)
            output = {
                'command':f"python operation/volumn_control.py --vol {self.num}",
                'chat':self.answer
            }
        return output
        try:
            self.vol_ctrl.alter(self.num)
            return self.answer
        except:
            return f'对不起，我没识别到您的指令，请重新描述~'

    def judge(self):
        _mute = '静音'
        _normal = '调节音量'
        _no_mute = '取消静音'
        corpus = [_mute,_normal,_no_mute]
        self.model_sim.eval()
        input_data = self.tokenizer_sim(self.inputs, return_tensors="pt")
        corp = self.tokenizer_sim(corpus, return_tensors="pt",padding=True)
        with torch.no_grad():
            corpus_embeddings = self.model_sim(**corp.to('cuda'))
            input_embeddings = self.model_sim(**input_data.to('cuda'))
        corpus_embeddings = self._pooling(corpus_embeddings,attention_mask=corp['attention_mask'])
        input_embeddings = self._pooling(input_embeddings,attention_mask=input_data['attention_mask'])
        self.selected = corpus[(corpus_embeddings@input_embeddings.T).argmax(axis=0)[0]]
        print(f"[音量调节功能]音量功能匹配为'{self.selected}'")

    def _pooling(self,model_output,attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        output = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return self._l2_normalization(output.cpu().numpy())
    
    def _l2_normalization(self,data):
        if data.ndim == 1:
            return data / np.linalg.norm(data).reshape(-1,1)
        else:
            return data/ np.linalg.norm(data,axis=1).reshape(-1,1)
        
    def extract_info(self,prompt,model,tokenizer):
        model.eval()
        with torch.no_grad():
            input_ids = tokenizer.encode(prompt, return_tensors='pt').to('cuda')
            out = model.generate(
                input_ids=input_ids,
                max_length=200,
                temperature=0.3,
                top_p = 0.95,
                # repetition_penalty = 1.15,
                # stopping_criteria = StoppingCriteriaList([stop_criteria])
                # do_sample = True
            )
            self.answer = tokenizer.decode(out[0]).split('<bot>:')[1]
            print('[音量调节功能]',self.answer)
            self.num = int(re.findall(r"\d+\.?\d*",self.answer)[-1])


if __name__=='__main__':
    parser = argparse.ArgumentParser('Client Operation')
    parser.add_argument('--select-idx', default=0)
    args = parser.parse_args() 
    operation = eval(f"Operation{args.select_idx}")()
    print(operation.fit())