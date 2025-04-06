#!/usr/bin/env python
import anthropic, tomllib

with open("settings.toml", "rb") as f:
    config = tomllib.load(f)



client = anthropic.Anthropic(
    api_key=config["API"]["KEY"]
)

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1000,
    temperature=1,
    system="You are a world-class poet. Respond only with short poems.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Why is the ocean salty?"
                }
            ]
        }
    ]
)
print(message.content)
