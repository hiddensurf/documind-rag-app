# Phase 1: CAD File Processing for DocuMind

## Overview

This module adds CAD file (DWG/DXF) processing capabilities to DocuMind, enabling:
- Upload and parsing of CAD drawings
- Text extraction from CAD entities (TEXT, MTEXT, DIMENSIONS)
- SVG rendering for browser visualization
- RAG-based querying of CAD content

## Architecture

```
CAD Processing Pipeline:
1. Upload DWG/DXF → 2. Convert to DXF → 3. Parse Entities → 4. Generate Manifest
                                                               ↓
5. Index Text in RAG ← 6. Render to SVG ← ──────────────────┘
```

## Installation

### 1. Install Python Dependencies

```bash
cd ~/documind-rag-app/backend
source venv/bin/activate
pip install ezdxf==1.1.3 pyparsing==3.1.1 svgwrite==1.4.3 matplotlib==3.8.2
pip freeze > requirements.txt
```

### 2. Verify Installation

```bash
python -c "import ezdxf; print('ezdxf version:', ezdxf.version)"
python -c "import matplotlib; print('matplotlib installed')"
```

## Directory Structure

```
backend/
├── app/
│   ├── cad/
│   │   ├── converter.py        # DWG→DXF conversion
│   │   ├── entity_extractor.py # Extract entities from DXF
│   │   ├── parser.py            # Generate JSON manifests
│   │   └── renderer.py          # Render DXF to SVG
│   └── utils/
│       └── cad_loader.py        # Integration with document service
├── cad_uploads/                 # Uploaded CAD files
├── cad_manifests/               # Generated JSON manifests
├── cad_renders/                 # SVG renders
├── schema/
│   └── manifest_example.json   # Example manifest structure
└── tests/
    ├── test_cad_parser.py      # Automated tests
    └── test_parser_validation.md # Test documentation
```

## Usage

### Standalone CAD Processing

```bash
# Start Python shell
cd ~/documind-rag-app/backend
source venv/bin/activate
python
```

```python
from app.cad.converter import CADConverter
from app.cad.parser import DXFParser
from app.cad.renderer import CADRenderer

# Convert DWG to DXF (or validate DXF)
converter = CADConverter()
success, dxf_path, error = converter.convert("path/to/drawing.dxf")

if success:
    # Parse DXF to manifest
    parser = DXFParser()
    manifest = parser.parse(dxf_path, "file123", "drawing.dxf")
    print(f"Parsed {manifest['statistics']['total_entities']} entities")
    
    # Extract text for RAG
    text = parser.extract_text_for_rag(manifest)
    print(f"Extracted {len(text)} characters for RAG")
    
    # Render to SVG
    renderer = CADRenderer()
    svg_path = renderer.render_to_svg(dxf_path, "file123")
    print(f"Rendered to: {svg_path}")
```

### Integrated with DocuMind

CAD files are automatically processed when uploaded through the document service:

1. **Upload CAD file** → Backend receives DWG/DXF
2. **Conversion** → Converts to DXF if needed
3. **Parsing** → Extracts entities, generates manifest
4. **Rendering** → Creates SVG for UI
5. **Indexing** → Text content indexed in Pinecone
6. **Querying** → Users can query CAD content via chat

## Manifest Schema

See `schema/manifest_example.json` for complete structure. Key fields:

```json
{
  "file_id": "unique_id",
  "sheet_id": "Model",
  "conversion_status": "success",
  "units": "millimeters",
  "scale": 1.0,
  "extents": {
    "min": [x1, y1],
    "max": [x2, y2]
  },
  "entities": [
    {
      "id": "ent_000001",
      "type": "TEXT",
      "raw_text": "Sample Text",
      "layer": "TEXT",
      "bbox_world": [x1, y1, x2, y2],
      "bbox_norm": [0..1, 0..1, 0..1, 0..1],
      "extra": { ... }
    }
  ],
  "statistics": {
    "total_entities": 145,
    "text_entities": 23,
    "dimension_entities": 18
  }
}
```

