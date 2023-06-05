from text2vec import SentenceModel, cos_sim, semantic_search
import argparse
import numpy as np
import os
import torch
parser = argparse.ArgumentParser('Matching Task')
parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
parser.add_argument('--new-embed', default=False)
parser.add_argument('--document-embed', default='./data/document_embed.npy')
parser.add_argument('--k', default=5)
args = parser.parse_args(args=[])

print('[INFO]Loading Model')
embedder = SentenceModel('shibing624/text2vec-base-chinese')

if args.new_embed or not os.path.isfile(args.document_embed):
    print('[INFO]Creating Document Embeddings')
    corpus = []
    with open(args.document_corpus,'r',encoding='utf-8') as f:
        for line in f:
            corpus.append(line.strip('\n'))
    corpus_embeddings = embedder.encode(corpus)
    np.save(args.document_embed,corpus_embeddings)
    print('[INFO]Finishing Saving Embedding')
else:
    corpus_embeddings = np.load(args.document_embed)


if __name__ == '__main__':
    corpus_embeddings = torch.tensor(corpus_embeddings).to('cuda')
    query = input('Please enter your question: ')
    query_embedding = embedder.encode(query)
    # We use cosine-similarity and torch.topk to find the highest 5 scores
    top_k = min(args.k, corpus_embeddings.shape[0])
    cos_scores = cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)
    print("\n\n======================\n\n")
    print("Query:", query)
    print("\nTop 5 most similar sentences in corpus:")
    for score, idx in zip(top_results[0], top_results[1]):
        print(idx, "(Score: {:.4f})".format(score))