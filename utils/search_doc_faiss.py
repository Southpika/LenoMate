from transformers import AutoModel,AutoTokenizer
import torch
import argparse
import faiss
import numpy as np
import os


## Predefined 
def get_parser():
    parser = argparse.ArgumentParser('Matching Task')
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--new-embed', default=False,type=bool)
    parser.add_argument('--document-embed', default='./data/document_embed.npy')
    parser.add_argument('--k', default=1)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")
    parser.add_argument('--index_location', default='./data/test.index')
    parser.add_argument('--search', default=1)
    args = parser.parse_args()      
    return args
def l2_normalization(data):
    if data.ndim == 1:
        return data / np.linalg.norm(data).reshape(-1,1)
    else:
        return data/np.linalg.norm(data,axis=1).reshape(-1,1)
def cls_pooling(model_output,return_tensors=False):
    if not return_tensors:
        return l2_normalization(model_output.last_hidden_state[:,0].cpu().numpy())
    else:
        return l2_normalization(model_output.last_hidden_state[:,0])

def mean_pooling(model_output, attention_mask, return_tensors=False):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    output = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    if not return_tensors:
        return output.cpu().numpy()
    else:
        return output

args = get_parser()

class faiss_corpus:
    def __init__(self,args=args):
        print('[INFO]Loading Model')
        self.args = args
        self.device = args.device
        self.tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        self.model = AutoModel.from_pretrained(args.model_name).to(self.device)
        ## Loading data 
        self.corpus = []
        with open(args.document_corpus,'r',encoding='utf-8') as f:
            for line in f:
                self.corpus.append(line.strip('\n'))

    def fit(self):
        """
        The first time to load corpus and set index
        """
        print('[INFO]Creating Document Embeddings')
        print(self.corpus)
        self.model.eval()
        input_data = self.tokenizer(self.corpus, padding=True, return_tensors="pt")
        with torch.no_grad():
            corpus_embeddings = self.model(**input_data.to(self.device))
        # corpus_embeddings = cls_pooling(corpus_embeddings)
        corpus_embeddings = mean_pooling(corpus_embeddings,attention_mask=input_data['attention_mask'])
        features = l2_normalization(corpus_embeddings)
        dim = features.shape[1]
        index_ip = faiss.IndexFlatIP(dim)
        index_ip.add(features)
        faiss.write_index(index_ip, self.args.index_location)
        print(f'[INFO]Finishing Saving Indexing to {self.args.index_location}')
    
    def load(self):
        self.index_ip = faiss.read_index(self.args.index_location)

    def search(self,query = '如何更换花呗绑定银行卡',verbose=False):
        self.load()
        input_data = self.tokenizer(query, padding=True, return_tensors="pt")  
        self.model.eval()     
        with torch.no_grad():
            query_embeddings = self.model(**input_data.to(self.device))
            # query_embeddings = cls_pooling(query_embeddings)
            query_embeddings = mean_pooling(query_embeddings,attention_mask=input_data['attention_mask'])
            feature_search = l2_normalization(query_embeddings)        
            D, I = self.index_ip.search(feature_search, self.args.k)
            idx,score = int(I[0][0]),float(D[0][0]) 
            # if args.search == 1:
            #     idx = instruction_prompt_map[idx]
            # else:
            #     idx = name_exe_map[idx]
            # print(idx,score)
        if verbose:
            print(idx,self.corpus[idx], "(Score: {:.4f})".format(score))
        return  idx,score

if __name__ == '__main__':
    corpus = faiss_corpus(args)
    print(corpus.search(query = input('请输入你的问题：\n'),verbose=True))









    
