#!/usr/bin/env python3
"""
Generate missing PNG files for existing CAD documents
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.document_service import document_service

def convert_svg_to_png(svg_path: str, png_path: str, dpi: int = 300):
    """Convert SVG to high-resolution PNG"""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            dpi=dpi,
            output_width=4096
        )
        print(f"✅ Created: {png_path}")
        return True
    except ImportError:
        print("⚠️  cairosvg not installed, using fallback...")
        try:
            from PIL import Image
            img = Image.new('RGB', (2048, 2048), color='white')
            img.save(png_path)
            print(f"✅ Created placeholder: {png_path}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False

def main():
    print("🔍 Looking for CAD documents without PNG files...")
    
    documents = document_service.get_documents()
    cad_docs = [doc for doc in documents if doc.get('name', '').lower().endswith(('.dxf', '.dwg'))]
    
    print(f"Found {len(cad_docs)} CAD documents")
    
    generated = 0
    
    for doc in cad_docs:
        doc_id = doc['id']
        doc_name = doc['name']
        
        # Check for SVG
        svg_path = Path(f"cad_renders/{doc_id}_render.svg")
        png_path = Path(f"cad_renders/{doc_id}_analysis.png")
        
        if not svg_path.exists():
            print(f"⚠️  {doc_name}: No SVG found, skipping")
            continue
        
        if png_path.exists():
            print(f"✓ {doc_name}: PNG already exists")
            continue
        
        print(f"🎨 {doc_name}: Generating PNG from SVG...")
        if convert_svg_to_png(str(svg_path), str(png_path)):
            generated += 1
    
    print(f"\n✨ Complete! Generated {generated} new PNG files")

if __name__ == '__main__':
    main()
