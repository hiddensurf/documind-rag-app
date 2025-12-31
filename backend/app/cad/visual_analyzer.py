"""
Visual Analyzer - Analyze CAD drawings using Computer Vision and Gemini Vision
"""
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io

logger = logging.getLogger(__name__)

class CADVisualAnalyzer:
    """Analyze CAD drawings visually using Gemini Vision"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def analyze_cad_visual(
        self, 
        svg_path: str, 
        manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze CAD drawing visually using Gemini Vision
        
        Args:
            svg_path: Path to SVG render
            manifest: CAD manifest with entity data
            
        Returns:
            Dictionary with visual analysis
        """
        try:
            logger.info(f"Starting visual analysis of CAD: {svg_path}")
            
            # Convert SVG to PNG for vision analysis
            png_path = self._convert_svg_to_png(svg_path)
            if not png_path:
                return self._create_fallback_analysis(manifest)
            
            # Load image
            image = Image.open(png_path)
            
            # Create analysis prompt
            prompt = self._create_visual_prompt(manifest)
            
            # Analyze with Gemini Vision
            logger.info("Calling Gemini Vision for analysis...")
            response = self.vision_model.generate_content([prompt, image])
            
            visual_description = response.text
            logger.info(f"Visual analysis completed: {len(visual_description)} chars")
            
            # Combine with entity data
            combined_analysis = self._combine_analyses(
                visual_description, 
                manifest
            )
            
            return {
                "success": True,
                "visual_description": visual_description,
                "combined_analysis": combined_analysis,
                "image_path": png_path
            }
            
        except Exception as e:
            logger.error(f"Error in visual analysis: {str(e)}")
            logger.exception("Full traceback:")
            
            return {
                "success": False,
                "error": str(e),
                "visual_description": "",
                "combined_analysis": self._create_fallback_analysis(manifest)
            }
    
    def _convert_svg_to_png(self, svg_path: str) -> Optional[str]:
        """Convert SVG to PNG for vision analysis"""
        try:
            import cairosvg
            
            png_path = svg_path.replace('.svg', '_analysis.png')
            
            # Convert with high resolution for better analysis
            cairosvg.svg2png(
                url=svg_path,
                write_to=png_path,
                output_width=1200,
                output_height=900
            )
            
            logger.info(f"Converted SVG to PNG: {png_path}")
            return png_path
            
        except Exception as e:
            logger.error(f"Error converting SVG to PNG: {e}")
            
            # Fallback: Try with PIL
            try:
                from PIL import Image
                from io import BytesIO
                import cairosvg
                
                png_data = cairosvg.svg2png(url=svg_path)
                image = Image.open(BytesIO(png_data))
                
                png_path = svg_path.replace('.svg', '_analysis.png')
                image.save(png_path, 'PNG')
                
                return png_path
            except Exception as e2:
                logger.error(f"Fallback conversion failed: {e2}")
                return None
    
    def _create_visual_prompt(self, manifest: Dict) -> str:
        """Create prompt for Gemini Vision analysis"""
        
        stats = manifest.get("statistics", {})
        layers = manifest.get("layers", [])
        units = manifest.get("units", "unknown")
        
        prompt = f"""Analyze this CAD/technical drawing image. Be specific and concise.

Drawing Stats:
- Units: {units}
- Entities: {stats.get('total_entities', 0)}
- Layers: {len(layers)}

Provide a clear, technical description (3-5 sentences):
1. Drawing type (mechanical part, circuit, building plan, etc.)
2. Main components visible
3. Overall layout/arrangement
4. Key features or notable elements

Be direct and factual. Focus on what IS visible, not what could be there."""
        
        return prompt
    
    def _combine_analyses(
        self, 
        visual_description: str, 
        manifest: Dict
    ) -> str:
        """Combine visual analysis with entity data"""
        
        # Extract text entities
        text_entities = []
        for entity in manifest.get("entities", []):
            if entity.get("raw_text"):
                layer = entity.get("layer", "unknown")
                text = entity["raw_text"]
                text_entities.append(f"[{layer}] {text}")
        
        # Build combined description
        parts = [
            "=== CAD DRAWING ANALYSIS ===\n",
            f"File: {manifest.get('source_file', 'Unknown')}",
            f"Status: {manifest.get('conversion_status', 'Unknown')}",
            f"Units: {manifest.get('units', 'Unknown')}",
            "",
            "=== VISUAL ANALYSIS ===",
            visual_description,
            "",
            "=== EXTRACTED TEXT & ANNOTATIONS ===",
        ]
        
        if text_entities:
            parts.append(f"Found {len(text_entities)} text annotations:")
            parts.extend(text_entities[:20])  # Limit to 20
            if len(text_entities) > 20:
                parts.append(f"... and {len(text_entities) - 20} more")
        else:
            parts.append("No text annotations found in this drawing.")
        
        parts.append("")
        parts.append("=== STATISTICS ===")
        stats = manifest.get("statistics", {})
        for key, value in stats.items():
            parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(parts)
    
    def _create_fallback_analysis(self, manifest: Dict) -> str:
        """Create fallback analysis without vision"""
        
        stats = manifest.get("statistics", {})
        layers = manifest.get("layers", [])
        
        parts = [
            f"CAD Drawing: {manifest.get('source_file', 'Unknown')}",
            f"Units: {manifest.get('units', 'Unknown')}",
            f"Total Entities: {stats.get('total_entities', 0)}",
            f"Layers: {', '.join(layers)}",
            "",
            "Text Annotations:"
        ]
        
        for entity in manifest.get("entities", []):
            if entity.get("raw_text"):
                parts.append(f"- [{entity.get('layer')}] {entity['raw_text']}")
        
        return "\n".join(parts)