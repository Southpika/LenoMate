import os
import openai
import pandas as pd
from tqdm import tqdm
import numpy as np
import argparse

openai.api_type = "azure"
openai.api_base = "https://openaipoc-kepler.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = '14639a3cad0f4ba38483194f82c6920b'

# messageshistory = 
def get_ans(data,verbose=False):
    response = openai.ChatCompletion.create(
        engine="Kepler1",
        messages = [
            {"role":"system","content":"You are an AI assistant named LenoMate from Lenovo that helps people find information."},
            {"role":"user","content":data['question']},
        ],
        temperature=0.5,
        max_tokens=400,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    if verbose:
        print('AI bot:',response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']
def get_parser():
    parser = argparse.ArgumentParser('Text Matching task')
    parser.add_argument('--record', default=500,type=int)
    parser.add_argument('--temp_path', default='data_ans_temp.csv')
    parser.add_argument('--final_path', default='data_ans.csv')
    config = parser.parse_args()
    return config
args = get_parser()

if __name__ == '__main__':
    df = pd.read_csv('data.csv',encoding='gbk')
    # tqdm.pandas(desc='Generating Answer...')
    df['ans'] = np.nan
    # print(args.record)
    for i in tqdm(range(df.shape[0])):
        df.iloc[i,1] = get_ans(df.iloc[i,:])
        if i % args.record == (args.record-1):
            df.to_csv(args.temp_path)
            print(f"已在{i}轮完成记录")
    df.to_csv(args.final_path)
    print('Finish Generating...')