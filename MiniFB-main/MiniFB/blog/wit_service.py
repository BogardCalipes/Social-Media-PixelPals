import requests
import json

# Set up your Wit.ai API key here
WIT_API_KEY = 'GHPQ5M7XILKXUNCQLGQVPB2CARVHFH5F'

def query_wit_ai(message):
    url = f'https://api.wit.ai/message?v=20231123&q={message}'
    headers = {
        'Authorization': f'Bearer {WIT_API_KEY}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {'error': 'Failed to communicate with Wit.ai'}

