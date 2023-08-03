import torch
from search_doc_faiss import faiss_corpus
import argparse


class long_text_dataset():
    def __init__(self,doc,tokenizer,required = 3000):

        doc_tokenization = tokenizer.encode(doc,add_special_tokens=False)
        self.doc = []
        size = len(doc_tokenization)
        if size >= required:
            for i in range(size // required + 1):
                self.doc.append(doc_tokenization[i*required : (i+1)*required])
    
    def get_parser(self):
        parser = argparse.ArgumentParser('Long Text Split')
        
        parser.add_argument('--new-embed', default=False,type=bool)
        parser.add_argument('--k', default=1)
        parser.add_argument('--device', default="cuda")
        parser.add_argument('--model-name', default="GanymedeNil/text2vec-large-chinese")

        parser.add_argument('--index_location', default='./data/test.index')
        parser.add_argument('--document-corpus', default='./data/document_corpus.txt')
        args = parser.parse_args()      
        return args
    
    def fit(self,model_sim,tokenizer_sim,query):

        args_document = self.get_parser()
        corpus = self.doc
        self.documents = faiss_corpus(args = args_document,doc_corpus=corpus,model = model_sim, tokenizer=tokenizer_sim)
        self.documents.fit()
    
    def search(self,query):
        self.documents.corpus
        return self.documents.search(query)
    
    
        
                
