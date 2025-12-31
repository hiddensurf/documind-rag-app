"""
Advanced CAD Visual Analysis Module
Uses Gemini 2.5 Flash for superior vision capabilities
"""

import os
import base64
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from google import genai
from google.genai import types
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from io import BytesIO

class AdvancedCADVisualAnalyzer:
    def __init__(self, api_key: str):
        """Initialize with Gemini 2.5 Flash (best available)"""
        self.client = genai.Client(api_key=api_key)
        # Use Gemini 2.5 Flash - superior model with good quota
        self.model_id = 'gemini-2.5-flash'
        
        # Multi-pass analysis configuration
        self.analysis_passes = {
            'overview': self._get_overview_prompt(),
            'technical': self._get_technical_prompt(),
            'components': self._get_components_prompt(),
            'measurements': self._get_measurements_prompt(),
            'quality': self._get_quality_prompt()
        }
        
    def _get_overview_prompt(self) -> str:
        return """Analyze this CAD drawing and provide a comprehensive overview:

1. **Drawing Type & Purpose**: What type of drawing is this (architectural, mechanical, electrical, civil, etc.)? What is its primary purpose?

2. **Overall Layout**: Describe the overall composition, organization, and structure of the drawing.

3. **Key Elements**: Identify and list the 5-10 most important elements, components, or features visible.

4. **Complexity Assessment**: Rate the complexity (Simple/Moderate/Complex/Very Complex) and explain why.

5. **Industry Context**: What industry or field would use this drawing?

Be detailed and specific. Use technical terminology where appropriate."""

    def _get_technical_prompt(self) -> str:
        return """Provide a detailed technical analysis of this CAD drawing:

1. **Dimensions & Scale**: 
   - Identify all visible dimensions and their units
   - Determine the scale or scale indicator
   - Note any dimension styles used

2. **Line Types & Weights**:
   - Describe the different line types visible (solid, dashed, center, hidden)
   - Note line weight variations and their purposes

3. **Annotation & Labels**:
   - List all text annotations, labels, and callouts
   - Identify title blocks, revision blocks, or notes sections
   - Extract any part numbers, reference designators, or identifiers

4. **Symbols & Standards**:
   - Identify any standard symbols (welding, surface finish, GD&T, electrical, etc.)
   - Note which drawing standards appear to be followed (ISO, ANSI, DIN, etc.)

5. **Views & Projections**:
   - Identify the projection method (orthographic, isometric, perspective)
   - List all views shown (plan, elevation, section, detail)
   - Note any cutting planes or section indicators

Be extremely thorough and technical."""

    def _get_components_prompt(self) -> str:
        return """Analyze the components and features in this CAD drawing:

1. **Component Inventory**:
   - List every distinct component, part, or feature
   - Provide descriptions of each component's appearance and function
   - Identify any assembly relationships or connections

2. **Geometric Features**:
   - Identify shapes: circles, rectangles, polygons, curves, arcs
   - Note any holes, slots, chamfers, fillets, or other features
   - Describe patterns or arrays of features

3. **Material Indications**:
   - Identify any material callouts or hatch patterns
   - Note surface finish indicators
   - List any material specifications visible

4. **Hierarchical Structure**:
   - Identify main assemblies and sub-assemblies
   - Note component groupings or systems
   - Describe spatial relationships between components

5. **Special Features**:
   - Identify any unique or notable features
   - Note any modifications, repairs, or variations indicated
   - Point out any incomplete or ambiguous areas

Provide a complete inventory with technical details."""

    def _get_measurements_prompt(self) -> str:
        return """Extract and analyze all measurements and specifications:

1. **Dimensional Data**:
   - Extract ALL numerical dimensions with their units
   - List dimensions systematically (lengths, widths, heights, diameters, radii, angles)
   - Note tolerance specifications (±, limit dimensions, geometric tolerances)

2. **Critical Dimensions**:
   - Identify which dimensions appear to be most critical
   - Note any reference dimensions or calculated values
   - Highlight dimensions with tight tolerances

3. **Coordinate Systems**:
   - Identify coordinate systems or datum references
   - Note any grid systems or reference lines
   - Describe origin points or reference features

4. **Quantifiable Features**:
   - Count: number of holes, fasteners, components, etc.
   - Areas: calculate or estimate surface areas if possible
   - Volumes: estimate enclosed volumes if applicable

5. **Specification Notes**:
   - Extract any numerical specifications (weights, capacities, ratings)
   - List performance specifications if visible
   - Note any inspection or quality control requirements

Create a comprehensive dimensional database from this drawing."""

    def _get_quality_prompt(self) -> str:
        return """Assess the quality and completeness of this CAD drawing:

1. **Drawing Clarity**:
   - Rate line clarity and visibility (1-10)
   - Assess text readability
   - Note any smudging, fading, or quality issues

2. **Completeness Check**:
   - Are all necessary views included?
   - Is the title block complete?
   - Are all dimensions provided?
   - Are there any missing details or ambiguities?

3. **Standards Compliance**:
   - Does it follow recognizable drafting standards?
   - Are symbols used correctly?
   - Is dimensioning practice correct?

4. **Potential Issues**:
   - Identify any errors, inconsistencies, or conflicts
   - Note any unclear or ambiguous areas
   - Highlight missing information

5. **Recommendations**:
   - Suggest improvements to clarity or completeness
   - Recommend additional views or details if needed
   - Note any information that should be verified

Provide a professional quality assessment."""

    def preprocess_image(self, image_path: str) -> List[Tuple[bytes, str]]:
        """
        Create multiple preprocessed versions of the image for better analysis
        Returns list of (image_bytes, description) tuples
        """
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        versions = []
        
        # 1. Original high-resolution
        original_buffer = BytesIO()
        # Resize if too large (max 4096px on longest side for Gemini)
        max_size = 4096
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
            img_resized.save(original_buffer, format='PNG', quality=95)
        else:
            img.save(original_buffer, format='PNG', quality=95)
        
        versions.append((
            original_buffer.getvalue(),
            "original_high_resolution"
        ))
        
        # 2. Enhanced contrast version (better for faint lines)
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(2.0)
        enhanced_buffer = BytesIO()
        if max(enhanced.size) > max_size:
            ratio = max_size / max(enhanced.size)
            new_size = tuple(int(dim * ratio) for dim in enhanced.size)
            enhanced = enhanced.resize(new_size, Image.Resampling.LANCZOS)
        enhanced.save(enhanced_buffer, format='PNG', quality=95)
        
        versions.append((
            enhanced_buffer.getvalue(),
            "enhanced_contrast"
        ))
        
        # 3. Sharpened version (better for text and fine details)
        sharpened = img.filter(ImageFilter.SHARPEN)
        sharp_buffer = BytesIO()
        if max(sharpened.size) > max_size:
            ratio = max_size / max(sharpened.size)
            new_size = tuple(int(dim * ratio) for dim in sharpened.size)
            sharpened = sharpened.resize(new_size, Image.Resampling.LANCZOS)
        sharpened.save(sharp_buffer, format='PNG', quality=95)
        
        versions.append((
            sharp_buffer.getvalue(),
            "sharpened"
        ))
        
        return versions

    def analyze_single_pass(self, image_bytes: bytes, prompt: str, pass_name: str, retry_count: int = 3) -> Dict:
        """Perform a single analysis pass with retry logic and rate limit handling"""
        
        for attempt in range(retry_count):
            try:
                # Create Parts
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/png'
                )
                
                text_part = types.Part.from_text(text=prompt)
                
                # Generate content with both parts
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[image_part, text_part],
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=8192,
                    )
                )
                
                return {
                    'pass_name': pass_name,
                    'success': True,
                    'analysis': response.text,
                    'error': None
                }
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if rate limit error
                if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    if attempt < retry_count - 1:
                        # Extract retry delay if available
                        wait_time = 10  # shorter default for 2.5-flash
                        if 'retry in' in error_msg.lower():
                            try:
                                # Try to parse delay
                                import re
                                match = re.search(r'retry in (\d+(?:\.\d+)?)', error_msg.lower())
                                if match:
                                    wait_time = min(float(match.group(1)), 60)  # cap at 60s
                            except:
                                pass
                        
                        print(f"   ⏸️  Rate limit hit, waiting {wait_time:.0f}s before retry...")
                        time.sleep(wait_time)
                        continue
                
                return {
                    'pass_name': pass_name,
                    'success': False,
                    'analysis': None,
                    'error': error_msg
                }
        
        return {
            'pass_name': pass_name,
            'success': False,
            'analysis': None,
            'error': f'Failed after {retry_count} attempts'
        }

    def comprehensive_analysis(self, png_path: str) -> Dict:
        """
        Perform comprehensive multi-pass analysis
        Returns structured analysis results
        """
        print(f"\n🔍 Starting comprehensive CAD analysis...")
        print(f"📊 Model: {self.model_id}")
        
        # Preprocess image into multiple versions
        print("📸 Preprocessing image (creating enhanced versions)...")
        image_versions = self.preprocess_image(png_path)
        
        # Use the original high-res version for analysis
        primary_image = image_versions[0][0]
        
        results = {
            'image_path': png_path,
            'model_used': self.model_id,
            'preprocessing': {
                'versions_created': len(image_versions),
                'version_types': [v[1] for v in image_versions]
            },
            'analyses': {},
            'summary': {},
            'errors': []
        }
        
        # Perform each analysis pass
        total_passes = len(self.analysis_passes)
        for idx, (pass_name, prompt) in enumerate(self.analysis_passes.items(), 1):
            print(f"🎯 Pass {idx}/{total_passes}: {pass_name.upper()} analysis...")
            
            result = self.analyze_single_pass(primary_image, prompt, pass_name)
            
            if result['success']:
                results['analyses'][pass_name] = result['analysis']
                print(f"   ✅ {pass_name} complete ({len(result['analysis'])} chars)")
            else:
                results['errors'].append({
                    'pass': pass_name,
                    'error': result['error']
                })
                print(f"   ❌ {pass_name} failed: {result['error'][:100]}...")
            
            # Small delay between passes to avoid rate limiting
            if idx < total_passes:
                time.sleep(1)
        
        # Generate final synthesis
        if len(results['analyses']) > 0:
            print("🔄 Generating synthesis...")
            results['summary'] = self._generate_synthesis(results['analyses'])
        
        print(f"✨ Analysis complete! Generated {len(results['analyses'])} detailed analyses.\n")
        
        return results

    def _generate_synthesis(self, analyses: Dict[str, str]) -> Dict:
        """Generate a synthesis of all analysis passes"""
        
        # Combine all analyses
        combined_text = "\n\n".join([
            f"=== {name.upper()} ===\n{content}"
            for name, content in analyses.items()
        ])
        
        synthesis_prompt = f"""Based on these multiple detailed analyses of the same CAD drawing, create a comprehensive executive summary:

{combined_text}

Provide:
1. **Drawing Identity**: Type, purpose, and primary application
2. **Key Specifications**: Most critical dimensions and specifications
3. **Notable Features**: Top 5-7 most important elements
4. **Technical Assessment**: Overall quality and completeness rating
5. **Critical Information**: Must-know details for anyone using this drawing

Be concise but complete. This should be the "executive briefing" on this drawing."""

        try:
            text_part = types.Part.from_text(text=synthesis_prompt)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[text_part],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )
            
            return {
                'executive_summary': response.text,
                'total_analysis_length': len(combined_text),
                'synthesis_success': True
            }
        except Exception as e:
            return {
                'executive_summary': 'Synthesis generation failed',
                'error': str(e),
                'synthesis_success': False
            }

    def format_for_rag(self, analysis_results: Dict) -> str:
        """
        Format analysis results for RAG indexing
        Creates a comprehensive text document from all analyses
        """
        
        formatted = []
        
        # Header
        formatted.append("=" * 80)
        formatted.append("COMPREHENSIVE CAD DRAWING ANALYSIS")
        formatted.append("=" * 80)
        formatted.append("")
        
        # Executive Summary (if available)
        if 'summary' in analysis_results and analysis_results['summary'].get('executive_summary'):
            formatted.append("EXECUTIVE SUMMARY")
            formatted.append("-" * 80)
            formatted.append(analysis_results['summary']['executive_summary'])
            formatted.append("")
        
        # Detailed Analyses
        formatted.append("DETAILED ANALYSES")
        formatted.append("=" * 80)
        formatted.append("")
        
        for pass_name, content in analysis_results.get('analyses', {}).items():
            formatted.append(f"\n{pass_name.upper()} ANALYSIS")
            formatted.append("-" * 80)
            formatted.append(content)
            formatted.append("")
        
        # Metadata
        formatted.append("\nANALYSIS METADATA")
        formatted.append("-" * 80)
        formatted.append(f"Image: {analysis_results.get('image_path', 'Unknown')}")
        formatted.append(f"Model: {analysis_results.get('model_used', 'Unknown')}")
        formatted.append(f"Analyses Completed: {len(analysis_results.get('analyses', {}))}")
        
        if analysis_results.get('errors'):
            formatted.append(f"Errors Encountered: {len(analysis_results['errors'])}")
        
        return "\n".join(formatted)


def analyze_cad_drawing(png_path: str, api_key: str) -> Dict:
    """
    Main entry point for advanced CAD analysis
    
    Args:
        png_path: Path to PNG render of CAD drawing
        api_key: Google AI API key
        
    Returns:
        Complete analysis results dictionary
    """
    analyzer = AdvancedCADVisualAnalyzer(api_key)
    return analyzer.comprehensive_analysis(png_path)


if __name__ == "__main__":
    # Test code
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_visual_analyzer.py <path_to_png>")
        sys.exit(1)
    
    png_path = sys.argv[1]
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)
    
    results = analyze_cad_drawing(png_path, api_key)
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS SUMMARY")
    print("=" * 80)
    print(f"Successful analyses: {len(results['analyses'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['summary'].get('executive_summary'):
        print("\nEXECUTIVE SUMMARY:")
        print(results['summary']['executive_summary'])
