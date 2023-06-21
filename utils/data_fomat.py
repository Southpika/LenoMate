from tqdm import tqdm
from datasets import load_dataset
import re
import pandas as pd
import numpy as np
import argparse

def get_parser():
    parser = argparse.ArgumentParser('Get Data From Huggingface')
    parser.add_argument('--record', default=100,type=int)
    parser.add_argument('--data_name', default="silk-road/Wizard-LM-Chinese-instruct-evol")
    parser.add_argument('--output_dir', default="./data/dolly_hug.csv")
    parser.add_argument('--output_dir_temp', default="./utils/temp_huggingface.csv")
    args = parser.parse_args() 
    return args
args = get_parser() 

def has_chinese(text):
    """
    Judging whether the sentence has Chinese
    """
    pattern = re.compile(r'[\u4e00-\u9fa5]')  # 匹配中文字符的正则表达式
    match = re.search(pattern, text)
    if match:
        return True
    else:
        return False

output_list = [] #pd.DataFrame()
# output_list['instruction_zh'] = np.nan
# output_list['output_zh'] = np.nan
# output_list['instruction'] = np.nan
# output_list['output'] = np.nan

dataset = load_dataset(args.data_name)
print('Begin to clean data...')
for i in tqdm(range(len(dataset['train']))):
    temp_data = dataset['train'][i]
    if temp_data['instruction_zh'] and temp_data['output_zh']:
        if has_chinese(temp_data['instruction_zh']) and has_chinese(temp_data['output_zh']):
            output_list.append(temp_data)
    if i % args.record == (args.record-1):
        print(f'Temp Saving for {i}th...')
        pd.DataFrame(output_list).to_csv(args.output_dir_temp)
pd.DataFrame(output_list).to_csv(args.output_dir)
print('Finish clean data...')

