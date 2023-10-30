"""
File_name: lenomate.py
author: tanzhehao
version: /

Overview:
这个文件主要为主处理函数，用于分发以及处理不同的意图

Note:
- state_code: 0聊天  1中间变量传输 2文件 3网页 4功能 5蓝屏 6绘画 7邮件
"""
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from utils.search_doc_faiss import faiss_corpus
import torch
import operation.operation_server_glm as operation
from peft import PeftModel
from transformers.generation import GenerationConfig
from utils.wallpaper_generate import sdmodels, sd_args


class LenoMate:
    def __init__(self, model_type, args):
        """
        Class: LenoMate

        Description:
        The LenoMate class is responsible for initializing and managing various models and components used in a chatbot system. It supports different model types, such as 'glm' and 'qw', and processes client data for generating responses.

        Attributes:
        - model_sim (AutoModel): A transformer model for semantic similarity.
        - tokenizer_sim (AutoTokenizer): A tokenizer for the semantic similarity model.
        - corpus (faiss_corpus): An instance for managing the document corpus used in similarity calculations.
        - args: Configuration parameters and arguments provided during initialization.
        - sd (sdmodels): A component responsible for picture generation in specific model types.
        - model (AutoModel or AutoModelForCausalLM): The main conversational model.
        - tokenizer (AutoTokenizer): The tokenizer for the main conversational model.

        Methods:
        - __init__(self, model_type, args): Initializes the LenoMate class by loading required models and components based on the model type and provided arguments.
        - process(self, data_client, history): Processes client data and generates responses based on the model type and chatbot state.
        - reset_bot(self): Resets the chatbot to its initial state and loads the appropriate model components.

        Note:
        - This class is designed to support different conversational models (e.g., 'glm' and 'qw') and is responsible for managing their initialization and usage.
        """
        print("模型加载中...")
        self.model_sim = AutoModel.from_pretrained(args.simmodel_dir).to('cuda')
        self.tokenizer_sim = AutoTokenizer.from_pretrained(args.simmodel_dir)
        self.model_sim.eval()
        self.corpus = faiss_corpus(args=args, model=self.model_sim, tokenizer=self.tokenizer_sim)
        args.model_type = model_type
        self.args = args


        if model_type == 'glm':
            prompt_model = AutoModelForCausalLM.from_pretrained(
                'alibaba-pai/pai-bloom-1b1-text2prompt-sd').eval().cuda()
            prompt_tokenizer = AutoTokenizer.from_pretrained('alibaba-pai/pai-bloom-1b1-text2prompt-sd')

            self.sd = sdmodels(sd_args, prompt_model, prompt_tokenizer)
            self.model = AutoModel.from_pretrained(args.glm_model_dir, trust_remote_code=True).cuda()
            self.tokenizer = AutoTokenizer.from_pretrained(args.glm_model_dir, trust_remote_code=True)
            self.model = PeftModel.from_pretrained(self.model, args.glm_work_dir)

        if model_type == 'qw':
            self.sd = sdmodels(sd_args)
            self.model = AutoModelForCausalLM.from_pretrained(args.qw_model_dir, trust_remote_code=True,
                                                              bf16=True).cuda()
            self.tokenizer = AutoTokenizer.from_pretrained(args.qw_model_dir, trust_remote_code=True)
            from transformers import PreTrainedModel
            from transformers_stream_generator.main import NewGenerationMixin
            PreTrainedModel.generate = NewGenerationMixin.generate
            PreTrainedModel.sample_stream = NewGenerationMixin.sample_stream
            
        self.reset_bot()

        self.model.is_parallelizable = True
        self.model.model_parallel = True
        self.model.eval()
        print("模型加载完成")

    def process(self, data_client, history):
        # self.reset_bot()
        torch.cuda.empty_cache()
        if data_client['state_code'] in [1, 4, 6]:
            result = self.opr.fit(data_client)
            # if data_client['state_code'] != 6:
            # print("模型输出：", result)
            return str(result)

        else:
            answer_dict = eval(f"self.chat_bot.mode{data_client['state_code']}")(data_client,history)
            # print("模型输出：", answer_dict)
            return answer_dict

    def reset_bot(self):
        if self.args.model_type == 'glm':
            import utils.glm.glm_chat_mode as glm_chat_mode
            self.chat_bot = glm_chat_mode.chat_bot(self.model, self.tokenizer)
            self.opr = glm_chat_mode.operation_bot(self.model, self.tokenizer, self.model_sim, self.tokenizer_sim,
                                                   self.corpus, self.sd)
        if self.args.model_type == 'qw':
            import utils.qwen.qw_chat_mode as qw_chat_mode
            from transformers_stream_generator.main import StreamGenerationConfig
            generation_config = GenerationConfig.from_pretrained(self.args.qw_model_dir, trust_remote_code=True)
            stream_config = StreamGenerationConfig(**generation_config.to_dict(), do_stream=True)

            generation_config = GenerationConfig.from_pretrained(self.args.qw_model_dir, trust_remote_code=True)
            self.chat_bot = qw_chat_mode.chat_bot(self.model, self.tokenizer, stream_config)
            self.opr = qw_chat_mode.operation_bot(self.model, self.tokenizer, self.model_sim, self.tokenizer_sim,
                                                  self.corpus, stream_config, self.sd)
    