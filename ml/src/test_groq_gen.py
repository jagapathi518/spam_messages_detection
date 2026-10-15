import os, time, json
from dotenv import load_dotenv
from groq import Groq

load_dotenv('backend/.env')
client = Groq()

for model in ['qwen/qwen3.8-27b', 'openai/gpt-oss-20b']:
    print(f"Testing model: {model}...")
    try:
        t0 = time.time()
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": 'Output a JSON object with a key "messages" containing a list of 3 spam SMS texts.'}
            ],
            model=model,
            response_format={"type": "json_object"},
            max_tokens=250
        )
        print(f"Success with {model} in {time.time() - t0:.2f}s:")
        print(resp.choices[0].message.content)
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
