import os
import shutil
from datetime import datetime
from typing import List
import uuid
import json
import logging
from pathlib import Path
from app.core.config import get_settings
from app.utils.document_loader import DocumentLoader
from app.utils.document_loader import document_loader

logger = logging.getLogger(__name__)
settings = get_settings()

class DocumentService:
    """Service for document management with advanced CAD support"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.upload_dir / "documents_metadata.json"
        self.documents = self._load_metadata()
        
        # Create CAD directories
        self.cad_manifest_dir = Path("cad_manifests")
        self.cad_render_dir = Path("cad_renders")
        self.cad_manifest_dir.mkdir(exist_ok=True)
        self.cad_render_dir.mkdir(exist_ok=True)
        
        logger.info(f"DocumentService initialized. Upload dir: {self.upload_dir}")
    
    def _load_metadata(self) -> dict:
        """Load document metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} documents from metadata")
                    return data
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save document metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
            logger.info(f"Saved metadata for {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _is_cad_file(self, filename: str) -> bool:
        """Check if file is a CAD file"""
        ext = Path(filename).suffix.lower()
        return ext in ['.dxf', '.dwg']
    
    async def upload_document(self, file, filename: str) -> dict:
        """Upload and process document with advanced CAD analysis"""
        file_path = None
        try:
            from app.services.rag_service import get_rag_service
            
            logger.info(f"Starting upload for file: {filename}")
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1]
            saved_filename = f"{doc_id}{file_ext}"
            file_path = self.upload_dir / saved_filename
            
            logger.info(f"Saving file to: {file_path}")
            
            # Save file
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"File saved. Size: {file_size} bytes")
            
            # Check if CAD file
            is_cad = self._is_cad_file(filename)
            
            if is_cad:
                logger.info("🔧 CAD file detected - using ADVANCED analysis pipeline")
            
            # Load document (will use advanced CAD loader if CAD file)
            logger.info("Loading document...")
            documents = document_loader.load_document(str(file_path), doc_id, filename)
            logger.info(f"Loaded {len(documents)} document(s)")
            
            # Index documents
            logger.info("Indexing documents...")
            rag_service = get_rag_service()
            rag_service.index_documents(documents, doc_id)
            logger.info("Documents indexed successfully")
            
            # Store metadata
            doc_metadata = {
                "id": doc_id,
                "name": filename,
                "size": file_size,
                "upload_date": datetime.now().isoformat(),
                "file_path": str(file_path),
                "status": "processed",
                "is_cad": is_cad
            }
            
            # Add CAD-specific metadata if applicable
            if is_cad:
                manifest_path = self.cad_manifest_dir / f"{doc_id}_manifest.json"
                analysis_path = self.cad_manifest_dir / f"{doc_id}_analysis.json"
                svg_path = self.cad_render_dir / f"{doc_id}_render.svg"
                
                if manifest_path.exists():
                    doc_metadata["cad_manifest"] = str(manifest_path)
                if analysis_path.exists():
                    doc_metadata["cad_analysis"] = str(analysis_path)
                    # Load analysis summary for quick access
                    try:
                        with open(analysis_path, 'r') as f:
                            analysis_data = json.load(f)
                            if 'summary' in analysis_data:
                                doc_metadata["analysis_summary"] = analysis_data['summary'].get('executive_summary', '')[:500]
                    except:
                        pass
                if svg_path.exists():
                    doc_metadata["cad_render"] = str(svg_path)
            
            self.documents[doc_id] = doc_metadata
            self._save_metadata()
            
            logger.info(f"Document uploaded successfully: {doc_id}")
            
            return doc_metadata
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            logger.exception("Full traceback:")
            # Clean up file if it exists
            if file_path and file_path.exists():
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up file: {cleanup_error}")
            raise
    
    def get_documents(self) -> List[dict]:
        """Get all documents"""
        return list(self.documents.values())
    
    def get_document(self, doc_id: str) -> dict:
        """Get single document"""
        return self.documents.get(doc_id)
    
    def get_cad_manifest(self, doc_id: str) -> dict:
        """Get CAD manifest for a document"""
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        if not doc.get('is_cad', False):
            return None
        
        manifest_path = self.cad_manifest_dir / f"{doc_id}_manifest.json"
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading CAD manifest: {e}")
            return None
    
    def get_cad_analysis(self, doc_id: str) -> dict:
        """Get advanced CAD analysis for a document"""
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        if not doc.get('is_cad', False):
            return None
        
        analysis_path = self.cad_manifest_dir / f"{doc_id}_analysis.json"
        if not analysis_path.exists():
            return None
        
        try:
            with open(analysis_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading CAD analysis: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and all associated files"""
        try:
            from app.services.rag_service import get_rag_service
            
            logger.info(f"Attempting to delete document: {doc_id}")
            
            if doc_id not in self.documents:
                logger.warning(f"Document not found in metadata: {doc_id}")
                return False
            
            doc = self.documents[doc_id]
            file_path = Path(doc["file_path"])
            
            # Delete from vector store FIRST
            logger.info("Deleting from vector store...")
            rag_service = get_rag_service()
            rag_service.delete_document(doc_id)
            
            # Delete physical file
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            else:
                logger.warning(f"File not found: {file_path}")
            
            # Delete CAD-specific files if they exist
            if doc.get('is_cad', False):
                # Delete manifest
                manifest_path = self.cad_manifest_dir / f"{doc_id}_manifest.json"
                if manifest_path.exists():
                    os.remove(manifest_path)
                    logger.info(f"Deleted CAD manifest: {manifest_path}")
                
                # Delete analysis
                analysis_path = self.cad_manifest_dir / f"{doc_id}_analysis.json"
                if analysis_path.exists():
                    os.remove(analysis_path)
                    logger.info(f"Deleted CAD analysis: {analysis_path}")
                
                # Delete SVG render
                svg_path = self.cad_render_dir / f"{doc_id}_render.svg"
                if svg_path.exists():
                    os.remove(svg_path)
                    logger.info(f"Deleted CAD render: {svg_path}")
                
                # Delete PNG analysis image
                png_path = self.cad_render_dir / f"{doc_id}_analysis.png"
                if png_path.exists():
                    os.remove(png_path)
                    logger.info(f"Deleted CAD PNG: {png_path}")
            
            # Remove from metadata
            del self.documents[doc_id]
            self._save_metadata()
            
            logger.info(f"Document deleted successfully: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            logger.exception("Full traceback:")
            raise

# Singleton instance
document_service = DocumentService()
