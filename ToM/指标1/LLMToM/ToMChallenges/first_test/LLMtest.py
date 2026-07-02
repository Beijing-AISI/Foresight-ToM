from openai import OpenAI

client = OpenAI(
    api_key='token-casia-braincog-233',
    base_url='http://210.75.240.144:3006/v1',
)

chat = client.chat.completions.create(
    model='Qwen/Qwen2.5-72B-Instruct',
    messages=[
        {"role": "user", "content": "你好"}
    ]
)
print(chat.choices[0].message.content)
