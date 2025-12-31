from pinecone import Pinecone
import os
from dotenv import load_dotenv
import shutil
from pathlib import Path

load_dotenv()

print("🧹 Starting complete cleanup...")

# 1. Clear Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX_NAME', 'documind-index')

try:
    index = pc.Index(index_name)
    stats_before = index.describe_index_stats()
    print(f"📊 Pinecone vectors before: {stats_before.total_vector_count}")
    
    # Delete all vectors
    index.delete(delete_all=True)
    
    stats_after = index.describe_index_stats()
    print(f"✅ Pinecone vectors after: {stats_after.total_vector_count}")
except Exception as e:
    print(f"⚠️  Pinecone cleanup: {e}")

# 2. Clear uploads
uploads_dir = Path('./uploads')
if uploads_dir.exists():
    for file in uploads_dir.glob('*'):
        if file.is_file():
            file.unlink()
    print("✅ Cleared uploads directory")

# 3. Clear conversations
conv_dir = Path('./conversations')
if conv_dir.exists():
    shutil.rmtree(conv_dir)
    conv_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Cleared conversations")

# 4. Clear document metadata
metadata_file = uploads_dir / 'documents_metadata.json'
if metadata_file.exists():
    metadata_file.unlink()
    print("✅ Cleared document metadata")

print("\n🎉 Complete cleanup finished!")
