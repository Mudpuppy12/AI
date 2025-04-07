# Playing with AI and Claude

## create a settings.toml file with your API Keys
```
[API]
KEY = "YOUR_API_KEY"
[ELEVEN]
KEY = "YOUR_API_KEY"
```

## create python environment, source it, add the required lib, etc
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## dungeon_rooms.py was created with claude with the following prompt:
Wanted to see if I could have AI, write AI to pass to a text to speech AI. 
It worked.

```
Write a python script to generate three ai descriptions using claude of dungeon rooms then use eleven.ai python sdk to generate the text so speech files 
```

## Azure
# General TF creation - See main.tf
```
 create a terraform script to connect to asure and create a linux virtual machine that is reachable from anywhere on the internet over port 22 ssh   
 ```
