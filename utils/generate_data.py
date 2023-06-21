import os
import openai
openai.api_type = "azure"
openai.api_base = "https://openaipoc-kepler.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = '14639a3cad0f4ba38483194f82c6920b'

# messageshistory = 
response = openai.ChatCompletion.create(
      engine="Kepler1",
      messages = [
                {"role":"system","content":"You are an AI assistant that helps people find information."},
                {"role":"user","content":""},
            ],
      temperature=0.5,
      max_tokens=300,
      top_p=0.95,
      frequency_penalty=0,
      presence_penalty=0,
      stop=None)
print('AI bot:',response['choices'][0]['message']['content'])
bot = response['choices'][0]['message']['content']