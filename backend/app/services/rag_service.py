from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.node_parser import SentenceSplitter
from pinecone import Pinecone, ServerlessSpec
import logging
from typing import List, Optional
from app.core.config import get_settings
import time
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class RAGService:
    """Service for RAG operations using LlamaIndex and Pinecone"""
    
    def __init__(self):
        self.settings = settings
        self.pc = None
        self.pinecone_index = None
        self.vector_store = None
        self.storage_context = None
        self.llm = None
        self.embed_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone, embeddings, and LLM"""
        try:
            logger.info("Initializing RAG Service...")
            logger.info(f"Using LLM Model: {self.settings.LLM_MODEL}")
            logger.info(f"Using Embedding Model: {self.settings.EMBEDDING_MODEL}")
            
            self.pc = Pinecone(api_key=self.settings.PINECONE_API_KEY)
            index_name = self.settings.PINECONE_INDEX_NAME
            
            try:
                existing_indexes = self.pc.list_indexes()
                if hasattr(existing_indexes, 'indexes'):
                    index_names = [idx.name for idx in existing_indexes.indexes]
                else:
                    index_names = [idx['name'] for idx in existing_indexes]
            except Exception as e:
                logger.warning(f"Error listing indexes: {e}")
                index_names = []
            
            if index_name not in index_names:
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Waiting for index to be ready...")
                time.sleep(10)
            
            self.pinecone_index = self.pc.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            
            self.vector_store = PineconeVectorStore(
                pinecone_index=self.pinecone_index
            )
            
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            
            self.embed_model = GeminiEmbedding(
                model_name=self.settings.EMBEDDING_MODEL,
                api_key=self.settings.GOOGLE_API_KEY
            )
            
            # Use higher temperature for more natural responses
            self.llm = Gemini(
                model_name=self.settings.LLM_MODEL,
                api_key=self.settings.GOOGLE_API_KEY,
                temperature=0.8  # Increased for more engaging responses
            )
            
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            Settings.chunk_size = self.settings.CHUNK_SIZE
            Settings.chunk_overlap = self.settings.CHUNK_OVERLAP
            
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG Service: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def index_documents(self, documents: List, doc_id: str) -> bool:
        """Index documents into Pinecone"""
        try:
            logger.info(f"Starting indexing for doc_id: {doc_id}")
            logger.info(f"Number of documents to index: {len(documents)}")
            
            for doc in documents:
                if not hasattr(doc, 'metadata') or doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["doc_id"] = doc_id
                logger.info(f"Document text length: {len(doc.text)}")
            
            node_parser = SentenceSplitter(
                chunk_size=self.settings.CHUNK_SIZE,
                chunk_overlap=self.settings.CHUNK_OVERLAP
            )
            
            nodes = node_parser.get_nodes_from_documents(documents)
            
            logger.info(f"Created {len(nodes)} nodes from documents")
            
            if len(nodes) == 0:
                logger.error("No nodes created from documents!")
                raise ValueError("Failed to create nodes from documents")
            
            logger.info("Creating VectorStoreIndex...")
            index = VectorStoreIndex(
                nodes,
                storage_context=self.storage_context,
                show_progress=True
            )
            
            logger.info(f"Successfully indexed document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def _clean_mermaid_code(self, text: str) -> Optional[str]:
        """Extract and clean Mermaid code from response"""
        try:
            if "MERMAID_START" in text and "MERMAID_END" in text:
                parts = text.split("MERMAID_START")
                if len(parts) > 1:
                    mermaid_part = parts[1].split("MERMAID_END")[0]
                    code = mermaid_part.strip()
                    
                    code = re.sub(r'```mermaid\n?', '', code)
                    code = re.sub(r'```\n?', '', code)
                    code = code.strip()
                    
                    if not code.startswith(('graph', 'flowchart')):
                        code = 'graph TD\n' + code
                    
                    code = code.replace('"', "'")
                    
                    logger.info(f"Cleaned Mermaid code:\n{code}")
                    return code
            
            return None
        except Exception as e:
            logger.error(f"Error cleaning Mermaid code: {e}")
            return None
    
    def query(
        self, 
        query_text: str, 
        doc_ids: Optional[List[str]] = None,
        return_mindmap: bool = False
    ) -> dict:
        """Query the RAG system"""
        try:
            logger.info(f"Querying: {query_text}")
            logger.info(f"Document IDs for filtering: {doc_ids}")
            
            index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            should_mindmap = return_mindmap or self._should_generate_mindmap(query_text)
            
            # Build query engine - simplified without filtering
            query_engine = index.as_query_engine(
                similarity_top_k=self.settings.TOP_K,
                response_mode="tree_summarize"
            )
            
            logger.info(f"Query engine created with TOP_K={self.settings.TOP_K}")
            
            if should_mindmap:
                mindmap_query = f"""Based on the document content, create a clear mind map about: {query_text}

