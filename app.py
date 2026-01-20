import ssl
import certifi
import os
import httpx
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from google import genai

# Monkey patch httpx to disable SSL verification (temporary fix for macOS SSL issues)
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

# Fix SSL certificate issue on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("Please set the GOOGLE_API_KEY in the .env file")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = client.models.generate_content(
            model="gemini-pro-latest",
            contents=user_message
        )
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
