#!/usr/bin/env python
import os
import anthropic
import tomllib
from elevenlabs.client import ElevenLabs

# Load the API keys and configuration from settings.toml
def load_config():
    with open("settings.toml", "rb") as f:
        return tomllib.load(f)

def generate_room_description(client, system_prompt, room_type, model="claude-3-7-sonnet-20250219", max_tokens=300, temperature=0.8):
    """Generate a description for a single dungeon room using Claude API"""
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
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
        return message.content[0].text
    except Exception as e:
        print(f"Error generating description for '{room_type}': {e}")
        return None

def generate_audio(eleven_labs, description, voice_name, filename):
    """Generate an audio file from a description using ElevenLabs API"""
    try:
        # Generate audio - this returns a generator
        audio_stream = eleven_labs.generate(
            text=description,
            voice=voice_name
        )
        
        # Stream audio data directly to the file
        with open(filename, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
        print(f"Audio saved to {filename}")
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

def main():
    # Load configuration
    config = load_config()
    
    # Set up API clients
    client = anthropic.Anthropic(
        api_key=config["API"]["KEY"]
    )
    eleven_labs = ElevenLabs(api_key=config["ELEVEN"]["KEY"])
    
    # Get model configuration (use defaults if not in settings)
    model_config = config.get("CLAUDE", {})
    model = model_config.get("MODEL", "claude-3-7-sonnet-20250219")
    max_tokens = model_config.get("MAX_TOKENS", 300)
    temperature = model_config.get("TEMPERATURE", 0.8)
    
    # Get voice configuration (use default if not in settings)
    voice_config = config.get("ELEVEN", {})
    voice_name = voice_config.get("VOICE", "Adam")
    
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
    
    # Room types to generate
    room_types = [
        "An ancient library filled with forbidden knowledge",
        "A flooded underground chamber with strange carvings",
        "A throne room corrupted by dark magic",
        "A cavernous hall with a glowing crystal ceiling"
    ]
    
    # Store descriptions for later text-to-speech conversion
    descriptions = []
    
    print("Generating room descriptions...")
    for i, room_type in enumerate(room_types, 1):
        description = generate_room_description(
            client, system_prompt, room_type, 
            model=model, max_tokens=max_tokens, temperature=temperature
        )
        
        if description:
            descriptions.append((i, room_type, description))
            print(f"=== Room {i}: {room_type} ===\n")
            print(description)
            print("\n" + "="*50 + "\n")
    
    print("Dungeon room descriptions generated, now converting to speech...")
    
    # Generate text-to-speech files
    for i, room_type, description in descriptions:
        # Clean room type for filename
        clean_name = room_type.replace(" ", "_").replace(":", "").lower()
        filename = f"dungeon_audio/room_{i}_{clean_name}.mp3"
        
        print(f"Converting Room {i} to speech...")
        generate_audio(eleven_labs, description, voice_name, filename)
    
    print("Dungeon room descriptions and audio files complete!")

if __name__ == "__main__":
    main()