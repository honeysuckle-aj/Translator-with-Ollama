# Translation Script using Ollama
from ollama import chat
from colorama import Fore, Back, Style
from langid import classify
# from ollama import ChatResponse

while(True):
    # s = "hello world"
    s = input()
    lang = classify(s)
    if lang[0] == 'zh':
        target = 'English'
    else:
        target = 'Chinese'
    stream = chat(
        model="qwen2.5",
        messages=
        [
            {
                'role': 'system',
                'content': 'you are a professional and talented translator, you just reply the translated sentences.'
            },
            {
                'role': 'user', 
                'content': f"translate the sentence into {target}: {s}."
            }
        ],
        stream=True
        )
    print(Fore.WHITE + f"Translate {lang[0]} into {target}:")
    for chunk in stream:
        print(Fore.GREEN+Style.BRIGHT+chunk['message']['content'], end='', flush=True)
    print("\n")