## Running Tests

### Automated Test Suite

```bash
cd ~/documind-rag-app/backend
source venv/bin/activate
python -m pytest tests/test_cad_parser.py -v
```

**Expected Output:**
```
tests/test_cad_parser.py::test_manifest_completeness PASSED
tests/test_cad_parser.py::test_entity_structure PASSED
tests/test_cad_parser.py::test_entity_extraction_sanity PASSED
tests/test_cad_parser.py::test_text_extraction_for_rag PASSED
tests/test_cad_parser.py::test_bbox_validity PASSED

========================= 5 passed in 1.23s =========================
```

### Manual Validation

See `tests/test_parser_validation.md` for detailed test checklist.

## Logs and Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Conversion Logs

Conversion failures are logged with detailed error messages:
```
ERROR - DWG conversion failed: Unsupported DWG version R2024
```

### Inspect Manifests

```bash
# View generated manifest
cat cad_manifests/file123_Model.json | jq '.statistics'
```

### Verify SVG Output

```bash
# Check SVG file
ls -lh cad_renders/file123.svg
```

## Supported File Types

| Format | Extension | Support Level | Notes |
|--------|-----------|---------------|-------|
| DXF | `.dxf` | ✅ Full | All DXF versions supported |
| DWG | `.dwg` | ⚠️ Limited | R2000-R2018 only (via ezdxf) |

**Recommendation:** Export DWG files to DXF format for best compatibility.

## Supported Entity Types

### Text Entities (extracted for RAG)
- `TEXT` - Single-line text
- `MTEXT` - Multi-line text
- `DIMENSION` - Dimension annotations

### Geometric Entities (counted but text not extracted)
- `LINE` - Lines and polylines
- `CIRCLE` - Circles
- `ARC` - Arcs
- `ELLIPSE` - Ellipses
- Others - Splines, hatches, blocks, etc.

## Error Handling

### Conversion Failures

If DWG conversion fails, a fallback manifest is created:
```json
{
  "conversion_status": "conversion_failed",
  "error_message": "Please export to DXF format",
  "entities": []
}
```

### Invalid DXF Files

Invalid or corrupted DXF files are detected and logged:
```
ERROR - Invalid DXF file: Syntax error at line 42
```

## Performance

| File Size | Entities | Parse Time | Render Time |
|-----------|----------|------------|-------------|
| Small (<100KB) | <100 | ~0.5s | ~1s |
| Medium (100KB-1MB) | 100-1000 | ~2s | ~3s |
| Large (>1MB) | >1000 | ~5s | ~10s |

## Limitations

1. **DWG Support**: Limited to older DWG versions (R2000-R2018)
2. **3D Entities**: Only 2D entities supported (Z-axis ignored)
3. **Complex Blocks**: Nested blocks may not render correctly
4. **Large Files**: Files >10MB may be slow to render

## Troubleshooting

### Issue: "DWG conversion failed"
**Solution:** Export the file to DXF format from AutoCAD or similar software.

### Issue: "No entities extracted"
**Solution:** Check if the file is empty or uses only unsupported entity types.

### Issue: "SVG render failed"
**Solution:** Check if matplotlib is installed correctly. Try rendering to PNG as fallback.

### Issue: "Out of memory"
**Solution:** Reduce DXF file size or increase server memory.

## Next Steps (Phase 2)

1. **Frontend Integration**: CAD viewer component with pan/zoom
2. **Advanced Queries**: Layer-specific, dimension-based queries
3. **Batch Processing**: Upload multiple CAD files at once
4. **Export Features**: Export manifests, entity lists
5. **3D Support**: Handle 3D DXF files

## Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review test validation checklist
3. Examine generated manifests
4. Enable debug logging for detailed output

---

**Phase 1 Complete** ✅
CAD processing engine ready for integration with DocuMind RAG system.
