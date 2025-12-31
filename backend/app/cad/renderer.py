"""
CAD Renderer - Convert DXF to SVG for browser display
"""
import logging
from pathlib import Path
from typing import Optional
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class CADRenderer:
    """Render DXF files to SVG"""
    
    def __init__(self, render_dir: str = "cad_renders"):
        self.render_dir = Path(render_dir)
        self.render_dir.mkdir(exist_ok=True)
        
    def render_to_svg(self, dxf_path: str, output_id: str) -> Optional[str]:
        """
        Render DXF file to SVG
        
        Args:
            dxf_path: Path to DXF file
            output_id: ID for output filename
            
        Returns:
            Path to rendered SVG file, or None if failed
        """
        try:
            logger.info(f"Rendering DXF to SVG: {dxf_path}")
            
            # Read DXF
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            # Setup matplotlib backend
            fig = plt.figure(figsize=(12, 9), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ctx = RenderContext(doc)
            out = MatplotlibBackend(ax)
            
            # Render
            Frontend(ctx, out).draw_layout(msp, finalize=True)
            
            # Save as SVG
            output_path = self.render_dir / f"{output_id}.svg"
            fig.savefig(output_path, format='svg', bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            
            logger.info(f"SVG rendered successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error rendering DXF to SVG: {str(e)}")
            return None
    
    def render_to_png(self, dxf_path: str, output_id: str, width: int = 1200) -> Optional[str]:
        """
        Render DXF file to PNG (fallback if SVG fails)
        
        Args:
            dxf_path: Path to DXF file
            output_id: ID for output filename
            width: Image width in pixels
            
        Returns:
            Path to rendered PNG file, or None if failed
        """
        try:
            logger.info(f"Rendering DXF to PNG: {dxf_path}")
            
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            # Calculate aspect ratio
            height = int(width * 0.75)  # 4:3 aspect ratio
            
            fig = plt.figure(figsize=(width/100, height/100), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ctx = RenderContext(doc)
            out = MatplotlibBackend(ax)
            
            Frontend(ctx, out).draw_layout(msp, finalize=True)
            
            output_path = self.render_dir / f"{output_id}.png"
            fig.savefig(output_path, format='png', bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            
            logger.info(f"PNG rendered successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error rendering DXF to PNG: {str(e)}")
            return None
