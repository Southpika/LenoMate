import operation.prompt as prompt
import operation.operation as operation
import torch
from transformers import AutoTokenizer, AutoModel
import warnings
from utils.search_doc_faiss import faiss_corpus
from data.map import instruction_prompt_map
import audio.recognition as recognition, audio.synthesis as synthesis, audio.play as play, audio.record as record

warnings.filterwarnings("ignore")


##
def main():
    corpus = faiss_corpus()

    # result = recognition.main()
    start = "你好，我是联想语音助手"
    synthesis.main(start)
    play.play()
    # input_statement = input("你想要做什么？\n")
    input_statement = recognition.main()
    selected_idx, score = corpus.search(query=input_statement, verbose=True)

    torch.cuda.empty_cache()

    # prompt = eval(f"prompt.Prompt{instruction_prompt_map[selected_idx]}")(input_statement)
    # prompt = prompt.Prompt0(input_statement)
    print('Loading...')
    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
    opt = eval(f"operation.Operation{selected_idx}")(input_statement)
    # print(opt.fit(model,tokenizer))
    result = opt.fit(model, tokenizer)
    synthesis.main(result)
    play.play()
    return result


if __name__ == '__main__':
    main()
