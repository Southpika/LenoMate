import argparse
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from PIL import Image
import math
import os
# import wallpaper
parser = argparse.ArgumentParser()

parser.add_argument(
    "--prompt",
    type=str,
    nargs="?",
    default="sea",
    help="the prompt to render"
)

parser.add_argument(
    "--model-location",
    type=str,
    nargs="?",
    default=r"models/anything-v5-PrtRE.safetensors",
    help="model path(end with safetensors)"
)

parser.add_argument(
    "--lora-location",
    type=str,
    nargs="?",
    default=r'./models/example_loras/PAseerCloudV1.safetensors',
    help="lora path(end with safetensors),recommend ./example_loras/PAseerCloudV1.safetensors"
)

parser.add_argument(
    "--width",
    type=int,
    nargs="?",
    default=968,
    help="picture width"
)

parser.add_argument(
    "--height",
    type=int,
    nargs="?",
    default=560,
    help="picture height"
)

parser.add_argument(
    "--num_images",
    type=int,
    nargs="?",
    default=4,
    help="num_images_per_prompt"
)

parser.add_argument(
    "--grid",
    type=bool,
    default=True,
    help="grid images"
)

parser.add_argument(
    "--save-dir",
    type=str,
    default=True,
    help="grid images"
)

parser.add_argument(
    "--outpath",
    type=str,
    nargs="?",
    help="dir to write results to",
    default="outputs/txt2img-samples"
)

parser.add_argument(
    "--accelerate",
    type=str,
    nargs="?",
    help="accelerate ways",
    default="xformers"
)

sd_args = parser.parse_args()

class sdmodels:
    def __init__(self,args,prompt_model = None, prompt_tokenizer = None):
        print('[Painting]loading model...')
        os.makedirs(os.path.dirname(args.model_location), exist_ok=True)
        self.args = args
        self.pipeline = StableDiffusionPipeline.from_single_file(
            args.model_location,
            torch_dtype=torch.float16,
            revision="fp16",
            local_files_only=True,
        ).to('cuda')
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self.pipeline.scheduler.config)
        if args.accelerate:
            self._accelerate()
        if args.lora_location:
            self.pipeline.load_lora_weights(args.lora_location)       

        self.negative_prompt =  ["(low quality, worst quality:1.4), (bad anatomy), (inaccurate limb:1.2), "
                   "bad composition, inaccurate eyes, extra digit, fewer digits, (extra arms:1.2), large breasts"]
        self.prompt = args.prompt
        # self.prompt_tokenizer = AutoTokenizer.from_pretrained('alibaba-pai/pai-bloom-1b1-text2prompt-sd')
        # self.prompt_model = AutoModelForCausalLM.from_pretrained('alibaba-pai/pai-bloom-1b1-text2prompt-sd').eval().cuda()
        # self.prompt_model.eval()
        self.prompt_model = prompt_model
        self.prompt_tokenizer = prompt_tokenizer
        print('model prepared...')
        print('*'*50)



    def inference(self,prompt=None):
        torch.cuda.empty_cache()
        
        input_prompt = prompt if prompt else self.args.prompt

        if self.prompt_model:
            input = f'Instruction: Give a simple description of the image to generate a drawing prompt.\nInput: {input_prompt}\nOutput:'
            input_ids = self.prompt_tokenizer.encode(input, return_tensors='pt').cuda()
            with torch.no_grad():
                outputs = self.prompt_model.generate(
                    input_ids,
                    max_length=384,
                    do_sample=True,
                    temperature=1.0,
                    top_k=50,
                    top_p=0.95,
                    repetition_penalty=1.2,
                    num_return_sequences=self.args.num_images)

            prompts = self.prompt_tokenizer.batch_decode(outputs[:, input_ids.size(1):], skip_special_tokens=True)
            input_prompt = [p.strip() for p in prompts]
        else:
            input_prompt = [input_prompt] * self.args.num_images
        torch.cuda.empty_cache()
        with torch.inference_mode():
            print(input_prompt)
            image = self.pipeline(
                prompt = input_prompt, 
                width = self.args.width,
                height = self.args.height,
                num_images_per_prompt=1,
                num_inference_steps=20, 
                negative_prompt=self.negative_prompt * self.args.num_images, 
                generator=torch.manual_seed(0)
            ).images
        torch.cuda.empty_cache()
        sample_path = os.path.join(self.args.outpath, "samples")
        os.makedirs(sample_path, exist_ok=True)
        base_count = len(os.listdir(sample_path))
        grid_count = len(os.listdir(self.args.outpath)) - 1   
        pic_path = []
        if self.args.grid:
            grid_image = self._grid_pic(image)
            grid_image.save(os.path.join(self.args.outpath, f'grid-{grid_count:04}.png'))
            grid_count += 1

        for img in image:
            img.save(os.path.join(sample_path, f"{base_count:05}.png"))
            pic_path.append(os.path.join(os.getcwd(),sample_path, f"{base_count:05}.png"))
            base_count += 1
            

        print(f"Your samples are ready and waiting for you here: \n{self.args.outpath} \n"
          f" \nEnjoy.")
        return pic_path


    def change_lora(self,lora_location,lora_scale):
        self.pipeline.unload_lora_weights()
        self.pipeline.load_lora_weights(lora_location,lora_scale=lora_scale)

    def _accelerate(self):
        if self.args.accelerate == 'xformers':
            self.pipeline.enable_xformers_memory_efficient_attention()

    def _grid_pic(self,image):
        width,height = image[0].size
        nums = len(image)
        rows,cols = int(math.ceil(nums/int(nums**0.5))),int(nums**0.5)
        new_width,new_height = rows*width, cols*height
        new_Image = Image.new('RGB',(new_width,new_height))

        for i in range(nums):
            new_Image.paste(image[i],box = (i%rows*width,i//rows*height))
        
        return new_Image

if __name__ == '__main__':
    
    sd = sdmodels(args)
    while True:
        path = sd.inference(input('Prompt: '))
        print(path)
        for pth in path:
            wallpaper.main(pth)