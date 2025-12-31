from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX_NAME', 'documind-index')

print(f"Connecting to index: {index_name}")
index = pc.Index(index_name)

# Get stats before deletion
stats = index.describe_index_stats()
print(f"\nBefore deletion:")
print(f"Total vectors: {stats.total_vector_count}")

# Delete all vectors
print("\nDeleting all vectors...")
index.delete(delete_all=True)

# Get stats after deletion
stats = index.describe_index_stats()
print(f"\nAfter deletion:")
print(f"Total vectors: {stats.total_vector_count}")
print("\n✅ Pinecone index cleared successfully!")
