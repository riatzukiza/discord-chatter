from threading import Thread
from .brain import _ml, speak
import os
ml_process = Thread(target=_ml)

generation_threads = []

for i in range(int(os.environ['SPEECH_THREADS'])):
    generation_thread = Thread(target=speak)
    generation_threads.append(generation_thread)

def start_threads():
    ml_process.start()
    for generation_thread in generation_threads:
        generation_thread.start()
