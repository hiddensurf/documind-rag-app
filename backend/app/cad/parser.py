"""
DXF Parser - Main parser that creates JSON manifests
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)

class DXFParser:
    """Parse DXF files and generate JSON manifests"""
    
    def __init__(self, manifest_dir: str = "cad_manifests"):
        self.manifest_dir = Path(manifest_dir)
        self.manifest_dir.mkdir(exist_ok=True)
        self.extractor = EntityExtractor()
        
    def parse(self, dxf_path: str, file_id: str, source_file: str) -> Dict[str, Any]:
        """
        Parse DXF file and create manifest
        
        Args:
            dxf_path: Path to DXF file
            file_id: Unique file identifier
            source_file: Original filename
            
        Returns:
            Manifest dictionary
        """
        try:
            logger.info(f"Parsing DXF file: {dxf_path}")
            
            # Extract entities and metadata
            extracted_data = self.extractor.extract_all(dxf_path)
            
            # Build manifest
            manifest = self._build_manifest(
                file_id, source_file, extracted_data, "success"
            )
            
            # Save manifest
            manifest_path = self._save_manifest(manifest, file_id)
            logger.info(f"Manifest saved: {manifest_path}")
            
            return manifest
            
        except Exception as e:
            logger.error(f"Error parsing DXF: {str(e)}")
            
            # Create fallback manifest for failed conversion
            manifest = self._build_fallback_manifest(file_id, source_file, str(e))
            manifest_path = self._save_manifest(manifest, file_id)
            
            return manifest
    
    def _build_manifest(
        self, file_id: str, source_file: str, 
        extracted_data: Dict, status: str
    ) -> Dict[str, Any]:
        """Build complete manifest structure"""
        
        return {
            "file_id": file_id,
            "sheet_id": "Model",  # DXF typically has one main sheet
            "source_file": source_file,
            "conversion_status": status,
            "parsed_at": datetime.now().isoformat(),
            "units": extracted_data["metadata"]["units"],
            "scale": extracted_data["metadata"]["scale"],
            "dxf_version": extracted_data["metadata"]["dxf_version"],
            "extents": extracted_data["extents"],
            "layers": extracted_data["layers"],
            "entities": extracted_data["entities"],
            "statistics": extracted_data["statistics"]
        }
    
    def _build_fallback_manifest(
        self, file_id: str, source_file: str, error: str
    ) -> Dict[str, Any]:
        """Build fallback manifest for failed conversions"""
        
        return {
            "file_id": file_id,
            "sheet_id": "Model",
            "source_file": source_file,
            "conversion_status": "conversion_failed",
            "error_message": error,
            "parsed_at": datetime.now().isoformat(),
            "units": "unknown",
            "scale": 1.0,
            "dxf_version": "unknown",
            "extents": {"min": [0, 0], "max": [0, 0]},
            "layers": [],
            "entities": [],
            "statistics": {
                "total_entities": 0,
                "text_entities": 0,
                "dimension_entities": 0
            }
        }
    
    def _save_manifest(self, manifest: Dict, file_id: str) -> str:
        """Save manifest to JSON file"""
        manifest_path = self.manifest_dir / f"{file_id}_Model.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(manifest_path)
    
    def extract_text_for_rag(self, manifest: Dict) -> str:
        """
        Extract all text content from manifest for RAG indexing
        
        Returns:
            Combined text string with layer and entity type context
        """
        if manifest["conversion_status"] == "conversion_failed":
            return f"CAD file conversion failed: {manifest.get('error_message', 'Unknown error')}"
        
        text_parts = []
        
        # Add file metadata
        text_parts.append(f"CAD Drawing: {manifest['source_file']}")
        text_parts.append(f"Units: {manifest['units']}")
        text_parts.append(f"Layers: {', '.join(manifest['layers'])}")
        text_parts.append("")
        
        # Add entity text grouped by layer
        layer_texts = {}
        
        for entity in manifest["entities"]:
            if entity.get("raw_text"):
                layer = entity["layer"]
                if layer not in layer_texts:
                    layer_texts[layer] = []
                
                entity_type = entity["type"]
                text = entity["raw_text"]
                layer_texts[layer].append(f"[{entity_type}] {text}")
        
        # Format by layer
        for layer, texts in layer_texts.items():
            text_parts.append(f"Layer '{layer}':")
            text_parts.extend(texts)
            text_parts.append("")
        
        # Add statistics
        stats = manifest["statistics"]
        text_parts.append(f"Total entities: {stats['total_entities']}")
        text_parts.append(f"Text entities: {stats['text_entities'] + stats.get('mtext_entities', 0)}")
        text_parts.append(f"Dimension entities: {stats['dimension_entities']}")
        
        return "\n".join(text_parts)
