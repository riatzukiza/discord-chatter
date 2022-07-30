from threading import Thread
from brain import _ml, speak
ml_process = Thread(target=_ml)
ml_process.start()

for i in range(int(os.environ['SPEECH_THREADS'])):
    speak_process = Thread(target=speak)
    speak_process.start()
