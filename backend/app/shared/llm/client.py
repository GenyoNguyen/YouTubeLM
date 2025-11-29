import os
from groq import Groq

def generate_completion(prompt: str, system_prompt: str = None, **kwargs):
    """Generate completion using LLM"""
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})

    model = kwargs.get("model", os.environ.get("LLM_MODEL", "openai/gpt-oss-120b"))

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
    )

    for chunk in chat_completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
