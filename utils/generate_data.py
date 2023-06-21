import os
import openai
import pandas as pd
from tqdm import tqdm


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
            max_tokens=300,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
      if verbose:
            print('AI bot:',response['choices'][0]['message']['content'])
      return response['choices'][0]['message']['content']

if __name__ == '__main__':
      df = pd.read_csv('data.csv')
      tqdm.pandas(desc='Generating Answer...')
      df['ans'] = df.progress_apply(get_ans,axis=1)
      df.to_csv('data_ans.csv')
      print('Finish Generating...')