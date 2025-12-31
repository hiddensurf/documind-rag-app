#!/usr/bin/env python3
"""
Quick test script for CAD processing
"""
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.cad.converter import CADConverter
from app.cad.parser import DXFParser
from app.cad.renderer import CADRenderer

def test_cad_pipeline():
    """Test the complete CAD processing pipeline"""
    print("=" * 60)
    print("CAD Processing Pipeline Test")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing components...")
    converter = CADConverter()
    parser = DXFParser()
    renderer = CADRenderer()
    print("   ✓ Components initialized")
    
    # Test with sample manifest
    print("\n2. Loading sample manifest...")
    manifest_path = Path("schema/manifest_example.json")
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"   ✓ Loaded sample manifest")
        print(f"   - File: {manifest['source_file']}")
        print(f"   - Status: {manifest['conversion_status']}")
        print(f"   - Entities: {manifest['statistics']['total_entities']}")
        print(f"   - Text entities: {manifest['statistics']['text_entities']}")
    else:
        print("   ✗ Sample manifest not found")
        return False
    
    # Test text extraction
    print("\n3. Testing text extraction for RAG...")
    text = parser.extract_text_for_rag(manifest)
    print(f"   ✓ Extracted {len(text)} characters")
    print(f"   Preview: {text[:100]}...")
    
    # Test validation
    print("\n4. Running validation checks...")
    checks = {
        "has_file_id": "file_id" in manifest,
        "has_extents": "extents" in manifest and "min" in manifest["extents"],
        "has_entities": "entities" in manifest and len(manifest["entities"]) > 0,
        "has_statistics": "statistics" in manifest,
        "entities_have_bbox": all("bbox_world" in e for e in manifest["entities"][:5])
    }
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"   {status} {check}: {result}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_cad_pipeline()
    sys.exit(0 if success else 1)
