import asyncio
import ssl
import certifi
import os
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai.types import SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
import pyaudio

# Monkey patch httpx to disable SSL verification (temporary fix for macOS SSL issues)
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

# Fix SSL certificate issue on macOS
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables from .env file
load_dotenv()

model_id = 'gemini-2.0-flash-exp'

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Fix websocket SSL
client._api_client._websocket_ssl_ctx = {'ssl': ssl._create_unverified_context()}

config = {"response_modalities": ["text"]} # we can add audio in the future

async def chat_with_gemini():
    # live client, the user will talk to the model in real-time
    async with client.aio.live.connect(model=model_id, config=config) as session:
        
        while True:
            # text input from user
            message = input("Enter a message: ")
            await session.send_realtime_input(text=message)

            # voice response from Gemini
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=24000,
                            output=True)

            full_response = ""
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if part.text:
                            full_response += part.text
                        if part.inline_data and part.inline_data.data:
                            stream.write(part.inline_data.data)
            
            if full_response:
                print(f"Gemini: {full_response}")

if __name__ == "__main__":
    asyncio.run(chat_with_gemini())