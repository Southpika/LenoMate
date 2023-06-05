from text2vec import  cos_sim
from transformers import AutoTokenizer,AutoModel
import argparse
import numpy as np
import os
import torch

def get_parser():
    parser = argparse.ArgumentParser('Matching Task')
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    parser.add_argument('--new-embed', default=False,type=bool)
    parser.add_argument('--document-embed', default='./data/document_embed.npy')
    parser.add_argument('--k', default=5)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")
    args = parser.parse_args()      
    return args
args = get_parser()

print('new embed',args.new_embed)
print('[INFO]Loading Model')
device = args.device
tokenizer = AutoTokenizer.from_pretrained(args.model_name)
model = AutoModel.from_pretrained(args.model_name).to(device)

def cls_pooling(model_output,return_tensors=False):
    if not return_tensors:
        return model_output.last_hidden_state[:,0].cpu().numpy()
    else:
        return model_output.last_hidden_state[:,0]
    

corpus = []
with open(args.document_corpus,'r',encoding='utf-8') as f:
    for line in f:
        corpus.append(line.strip('\n'))
if args.new_embed or not os.path.isfile(args.document_embed):
    print('[INFO]Creating Document Embeddings')
    with torch.no_grad():
        corpus_embeddings = model(**tokenizer(corpus, padding=True, return_tensors="pt").to(device))
    corpus_embeddings = cls_pooling(corpus_embeddings)
    np.save(args.document_embed,corpus_embeddings)
    print('[INFO]Finishing Saving Embedding')
else:
    corpus_embeddings = np.load(args.document_embed)


if __name__ == '__main__':
    
    corpus_embeddings = torch.tensor(corpus_embeddings).to(device)
    query = input('Please enter your question: ')
    query_embedding = cls_pooling(model(**tokenizer(query, return_tensors="pt").to(device)),return_tensors=True).to(device)
    # We use cosine-similarity and torch.topk to find the highest 5 scores
    top_k = min(args.k, corpus_embeddings.shape[0])
    cos_scores = cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)
    print("\n======================\n")
    print("Query:", query)
    print("\nTop 5 most similar sentences in corpus:")
    for score, idx in zip(top_results[0], top_results[1]):
        print(corpus[idx], "(Score: {:.4f})".format(score))