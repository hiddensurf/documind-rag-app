"""
CAD Document Loader - Basic entity extraction only
Advanced vision analysis is triggered on-demand via chat
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from llama_index.core import Document

from app.cad.converter import convert_dwg_to_dxf
from app.cad.entity_extractor import EntityExtractor
from app.cad.parser import DXFParser
from app.cad.renderer import CADRenderer
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CADLoader:
    """Load and process CAD files - basic extraction only"""
    
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.parser = DXFParser(manifest_dir="cad_manifests")
        self.renderer = CADRenderer(render_dir="cad_renders")
        
    def load_cad_file(self, file_path: str, file_id: str, file_name: str) -> Dict[str, Any]:
        """
        Load and process a CAD file (basic extraction)
        Advanced vision analysis is done on-demand via chat
        """
        
        try:
            logger.info(f"🔧 Processing CAD file: {file_name}")
            
            file_ext = Path(file_path).suffix.lower()
            
            # Step 1: Handle DWG conversion
            if file_ext == '.dwg':
                logger.info("Converting DWG to DXF...")
                dxf_path = convert_dwg_to_dxf(file_path, "uploads")
                if not dxf_path:
                    return {
                        "success": False,
                        "documents": [],
                        "text_content": f"DWG file: {file_name}\nConversion to DXF required.",
                        "error": "DWG conversion not available"
                    }
            elif file_ext == '.dxf':
                dxf_path = file_path
            else:
                return {
                    "success": False,
                    "documents": [],
                    "text_content": f"Unsupported CAD format: {file_ext}",
                    "error": f"Unsupported format: {file_ext}"
                }
            
            logger.info(f"Using DXF file: {dxf_path}")
            
            # Step 2: Extract entities
            logger.info("Extracting CAD entities...")
            entity_data = self.entity_extractor.extract_all(dxf_path)
            entities = entity_data.get('entities', [])
            logger.info(f"Found {len(entities)} entities")
            
            # Step 3: Parse and create manifest
            logger.info("Parsing DXF structure...")
            manifest = self.parser.parse(dxf_path, file_id, file_name)
            logger.info(f"Manifest created with {len(manifest.get('layers', []))} layers")
            
            # Step 4: Render to SVG and PNG (for later advanced analysis)
            logger.info("Rendering to SVG...")
            svg_path = self.renderer.render_to_svg(dxf_path, f"{file_id}_render")
            
            if svg_path:
                logger.info(f"SVG rendered: {svg_path}")
                # Convert to PNG for future vision analysis
                png_path = str(Path(svg_path).with_name(f"{file_id}_analysis.png"))
                self._convert_svg_to_png(svg_path, png_path)
                logger.info(f"PNG created: {png_path}")
            else:
                logger.warning(f"SVG rendering failed")
            
            # Step 5: Create Document for RAG (entity data only)
            entity_text = self._format_entities(entities, manifest)
            doc = Document(
                text=entity_text,
                metadata={
                    'doc_id': file_id,
                    'file_name': file_name,
                    'file_type': 'cad',
                    'cad_type': file_ext[1:].upper(),
                    'source_type': 'cad_entities',
                    'entity_count': len(entities),
                    'layer_count': len(manifest.get('layers', []))
                }
            )
            
            logger.info(f"✅ CAD file processed successfully")
            
            return {
                "success": True,
                "documents": [doc],
                "text_content": entity_text,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error processing CAD file: {e}", exc_info=True)
            return {
                "success": False,
                "documents": [],
                "text_content": f"CAD file: {file_name}\nError: {str(e)}",
                "error": str(e)
            }
    
    def _format_entities(self, entities: List[Dict], manifest: Dict) -> str:
        """Format entities into searchable text"""
        lines = []
        lines.append("CAD ENTITY DATA")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic info
        lines.append(f"Drawing Units: {manifest.get('units', 'Unknown')}")
        lines.append(f"Total Entities: {len(entities)}")
        
        layers = manifest.get('layers', [])
        if layers:
            layer_names = [layer['name'] for layer in layers[:10]]
            lines.append(f"Layers: {', '.join(layer_names)}")
        lines.append("")
        
        # Group by type
        from collections import defaultdict
        by_type = defaultdict(list)
        for entity in entities:
            ent_type = entity.get('type', 'UNKNOWN')
            by_type[ent_type].append(entity)
        
        # Text content
        text_entities = by_type.get('TEXT', []) + by_type.get('MTEXT', [])
        if text_entities:
            lines.append("TEXT CONTENT")
            lines.append("-" * 80)
            for ent in text_entities[:100]:
                text = ent.get('content', ent.get('raw_text', ''))
                layer = ent.get('layer', 'Unknown')
                if text:
                    lines.append(f"  [{layer}] {text}")
            lines.append("")
        
        # Dimensions
        dimensions = by_type.get('DIMENSION', [])
        if dimensions:
            lines.append("DIMENSIONS")
            lines.append("-" * 80)
            for dim in dimensions[:50]:
                text = dim.get('text', dim.get('raw_text', 'N/A'))
                if text:
                    lines.append(f"  {text}")
            lines.append("")
        
        # Statistics
        lines.append("ENTITY STATISTICS")
        lines.append("-" * 80)
        for ent_type, items in sorted(by_type.items()):
            lines.append(f"  {ent_type}: {len(items)}")
        
        return "\n".join(lines)
    
    def _convert_svg_to_png(self, svg_path: str, png_path: str, dpi: int = 300):
        """Convert SVG to high-resolution PNG"""
        try:
            import cairosvg
            cairosvg.svg2png(
                url=svg_path,
                write_to=png_path,
                dpi=dpi,
                output_width=4096
            )
        except ImportError:
            logger.warning("cairosvg not installed, using fallback")
            try:
                from PIL import Image
                img = Image.new('RGB', (2048, 2048), color='white')
                img.save(png_path)
            except Exception as e:
                logger.error(f"PNG creation failed: {e}")
