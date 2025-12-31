"""
Hybrid CAD Analyzer
Combines CV feature extraction with LLM analysis
Allows text-only models to analyze CAD drawings
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from app.cad.cv_extractor import CADFeatureExtractor
from app.cad.multi_model_analyzer import MultiModelCADAnalyzer

logger = logging.getLogger(__name__)

class HybridCADAnalyzer:
    """
    Hybrid analyzer combining:
    1. CV feature extraction (local, free, instant)
    2. LLM analysis (using extracted features)
    """
    
    def __init__(self, gemini_api_key: str = None, openrouter_api_key: str = None):
        self.cv_extractor = CADFeatureExtractor()
        self.llm_analyzer = MultiModelCADAnalyzer(gemini_api_key, openrouter_api_key)
    
    async def analyze_with_cv_assistance(
        self,
        png_path: str,
        model_id: str,
        include_vision: bool = False
    ) -> Dict:
        """
        Analyze CAD using CV extraction + LLM
        
        Args:
            png_path: Path to CAD image
            model_id: LLM model to use
            include_vision: If True and model supports vision, send image too
        
        Returns:
            Analysis results with CV features + LLM insights
        """
        if not Path(png_path).exists():
            raise FileNotFoundError(f"PNG not found: {png_path}")
        
        model_info = self.llm_analyzer.MODELS.get(model_id)
        if not model_info:
            raise ValueError(f"Unknown model: {model_id}")
        
        logger.info(f"🔬 Hybrid analysis: CV + {model_info['name']}")
        
        # Step 1: Extract CV features (local, instant)
        logger.info("  Step 1/3: CV feature extraction...")
        cv_features = self.cv_extractor.extract_features(png_path)
        cv_prompt = self.cv_extractor.format_for_llm(cv_features)
        
        # Step 2: Decide if we can use vision
        use_vision = include_vision and 'vision' in model_info['capabilities']
        
        if use_vision:
            logger.info("  Step 2/3: Vision-enabled analysis (CV + image)...")
            # Read image for vision model
            with open(png_path, 'rb') as f:
                image_bytes = f.read()
            
            # Enhanced prompt with CV hints
            vision_prompt = f"""{cv_prompt}

Based on the computer vision analysis above AND the actual image, provide:
1. What type of CAD drawing is this?
2. What is the primary purpose?
3. Identify key components and their relationships
4. Any insights not captured by CV analysis?"""
            
            response, provider = await self.llm_analyzer.analyze_with_auto_fallback(
                image_bytes,
                vision_prompt,
                model_id
            )
        else:
            logger.info("  Step 2/3: Text-only analysis (CV features only)...")
            # Text-only: just use CV features
            text_prompt = f"""{cv_prompt}

Based on the computer vision analysis above, provide:
1. What type of CAD drawing is this likely to be?
2. What insights can you derive from the detected shapes and lines?
3. What is the likely purpose and application?
4. Any recommendations based on the complexity and structure?"""
            
            response, provider = await self.llm_analyzer.analyze_with_auto_fallback(
                None,  # No image
                text_prompt,
                model_id
            )
        
        logger.info("  Step 3/3: Complete!")
        
        return {
            "model_used": model_info['name'],
            "model_id": model_id,
            "provider_used": provider,
            "method": "vision+cv" if use_vision else "cv_only",
            "cv_features": cv_features,
            "llm_analysis": response,
            "combined_analysis": self._format_combined(cv_features, response, model_info['name'])
        }
    
    async def comprehensive_hybrid_analysis(
        self,
        png_path: str,
        vision_model_id: str = "nvidia/nemotron-nano-12b-v2-vl:free",
        text_model_ids: list = None
    ) -> Dict:
        """
        Run comprehensive analysis using:
        1. One vision model (with CV hints)
        2. Multiple text-only models (CV features only)
        
        This gives multiple perspectives on the same CAD drawing
        """
        if not Path(png_path).exists():
            raise FileNotFoundError(f"PNG not found: {png_path}")
        
        if text_model_ids is None:
            # Default: use free text models
            text_model_ids = [
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemma-3-27b-it:free",
                "deepseek/deepseek-r1"
            ]
        
        logger.info(f"🔬 Comprehensive hybrid analysis")
        logger.info(f"   Vision model: {vision_model_id}")
        logger.info(f"   Text models: {len(text_model_ids)}")
        
        # Extract CV features once
        logger.info("  Extracting CV features...")
        cv_features = self.cv_extractor.extract_features(png_path)
        
        results = {
            "cv_features": cv_features,
            "vision_analysis": None,
            "text_analyses": []
        }
        
        # Vision analysis (if model available)
        try:
            logger.info(f"  Running vision analysis...")
            vision_result = await self.analyze_with_cv_assistance(
                png_path,
                vision_model_id,
                include_vision=True
            )
            results["vision_analysis"] = vision_result
        except Exception as e:
            logger.error(f"  Vision analysis failed: {e}")
            results["vision_analysis"] = {"error": str(e)}
        
        # Text-only analyses
        for i, model_id in enumerate(text_model_ids, 1):
            try:
                logger.info(f"  Running text analysis {i}/{len(text_model_ids)}: {model_id}")
                text_result = await self.analyze_with_cv_assistance(
                    png_path,
                    model_id,
                    include_vision=False
                )
                results["text_analyses"].append(text_result)
            except Exception as e:
                logger.error(f"  Text analysis {i} failed: {e}")
                results["text_analyses"].append({
                    "model_id": model_id,
                    "error": str(e)
                })
        
        # Synthesize all perspectives
        results["synthesis"] = self._synthesize_analyses(results)
        
        return results
    
    def _format_combined(self, cv_features: Dict, llm_response: str, model_name: str) -> str:
        """Format combined CV + LLM analysis"""
        summary = cv_features.get('summary', {})
        
        return f"""HYBRID CAD ANALYSIS
Model: {model_name}

=== COMPUTER VISION DETECTION ===
Shapes: {summary.get('total_shapes', 0)} total
Lines: {summary.get('total_lines', 0)} total
Complexity: {summary.get('complexity', 'unknown').upper()}

=== AI ANALYSIS ===
{llm_response}
"""
    
    def _synthesize_analyses(self, results: Dict) -> str:
        """Synthesize insights from multiple models"""
        parts = ["MULTI-MODEL SYNTHESIS\n"]
        
        # CV summary
        cv = results.get('cv_features', {}).get('summary', {})
        parts.append(f"CV Detection: {cv.get('total_shapes', 0)} shapes, {cv.get('total_lines', 0)} lines")
        
        # Vision model insight
        if results.get('vision_analysis') and 'llm_analysis' in results['vision_analysis']:
            parts.append(f"\nVision Model: {results['vision_analysis']['llm_analysis'][:200]}...")
        
        # Text models consensus
        text_count = len([r for r in results.get('text_analyses', []) if 'llm_analysis' in r])
        if text_count > 0:
            parts.append(f"\nText Models: {text_count} models analyzed successfully")
        
        return "\n".join(parts)
