"""
DWG to DXF Converter Module
Handles conversion of DWG files to DXF format
"""

import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def convert_dwg_to_dxf(dwg_path: str, output_dir: str) -> str:
    """
    Convert DWG file to DXF format
    
    Currently returns None to indicate manual conversion needed.
    In production, this could use ODA File Converter or LibreDWG.
    
    Args:
        dwg_path: Path to DWG file
        output_dir: Directory to save converted DXF
        
    Returns:
        Path to converted DXF file, or None if conversion not available
    """
    logger.warning("DWG conversion not implemented - manual conversion required")
    logger.info(f"Please convert {dwg_path} to DXF manually")
    
    # For now, we don't support automatic DWG conversion
    # This would require installing ODA File Converter or LibreDWG
    return None


def is_dwg_converter_available() -> bool:
    """
    Check if DWG conversion tools are available
    
    Returns:
        True if conversion is possible, False otherwise
    """
    # Check for ODA File Converter
    oda_paths = [
        '/usr/bin/ODAFileConverter',
        '/opt/ODAFileConverter/ODAFileConverter',
        'C:\\Program Files\\ODA\\ODAFileConverter\\ODAFileConverter.exe'
    ]
    
    for path in oda_paths:
        if os.path.exists(path):
            return True
    
    # Check for LibreDWG
    try:
        result = subprocess.run(['dwg2dxf', '--version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            return True
    except:
        pass
    
    return False


def convert_dwg_with_oda(dwg_path: str, output_dir: str) -> str:
    """
    Convert DWG using ODA File Converter (if available)
    
    Args:
        dwg_path: Path to DWG file
        output_dir: Output directory
        
    Returns:
        Path to DXF file
    """
    # Find ODA File Converter
    oda_paths = [
        '/usr/bin/ODAFileConverter',
        '/opt/ODAFileConverter/ODAFileConverter',
    ]
    
    oda_path = None
    for path in oda_paths:
        if os.path.exists(path):
            oda_path = path
            break
    
    if not oda_path:
        raise FileNotFoundError("ODA File Converter not found")
    
    # Create temp directory for conversion
    temp_dir = Path(output_dir) / "temp_oda"
    temp_dir.mkdir(exist_ok=True, parents=True)
    
    # Run conversion
    # ODA syntax: ODAFileConverter input_folder output_folder output_version output_format
    result = subprocess.run([
        oda_path,
        str(Path(dwg_path).parent),
        str(temp_dir),
        'ACAD2018',
        'DXF',
        '0',  # Recurse subdirectories: 0=no
        '1',  # Audit: 1=yes
        ''    # Input filter (empty = all)
    ], capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        raise RuntimeError(f"ODA conversion failed: {result.stderr}")
    
    # Find the converted DXF
    dwg_name = Path(dwg_path).stem
    dxf_path = temp_dir / f"{dwg_name}.dxf"
    
    if not dxf_path.exists():
        raise FileNotFoundError(f"Converted DXF not found: {dxf_path}")
    
    # Move to output directory
    final_path = Path(output_dir) / f"{dwg_name}.dxf"
    dxf_path.rename(final_path)
    
    # Cleanup temp directory
    try:
        temp_dir.rmdir()
    except:
        pass
    
    return str(final_path)
