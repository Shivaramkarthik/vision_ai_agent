import ollama

response = ollama.chat(
    model="llava",
    messages=[
        {
            "role": "user",
            "content": "Describe what is on this screen",
            "images": ["screenshots/test.png"]
        }
    ]
)

print(response["message"]["content"])