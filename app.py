import ssl
import certifi
import os
import httpx

# Monkey patch httpx to disable SSL verification (temporary fix for macOS SSL issues)
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

# Fix SSL certificate issue on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google import genai

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("Please set the GOOGLE_API_KEY in the .env file")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-pro-latest",
    contents='Is Gemini 1.5 Pro better than GPT-4?'
)

print(response.text)
