from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
import time

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX_NAME', 'documind-index')

print(f"Deleting index: {index_name}")
try:
    pc.delete_index(index_name)
    print("Index deleted. Waiting 10 seconds...")
    time.sleep(10)
except Exception as e:
    print(f"Error deleting index: {e}")

print(f"Creating new index: {index_name}")
pc.create_index(
    name=index_name,
    dimension=768,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print("Waiting for index to be ready...")
time.sleep(10)

print("✅ Index reset complete!")
