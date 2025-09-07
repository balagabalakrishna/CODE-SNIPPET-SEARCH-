import google.generativeai as genai

# Use your real Gemini API key
genai.configure(api_key="AIzaSyAkF4lh1VIuncDwLKCqlqviGf3cOwO8AaU")

try:
    models = genai.list_models()
    for model in models:
        print(f"Model: {model.name} | Supports: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
