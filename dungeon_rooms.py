#!/usr/bin/env python
import os
import anthropic
import tomllib
from elevenlabs.client import ElevenLabs
import signal

# Load the API keys from settings.toml
with open("settings.toml", "rb") as f:
    config = tomllib.load(f)

client = anthropic.Anthropic(
    api_key=config["API"]["KEY"]
)

# Initialize ElevenLabs client
eleven_labs = ElevenLabs(api_key=config["ELEVEN"]["KEY"])

# Create output directory for audio files
os.makedirs("dungeon_audio", exist_ok=True)

# System prompt for dungeon room descriptions
system_prompt = """You are a master dungeon designer. Create vivid, atmospheric descriptions of fantasy dungeon rooms.
Each description should be 2-3 paragraphs that include:
- Visual details of the room (architecture, lighting, size)
- Sensory information (smells, sounds, temperature)
- Notable features or objects
- A subtle hint about potential danger, treasure, or history
Keep descriptions evocative but concise."""

# Generate three different room descriptions
room_types = [
    "An ancient library filled with forbidden knowledge",
    "A flooded underground chamber with strange carvings",
    "A throne room corrupted by dark magic"
]

# Store descriptions for later text-to-speech conversion
descriptions = []

for i, room_type in enumerate(room_types, 1):
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=300,
        temperature=0.8,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Describe this dungeon room: {room_type}"
                    }
                ]
            }
        ]
    )
    
    # Save the description text
    description = message.content[0].text
    descriptions.append((i, room_type, description))
    
    print(f"=== Room {i}: {room_type} ===\n")
    print(description)
    print("\n" + "="*50 + "\n")

print("Dungeon room descriptions generated, now converting to speech...")

# Default voice to use
voice_name = "Adam"

# Generate text-to-speech files
for i, room_type, description in descriptions:
    # Clean room type for filename
    clean_name = room_type.replace(" ", "_").replace(":", "").lower()
    filename = f"dungeon_audio/room_{i}_{clean_name}.mp3"
    
    print(f"Converting Room {i} to speech...")
    try:
        # Generate audio - this returns a generator
        audio_stream = eleven_labs.generate(
            text=description,
            voice=voice_name
        )
        
        # Collect all chunks from the generator
        audio_data = b"".join(chunk for chunk in audio_stream)
        
        # Save to file
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {filename}")
    except Exception as e:
        print(f"Error generating speech for Room {i}: {e}")

print("Dungeon room descriptions and audio files complete!")