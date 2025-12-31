# CAD Parser Validation Tests

## Test Checklist

### 1. Conversion Tests
- [ ] **DXF File Handling**: DXF files are processed without conversion
- [ ] **DWG Conversion**: DWG files attempt conversion to DXF
- [ ] **Conversion Failure Handling**: Failed conversions create fallback manifest
- [ ] **File Validation**: Invalid DXF files are detected and logged

### 2. Manifest Completeness Tests
- [ ] **Required Fields Present**: Every manifest contains:
  - `file_id`
  - `sheet_id`
  - `conversion_status`
  - `units`
  - `scale`
  - `extents` (with `min` and `max`)
  - `entities[]`
- [ ] **Extents Validity**: Extents have valid numeric coordinates
- [ ] **Layer List**: Layers array is populated
- [ ] **Statistics**: Statistics object contains all counters

### 3. Entity Extraction Tests
- [ ] **TEXT Entities**: All TEXT entities are detected
- [ ] **MTEXT Entities**: Multi-line text is captured
- [ ] **DIMENSION Entities**: Dimensions are extracted with measurements
- [ ] **Geometric Entities**: Lines, circles, arcs are counted
- [ ] **Layer Attribution**: Each entity has correct layer assignment
- [ ] **Bounding Boxes**: Both world and normalized coordinates present

### 4. Text Extraction for RAG
- [ ] **Text Concatenation**: All text entities are combined
- [ ] **Layer Grouping**: Text is organized by layer
- [ ] **Metadata Inclusion**: File info and statistics included
- [ ] **Empty Handling**: Files with no text don't crash

### 5. Rendering Tests
- [ ] **SVG Generation**: SVG files are created
- [ ] **Valid SVG Format**: Output is valid SVG XML
- [ ] **File Size**: Rendered files are reasonable size (<5MB)

## Sample Assertions

### Python Test Assertions

```python
def test_manifest_completeness(manifest):
    """Test that manifest has all required fields"""
    assert "file_id" in manifest
    assert "sheet_id" in manifest
    assert "conversion_status" in manifest
    assert "extents" in manifest
    assert "min" in manifest["extents"]
    assert "max" in manifest["extents"]
    assert len(manifest["extents"]["min"]) == 2
    assert len(manifest["extents"]["max"]) == 2
    assert "entities" in manifest
    assert isinstance(manifest["entities"], list)
    print("✓ Manifest completeness PASS")

def test_entity_extraction_sanity(manifest):
    """Test that entities are properly extracted"""
    stats = manifest["statistics"]
    
    # At least one entity should exist
    assert stats["total_entities"] > 0, "No entities extracted"
    
    # Text entities check
    text_count = stats["text_entities"] + stats.get("mtext_entities", 0)
    if text_count > 0:
        # Verify text entities have raw_text
        text_entities = [e for e in manifest["entities"] 
                        if e["type"] in ["TEXT", "MTEXT"]]
        assert len(text_entities) > 0
        assert all("raw_text" in e for e in text_entities)
    
    # Dimension entities check
    if stats["dimension_entities"] > 0:
        dim_entities = [e for e in manifest["entities"] 
                       if e["type"] == "DIMENSION"]
        assert len(dim_entities) == stats["dimension_entities"]
    
    print(f"✓ Entity extraction sanity PASS (found {stats['total_entities']} entities)")

def test_bbox_validity(manifest):
    """Test that bounding boxes are valid"""
    for entity in manifest["entities"]:
        bbox_world = entity["bbox_world"]
        bbox_norm = entity["bbox_norm"]
        
        # Check world bbox
        assert len(bbox_world) == 4
        assert all(isinstance(x, (int, float)) for x in bbox_world)
        
        # Check normalized bbox (should be 0-1 range)
        assert len(bbox_norm) == 4
        assert all(0 <= x <= 1 for x in bbox_norm), \
            f"Normalized bbox out of range: {bbox_norm}"
    
    print("✓ Bounding box validity PASS")
```

## Commands to Run Tests

### Run Full Test Suite
```bash
cd ~/documind-rag-app/backend
source venv/bin/activate
python -m pytest tests/test_cad_parser.py -v
```

### Run Specific Tests
```bash
# Test manifest completeness
python -m pytest tests/test_cad_parser.py::test_manifest_completeness -v

# Test entity extraction
python -m pytest tests/test_cad_parser.py::test_entity_extraction_sanity -v

# Test conversion coverage
python -m pytest tests/test_cad_parser.py::test_conversion_coverage -v
```

### Expected Output
```
tests/test_cad_parser.py::test_conversion_coverage PASSED
tests/test_cad_parser.py::test_manifest_completeness PASSED
tests/test_cad_parser.py::test_entity_extraction_sanity PASSED
tests/test_cad_parser.py::test_bbox_validity PASSED

========================= 4 passed in 2.34s =========================
```

## Success Metrics

### Conversion Coverage (≤5% failure rate)
- **Target**: ≤1 failure in 10-file sample
- **Measurement**: Count conversion_status == "conversion_failed"
- **Threshold**: Maximum 5% failure rate

### Manifest Completeness (100%)
- **Target**: All manifests have required fields
- **Measurement**: Check for presence of all required keys
- **Threshold**: 0 missing fields

### Entity Extraction Sanity (≥90% accuracy)
- **Target**: Spot-check accuracy for TEXT/DIMENSION entities
- **Measurement**: Manual verification against source DXF
- **Threshold**: ≥90% of expected entities detected

## Test Data Requirements

Sample files should include:
- Simple DXF (few entities, basic shapes)
- Complex DXF (100+ entities, multiple layers)
- Text-heavy DXF (annotations, dimensions)
- Failed case (corrupted or unsupported version)
