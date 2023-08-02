class long_text_dataset():
    def __init__(self,doc,tokenizer,required = 3000):

        doc_tokenization = tokenizer.encode(doc,add_special_tokens=False)
        self.doc = []
        size = len(doc_tokenization)
        if size >= required:
            for i in range(size // required + 1):
                self.doc.append(doc_tokenization[i*required : (i+1)*required])

    def fit(self):
        return self.doc

my_doc = long_text_dataset(cont,tokenizer)
doc = my_doc.fit()