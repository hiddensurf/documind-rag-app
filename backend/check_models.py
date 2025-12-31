import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 80)
print("AVAILABLE GEMINI MODELS")
print("=" * 80)

try:
    # List all available models
    models = genai.list_models()
    
    generation_models = []
    embedding_models = []
    
    for model in models:
        print(f"\nModel: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description[:100]}...")
        print(f"  Supported Methods: {model.supported_generation_methods}")
        
        # Categorize models
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model.name)
        if 'embedContent' in model.supported_generation_methods:
            embedding_models.append(model.name)
    
    print("\n" + "=" * 80)
    print("RECOMMENDED MODELS FOR YOUR APP")
    print("=" * 80)
    
    print("\n📝 GENERATION MODELS (for chat/responses):")
    for model in generation_models:
        print(f"  - {model}")
    
    print("\n🔍 EMBEDDING MODELS (for document indexing):")
    for model in embedding_models:
        print(f"  - {model}")
    
    print("\n" + "=" * 80)
    print("TESTING A SIMPLE GENERATION")
    print("=" * 80)
    
    # Try to use a model
    if generation_models:
        test_model_name = generation_models[0]
        print(f"\nTesting: {test_model_name}")
        
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("Say hello in one word")
        print(f"Response: {response.text}")
        print("✅ Model is working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nThis might mean:")
    print("1. Invalid API key")
    print("2. API key doesn't have access to Gemini API")
    print("3. Network connectivity issue")
    print("\nCheck your API key at: https://aistudio.google.com/app/apikey")

