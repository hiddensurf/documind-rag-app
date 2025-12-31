"""
STL Loader - Load and process STL 3D model files
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from llama_index.core import Document

logger = logging.getLogger(__name__)

class STLLoader:
    """Load STL 3D model files and extract metadata"""
    
    def __init__(self):
        pass
    
    def load_stl(self, file_path: str, file_id: str, file_name: str) -> Dict[str, Any]:
        """
        Load STL file and extract metadata
        
        Args:
            file_path: Path to STL file
            file_id: Unique identifier
            file_name: Original filename
            
        Returns:
            Dictionary with documents and metadata
        """
        try:
            import trimesh
            
            logger.info(f"Loading STL file: {file_name}")
            
            # Load STL mesh
            mesh = trimesh.load(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(mesh, file_name)
            
            # Create text description for RAG
            text_content = self._create_text_description(metadata)
            
            # Create LlamaIndex documents
            documents = self._create_documents(text_content, file_id, file_name, metadata)
            
            logger.info(f"STL file loaded successfully: {len(documents)} documents created")
            
            return {
                "success": True,
                "error": None,
                "documents": documents,
                "metadata": metadata,
                "text_content": text_content
            }
            
        except Exception as e:
            logger.error(f"Error loading STL file: {str(e)}")
            logger.exception("Full traceback:")
            
            return {
                "success": False,
                "error": str(e),
                "documents": [],
                "metadata": None,
                "text_content": f"Error processing STL file: {str(e)}"
            }
    
    def _extract_metadata(self, mesh, file_name: str) -> Dict[str, Any]:
        """Extract metadata from STL mesh"""
        try:
            # Get mesh properties
            vertices = mesh.vertices
            faces = mesh.faces
            
            # Calculate bounding box
            bounds = mesh.bounds
            dimensions = bounds[1] - bounds[0]
            
            # Calculate other properties
            volume = mesh.volume if hasattr(mesh, 'volume') else 0
            area = mesh.area if hasattr(mesh, 'area') else 0
            
            metadata = {
                "file_name": file_name,
                "file_type": "stl",
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "bounding_box": {
                    "min": bounds[0].tolist(),
                    "max": bounds[1].tolist(),
                    "dimensions": dimensions.tolist()
                },
                "volume": float(volume),
                "surface_area": float(area),
                "is_watertight": mesh.is_watertight if hasattr(mesh, 'is_watertight') else False,
                "center_of_mass": mesh.center_mass.tolist() if hasattr(mesh, 'center_mass') else [0, 0, 0]
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting STL metadata: {e}")
            return {
                "file_name": file_name,
                "file_type": "stl",
                "error": str(e)
            }
    
    def _create_text_description(self, metadata: Dict) -> str:
        """Create text description from metadata"""
        if "error" in metadata:
            return f"STL file: {metadata['file_name']} (Error: {metadata['error']})"
        
        dims = metadata["bounding_box"]["dimensions"]
        
        text_parts = [
            f"3D Model: {metadata['file_name']}",
            "",
            "Model Statistics:",
            f"- Vertices: {metadata['vertex_count']:,}",
            f"- Faces (Triangles): {metadata['face_count']:,}",
            f"- Dimensions: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} units",
            f"- Volume: {metadata['volume']:.2f} cubic units",
            f"- Surface Area: {metadata['surface_area']:.2f} square units",
            f"- Watertight: {'Yes' if metadata['is_watertight'] else 'No'}",
            "",
            "Bounding Box:",
            f"- Min: ({metadata['bounding_box']['min'][0]:.2f}, {metadata['bounding_box']['min'][1]:.2f}, {metadata['bounding_box']['min'][2]:.2f})",
            f"- Max: ({metadata['bounding_box']['max'][0]:.2f}, {metadata['bounding_box']['max'][1]:.2f}, {metadata['bounding_box']['max'][2]:.2f})",
            f"- Center: ({metadata['center_of_mass'][0]:.2f}, {metadata['center_of_mass'][1]:.2f}, {metadata['center_of_mass'][2]:.2f})"
        ]
        
        return "\n".join(text_parts)
    
    def _create_documents(
        self, text_content: str, file_id: str, 
        file_name: str, metadata: Dict
    ) -> List[Document]:
        """Create LlamaIndex documents"""
        
        doc = Document(
            text=text_content,
            metadata={
                "doc_id": file_id,
                "file_name": file_name,
                "file_type": "stl",
                "vertex_count": metadata.get("vertex_count", 0),
                "face_count": metadata.get("face_count", 0)
            }
        )
        
        return [doc]
