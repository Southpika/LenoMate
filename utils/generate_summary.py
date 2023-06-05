## 根据已有回答产生summary，并将summary保存至data目录下以供索引

import argparse
import pandas as pd
from tqdm import tqdm
from numba import jit
from transformers import AutoTokenizer,AutoModel
from peft import PeftModel
import pandas as pd
import torch
import time
from stop_criterion import StopWordsCriteria

def get_parser():
    parser = argparse.ArgumentParser('Text Matching task')
    parser.add_argument('--document', default='./data/document.txt')
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--BATCH-SIZE',default=256)

    parser.add_argument('--data-path',default='new_pqaa.jsonl')
    parser.add_argument('--work-dir',default="./tzh_model/medical_glm_v3")
    parser.add_argument('--model-dir',default="/root/autodl-tmp/chatglm")
    
    parser.add_argument('--max-length',default=300)
    parser.add_argument('--temperature',default=0.9)
    parser.add_argument('--temperature',default=300)
    parser.add_argument('--top-p',default=0.95)
    parser.add_argument('--repetition',default=1.15)


    config = parser.parse_args([])      
    return config

args = get_parser()
model = AutoModel.from_pretrained(args.model_dir, load_in_8bit=True, trust_remote_code=True, device_map='auto')
tokenizer = AutoTokenizer.from_pretrained(args.model_dir, trust_remote_code=True)
model.config.use_cache = False
model.supports_gradient_checkpointing = True
model.gradient_checkpointing_enable()
model.enable_input_require_grads()
model.config.use_cache = False  
model = PeftModel.from_pretrained(model, args.work_dir)
model.is_parallelizable = True
model.model_parallel = True



def generate_prompt(s):
    return f"""<用户>：请总结以下文章，文章：{s}
<ChatGLM-6B>：
"""

doc = []
with open(args.document,'r',encoding='utf-8') as f:
    for line in f:
        doc.append(line.strip('\n'))

doc_batch = []
for i in tqdm(range(0, len(doc), args.BATCH_SIZE)):
    batch = doc[i:min(i+args.BATCH_SIZE, len(doc)-1)]
    doc_batch.append(tokenizer(batch, padding=True, return_tensors='pt'))

def time_suffix():
    return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

stop_criteria = StopWordsCriteria(tokenizer, ['<ChatGLM-6B>'], stream_callback=None)
with open(f"ans{time_suffix()}.txt", 'w') as f:
    ans = []
    for batch in tqdm(doc_batch):
        with torch.no_grad():
            out = model.generate(
                **batch.to('cuda'),
                max_length=args.max_length,
                temperature=args.temperature,
                top_p = args.top_p,
                repetition_penalty = args.repetition,
            )
            answer = tokenizer.batch_decode(out)
            f.write('\n'.join(answer) + '\n'+'='*30)
            ans += answer

    print('Finish Inference...')
f.close()



    