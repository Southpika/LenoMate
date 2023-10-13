import torch
import numpy as np

def l2_normalization(data):
    if data.ndim == 1:
        return data / np.linalg.norm(data).reshape(-1, 1)
    else:
        return data / np.linalg.norm(data, axis=1).reshape(-1, 1)
    
def _pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    output = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1),
                                                                                min=1e-9)
    return l2_normalization(output.cpu().numpy()) 


def judge(input_statement,model_sim,tokenizer_sim):
    _mute = '静音'
    _normal = '调节音量'
    _no_mute = '取消静音'
    corpus = [_mute, _normal, _no_mute]
    model_sim.eval()
    input_data = tokenizer_sim(input_statement, return_tensors="pt")
    corp = tokenizer_sim(corpus, return_tensors="pt", padding=True)
    with torch.no_grad():
        corpus_embeddings = model_sim(**corp.to('cuda'))
        input_embeddings = model_sim(**input_data.to('cuda'))
    corpus_embeddings = _pooling(corpus_embeddings, attention_mask=corp['attention_mask'])
    input_embeddings = _pooling(input_embeddings, attention_mask=input_data['attention_mask'])
    selected = corpus[(corpus_embeddings @ input_embeddings.T).argmax(axis=0)[0]]
    print(f"[音量调节功能]音量功能匹配为'{selected}'")
    return selected