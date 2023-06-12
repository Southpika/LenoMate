from search_doc_faiss import faiss_corpus

import argparse


## Predefined 


def get_parser():
    parser = argparse.ArgumentParser('Matching Task')
    
    parser.add_argument('--new-embed', default=False,type=bool)
    parser.add_argument('--document-embed', default='./data/document_embed.npy')
    parser.add_argument('--k', default=1)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")

    parser.add_argument('--index_location', default='./data/test.index')
    parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
    args = parser.parse_args()      
    return args
args_app = get_parser()
corpus = []
with open(args_app.document_corpus,'r',encoding='utf-8') as f:
    for line in f:
        corpus.append(line.strip('\n'))
corpus = faiss_corpus(args = args_app)
corpus.fit()

#如果需要更新app匹配 把index_location改成app_map.index document-corpus改成app.text
