import tiktoken
import os
import torch
import pickle

from shared.nano_gpt.model import GPTConfig, GPT
# from shared.nano_gpt.trainer import encode_training_documents
from contextlib import nullcontext


def generate_text_from_gpt_model(
        model,
        device='cpu',
        seed=1337,
        num_samples=1,
        max_new_tokens=10000,
        temperature=0.8,
        top_k=200,
        start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, use as: "FILE:prompt.txt"
):

    dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
    torch.manual_seed(seed)

    device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
    ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
    ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

    enc = tiktoken.get_encoding("gpt2")

    print("inference from",start)
    start_ids = enc.encode_ordinary(start)

    encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
    decode = lambda l: enc.decode(l)
    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

    model.eval()
    # run generation
    samples=[]
    with torch.no_grad():
        with ctx:
            for k in range(num_samples):
                y = model.generate(x, max_new_tokens,
                                   encoder=enc,
                                   temperature=temperature,
                                   top_k=top_k)
                samples.append(decode(y[0].tolist()).replace("<|endoftext|>",""))
    return samples
