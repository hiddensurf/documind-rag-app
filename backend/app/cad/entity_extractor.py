"""
Entity Extractor - Extract structured data from DXF entities
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace

logger = logging.getLogger(__name__)

class EntityExtractor:
    """Extract entities and metadata from DXF files"""
    
    def __init__(self):
        self.entity_counter = 0
        
    def extract_all(self, dxf_path: str) -> Dict[str, Any]:
        """
        Extract all entities and metadata from DXF file
        
        Returns:
            Dictionary with file metadata and entities
        """
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            # Get file metadata
            metadata = self._extract_metadata(doc)
            
            # Get extents
            extents = self._calculate_extents(msp)
            
            # Extract entities
            entities = self._extract_entities(msp, extents)
            
            # Get layer list
            layers = list(doc.layers.entries.keys())
            
            # Calculate statistics
            stats = self._calculate_statistics(entities)
            
            return {
                "metadata": metadata,
                "extents": extents,
                "layers": layers,
                "entities": entities,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            raise
    
    def _extract_metadata(self, doc: Drawing) -> Dict[str, Any]:
        """Extract file-level metadata"""
        header = doc.header
        
        return {
            "dxf_version": doc.dxfversion,
            "units": self._get_units(header),
            "author": header.get('$AUTHOR', 'Unknown'),
            "title": header.get('$TITLE', 'Untitled'),
            "scale": 1.0  # Default scale
        }
    
    def _get_units(self, header) -> str:
        """Determine drawing units"""
        insunits = header.get('$INSUNITS', 0)
        
        units_map = {
            0: "unitless",
            1: "inches",
            2: "feet",
            4: "millimeters",
            5: "centimeters",
            6: "meters",
            8: "miles",
            9: "microinches",
            10: "mils",
            11: "yards",
            12: "angstroms",
            13: "nanometers",
            14: "microns",
        }
        
        return units_map.get(insunits, "unknown")
    
    def _calculate_extents(self, msp: Modelspace) -> Dict[str, List[float]]:
        """Calculate bounding box of all entities"""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        found_entity = False
        
        for entity in msp:
            try:
                # Try to get bounding box
                if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'insert'):
                    # INSERT (block reference)
                    point = entity.dxf.insert
                    min_x = min(min_x, point.x)
                    max_x = max(max_x, point.x)
                    min_y = min(min_y, point.y)
                    max_y = max(max_y, point.y)
                    found_entity = True
                    
                elif hasattr(entity, 'dxf'):
                    # Try common coordinate attributes
                    for attr in ['start', 'end', 'center', 'location']:
                        if hasattr(entity.dxf, attr):
                            point = getattr(entity.dxf, attr)
                            if hasattr(point, 'x') and hasattr(point, 'y'):
                                min_x = min(min_x, point.x)
                                max_x = max(max_x, point.x)
                                min_y = min(min_y, point.y)
                                max_y = max(max_y, point.y)
                                found_entity = True
                                
            except Exception as e:
                logger.debug(f"Could not process entity for extents: {e}")
                continue
        
        if not found_entity:
            # Default extents if no entities found
            return {"min": [0, 0], "max": [100, 100]}
        
        return {
            "min": [min_x, min_y],
            "max": [max_x, max_y]
        }
    
    def _extract_entities(self, msp: Modelspace, extents: Dict) -> List[Dict[str, Any]]:
        """Extract all entities with normalized coordinates"""
        entities = []
        self.entity_counter = 0
        
        # Calculate normalization factors
        min_x, min_y = extents["min"]
        max_x, max_y = extents["max"]
        width = max_x - min_x if max_x > min_x else 1
        height = max_y - min_y if max_y > min_y else 1
        
        for entity in msp:
            try:
                extracted = self._extract_single_entity(
                    entity, min_x, min_y, width, height
                )
                if extracted:
                    entities.append(extracted)
            except Exception as e:
                logger.debug(f"Could not extract entity: {e}")
                continue
        
        return entities
    
    def _extract_single_entity(
        self, entity, min_x: float, min_y: float, 
        width: float, height: float
    ) -> Optional[Dict[str, Any]]:
        """Extract data from a single entity"""
        self.entity_counter += 1
        entity_id = f"ent_{self.entity_counter:06d}"
        
        entity_type = entity.dxftype()
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else "0"
        
        # Extract based on entity type
        if entity_type == "TEXT":
            return self._extract_text(entity, entity_id, layer, min_x, min_y, width, height)
        elif entity_type == "MTEXT":
            return self._extract_mtext(entity, entity_id, layer, min_x, min_y, width, height)
        elif entity_type == "DIMENSION":
            return self._extract_dimension(entity, entity_id, layer, min_x, min_y, width, height)
        elif entity_type in ["LINE", "POLYLINE", "LWPOLYLINE", "CIRCLE", "ARC", "ELLIPSE"]:
            return self._extract_geometric(entity, entity_id, layer, entity_type, min_x, min_y, width, height)
        else:
            # Generic entity
            return {
                "id": entity_id,
                "type": entity_type,
                "layer": layer,
                "block": None,
                "bbox_world": [0, 0, 0, 0],
                "bbox_norm": [0, 0, 0, 0],
                "extra": {}
            }
    
    def _extract_text(self, entity, entity_id, layer, min_x, min_y, width, height):
        """Extract TEXT entity"""
        text = entity.dxf.text
        insert = entity.dxf.insert
        height_val = entity.dxf.height
        rotation = entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0
        
        # Approximate bbox
        text_width = len(text) * height_val * 0.6
        bbox_world = [insert.x, insert.y, insert.x + text_width, insert.y + height_val]
        bbox_norm = self._normalize_bbox(bbox_world, min_x, min_y, width, height)
        
        return {
            "id": entity_id,
            "type": "TEXT",
            "raw_text": text,
            "layer": layer,
            "block": None,
            "bbox_world": bbox_world,
            "bbox_norm": bbox_norm,
            "extra": {
                "height": height_val,
                "rotation": rotation,
                "style": entity.dxf.style if hasattr(entity.dxf, 'style') else "Standard"
            }
        }
    
    def _extract_mtext(self, entity, entity_id, layer, min_x, min_y, width, height):
        """Extract MTEXT entity"""
        text = entity.text
        insert = entity.dxf.insert
        text_height = entity.dxf.char_height if hasattr(entity.dxf, 'char_height') else 1.0
        
        # Approximate bbox
        lines = text.split('\n')
        text_width = max(len(line) for line in lines) * text_height * 0.6
        text_total_height = len(lines) * text_height * 1.5
        
        bbox_world = [insert.x, insert.y, insert.x + text_width, insert.y + text_total_height]
        bbox_norm = self._normalize_bbox(bbox_world, min_x, min_y, width, height)
        
        return {
            "id": entity_id,
            "type": "MTEXT",
            "raw_text": text,
            "layer": layer,
            "block": None,
            "bbox_world": bbox_world,
            "bbox_norm": bbox_norm,
            "extra": {
                "char_height": text_height,
                "line_count": len(lines)
            }
        }
    
    def _extract_dimension(self, entity, entity_id, layer, min_x, min_y, width, height):
        """Extract DIMENSION entity"""
        text = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
        
        # Get dimension points
        defpoint = entity.dxf.defpoint if hasattr(entity.dxf, 'defpoint') else (0, 0, 0)
        
        bbox_world = [defpoint[0], defpoint[1], defpoint[0] + 50, defpoint[1] + 10]
        bbox_norm = self._normalize_bbox(bbox_world, min_x, min_y, width, height)
        
        return {
            "id": entity_id,
            "type": "DIMENSION",
            "raw_text": text,
            "layer": layer,
            "block": None,
            "bbox_world": bbox_world,
            "bbox_norm": bbox_norm,
            "extra": {
                "dim_type": entity.dimtype if hasattr(entity, 'dimtype') else "UNKNOWN"
            }
        }
    
    def _extract_geometric(self, entity, entity_id, layer, entity_type, min_x, min_y, width, height):
        """Extract geometric entities"""
        bbox_world = [0, 0, 0, 0]
        
        try:
            if entity_type == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                bbox_world = [
                    min(start.x, end.x), min(start.y, end.y),
                    max(start.x, end.x), max(start.y, end.y)
                ]
            elif entity_type == "CIRCLE":
                center = entity.dxf.center
                radius = entity.dxf.radius
                bbox_world = [
                    center.x - radius, center.y - radius,
                    center.x + radius, center.y + radius
                ]
        except Exception as e:
            logger.debug(f"Could not extract bbox for {entity_type}: {e}")
        
        bbox_norm = self._normalize_bbox(bbox_world, min_x, min_y, width, height)
        
        return {
            "id": entity_id,
            "type": entity_type,
            "raw_text": None,
            "layer": layer,
            "block": None,
            "bbox_world": bbox_world,
            "bbox_norm": bbox_norm,
            "extra": {}
        }
    
    def _normalize_bbox(self, bbox_world, min_x, min_y, width, height):
        """Normalize bounding box to 0-1 range"""
        return [
            (bbox_world[0] - min_x) / width,
            (bbox_world[1] - min_y) / height,
            (bbox_world[2] - min_x) / width,
            (bbox_world[3] - min_y) / height
        ]
    
    def _calculate_statistics(self, entities: List[Dict]) -> Dict[str, int]:
        """Calculate entity statistics"""
        stats = {
            "total_entities": len(entities),
            "text_entities": 0,
            "mtext_entities": 0,
            "dimension_entities": 0,
            "line_entities": 0,
            "circle_entities": 0,
            "arc_entities": 0,
            "other_entities": 0
        }
        
        for entity in entities:
            entity_type = entity["type"].lower()
            if entity_type == "text":
                stats["text_entities"] += 1
            elif entity_type == "mtext":
                stats["mtext_entities"] += 1
            elif entity_type == "dimension":
                stats["dimension_entities"] += 1
            elif entity_type == "line" or entity_type == "polyline" or entity_type == "lwpolyline":
                stats["line_entities"] += 1
            elif entity_type == "circle":
                stats["circle_entities"] += 1
            elif entity_type == "arc":
                stats["arc_entities"] += 1
            else:
                stats["other_entities"] += 1
        
        return stats
