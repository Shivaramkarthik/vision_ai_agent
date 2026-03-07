import ollama

response = ollama.chat(
    model="llama3:8b",
    messages=[
        {"role": "user", "content": "Say hello briefly"}
    ]
)

print(response["message"]["content"])