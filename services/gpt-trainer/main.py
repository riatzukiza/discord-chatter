"""It is where we define the model stuff"""
from time import sleep
from shared.nano_gpt.trainer import train_gpt_model, setup_model
from shared.nano_gpt.generator import generate_text_from_gpt_model
from shared.training_data import get_messages_for_in_order_training
import shared.settings as settings
import os
import json
import shutil
import time

model_path="/app/models/duck_gpt.v0.2.0/"

print("start building model")
model, model_args, iter_num, best_val_loss, checkpoint, scaler,optimizer=setup_model(
    out_dir=model_path,
    device='cuda',
    init_from="resume" if os.path.exists(model_path) and len(os.listdir(model_path)) > 0 else "gpt2-medium",
)
print("building model complete")
while True:
    messages=get_messages_for_in_order_training(400,10)
    print("training on messages ")

    if messages:
        model, model_args, iter_num, best_val_loss, checkpoint, scaler,optimizer=train_gpt_model(
            model, iter_num, best_val_loss, checkpoint, scaler,optimizer,model_args,
            always_save_checkpoint=True,
            out_dir=model_path,
            input_data=messages,
            warmup_iters=2,
            max_iters=10
        )
       
    else:
        print("no messages to train on")
        continue