RESPONSE FORMAT (STRICT):
First, write 2-3 sentences explaining the topic naturally.

Then write exactly: MERMAID_START
Then write the mermaid code starting with: graph TD
Then write exactly: MERMAID_END

MERMAID RULES:
- Use simple labels (3-5 words max)
- Use single quotes only
- No special characters in labels
- Use clear hierarchy
- Maximum 10 nodes

Example:
The UAV project focuses on detecting corrosion using advanced sensors.

MERMAID_START
graph TD
    A[UAV System] --> B[Hardware]
    A --> C[Software]
    B --> D[ZED2 Camera]
    B --> E[LiDAR]
    C --> F[AI Processing]
MERMAID_END
"""
                response = query_engine.query(mindmap_query)
            else:
                
                # IMPROVED PROMPT FOR CONCISE RESPONSES
                full_query = f"""Answer this question directly and concisely based on the document data provided.

Question: {query_text}

INSTRUCTIONS:
- Give a direct, focused answer (2-4 sentences for simple questions)
- For CAD drawings, be specific about what you see in the data
- If asking about visual elements, use the visual analysis data
- If asking about text/dimensions, cite specific entities
- Don't explain what you CAN'T see - focus on what IS in the data
- Be technical but clear
- If the data doesn't contain the answer, say so briefly

IMPORTANT: Base your answer ONLY on the document data provided. Be concise and specific."""
                
                
                logger.info(f"Sending query to LLM...")
                response = query_engine.query(full_query)
            
            response_text = str(response)
            logger.info(f"Raw response length: {len(response_text)}")
            
            mermaid_code = self._clean_mermaid_code(response_text)
            
            if mermaid_code:
                response_text = response_text.split("MERMAID_START")[0].strip()
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                logger.info(f"Retrieved {len(response.source_nodes)} source nodes")
                sources = [
                    node.metadata.get('file_name', 'Unknown')
                    for node in response.source_nodes
                ]
            
            logger.info(f"Query completed. Response length: {len(response_text)}, Has mindmap: {mermaid_code is not None}")
            
            # Check for too-short responses
            if len(response_text) < 50 and not mermaid_code:
                logger.warning(f"Response too short ({len(response_text)} chars)")
                response_text = "I apologize, but I'm having trouble generating a proper response. This could be due to API limitations or the query not matching the document content well. Could you try rephrasing your question or asking something more specific about the document?"
            
            return {
                "response": response_text,
                "has_mindmap": mermaid_code is not None,
                "mermaid_code": mermaid_code,
                "sources": list(set(sources))
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            logger.exception("Full traceback:")
            
            # Better error messages
            error_msg = str(e)
            if "500" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                response_text = "⚠️ I've hit the API rate limit. Please wait a minute and try again. If this persists, you may need to check your Gemini API quota at https://aistudio.google.com/app/apikey"
            else:
                response_text = f"I encountered an error: {error_msg}. Please try again with a different question."
            
            return {
                "response": response_text,
                "has_mindmap": False,
                "mermaid_code": None,
                "sources": []
            }
    
    def _should_generate_mindmap(self, query: str) -> bool:
        """Determine if query is asking for a mind map"""
        mindmap_keywords = [
            'mind map', 'mindmap', 'diagram', 'structure', 
            'visualize', 'visualization', 'chart', 'graph',
            'relationship', 'overview', 'flow', 'map out'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in mindmap_keywords)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        try:
            logger.info(f"Deleting document from Pinecone: {doc_id}")
            
            # Delete all vectors with this doc_id
            self.pinecone_index.delete(filter={"doc_id": doc_id})
            
            logger.info(f"Successfully deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {str(e)}")
            return False

rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        logger.info("Creating RAG service instance...")
        rag_service = RAGService()
    return rag_service
