# Translation Script using Ollama
from ollama import chat as ollama_chat
from colorama import Fore, Back, Style
from langid import classify
from openai import AzureOpenAI
# from ollama import ChatResponse



with open("api.txt", "r") as f:
    api_ = f.read().strip()
    # print(api_)
    
azure_client = AzureOpenAI(
    api_key=api_,
    api_version="2024-10-21",
    azure_endpoint="https://hkust.azure-api.net"
)

def reply_translation(text, server: str, model: str):
    """_summary_

    Args:
        text (str): text to be translated
        server (str): ollama or azure

    Returns:
        str: 
    """
    lang = classify(text)
    if lang[0] == "zh":
        target = "English"
    else:
        target = "Chinese"
    input_messages = [
            {
                "role": "system",
                "content": "you are a professional and talented translator, you just reply the translated sentences."
            },
            {
                "role": "user", 
                "content": f"translate the sentence into {target}: {text}."
            }
        ]
    if server == "ollama":
        stream = ollama_chat(
            model=model,
            messages=input_messages,
            stream=True
            )
        trans_text = ""
        for chunk in stream:
            trans_text += chunk["message"]["content"]
        return trans_text
    elif server == "azure":
        response = azure_client.chat.completions.create(
            model=model,
            messages=input_messages
        )
        return response.choices[0].message.content
    else:
        print("invalid server")
        

    
if __name__ == "__main__":   
    print("try translation")
    while(True):
        # s = "hello world"
        s = input()
        response = reply_translation(s, "azure", "gpt-4o")
        print(response)
