"""
Multi-Model CAD Analyzer
Supports Gemini (direct + OpenRouter) + other OpenRouter models
Updated with gemini-2.5-flash and gemini-2.5-flash-lite fallback
"""

import os
import io
import base64
import httpx
import logging
from typing import Dict, Optional
from pathlib import Path
from PIL import Image
import google.generativeai as genai

logger = logging.getLogger(__name__)

class MultiModelCADAnalyzer:
    """Advanced CAD analyzer with multiple Gemini fallbacks"""
    
    MODELS = {
        # === GOOGLE STUDIO GEMINI (PRIMARY) ===
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "provider": "GEMINI_DIRECT",
            "fallback_provider": "GEMINI_DIRECT",
            "fallback_model": "gemini-2.5-flash-lite",
            "capabilities": ["vision", "fast"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "Google AI Studio (recommended)",
            "api_model": "gemini-2.5-flash"
        },
        
        # === GOOGLE STUDIO GEMINI LITE (FALLBACK) ===
        "gemini-2.5-flash-lite": {
            "name": "Gemini 2.5 Flash Lite",
            "provider": "GEMINI_DIRECT",
            "capabilities": ["vision", "fast", "lite"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "Lighter version, better for quota limits",
            "api_model": "gemini-2.5-flash-lite"
        },
        
        # === OPENROUTER GEMINI (SECONDARY FALLBACK) ===
        "google/gemini-2.0-flash-exp:free": {
            "name": "Gemini 2.0 Flash (OpenRouter)",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "fast"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "OpenRouter fallback (rate limited)"
        },
        
        # === VISION MODELS (FREE) ===
        "nvidia/nemotron-nano-12b-v2-vl:free": {
            "name": "NVIDIA Nemotron Nano VL",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "technical"],
            "context_window": "32K tokens",
            "free": True,
            "notes": "Optimized for technical diagrams"
        },
        
        "qwen/qwen-2.5-vl-7b-instruct:free": {
            "name": "Qwen 2.5 VL 7B",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "fast"],
            "context_window": "32K tokens",
            "free": True,
            "notes": "Qwen vision model"
        },
        
        # === TEXT-ONLY MODELS (FREE) ===
        "meta-llama/llama-3.3-70b-instruct:free": {
            "name": "Llama 3.3 70B Instruct",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "large_context"],
            "context_window": "128K tokens",
            "free": True,
            "notes": "Best free text model"
        },
        
        "google/gemma-3-27b-it:free": {
            "name": "Gemma 3 27B IT",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "fast"],
            "context_window": "8K tokens",
            "free": True,
            "notes": "Fast Google model"
        },
        
        "openai/gpt-oss-20b:free": {
            "name": "GPT OSS 20B",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning"],
            "context_window": "16K tokens",
            "free": True,
            "notes": "Open source GPT-style"
        },
        
        # === TEXT-ONLY MODELS (PAID) ===
        "deepseek/deepseek-r1": {
            "name": "DeepSeek R1",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "advanced"],
            "context_window": "64K tokens",
            "free": False,
            "notes": "Excellent reasoning (paid)"
        },
        
        "qwen/qwen3-235b-a22b": {
            "name": "Qwen 3 235B",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "advanced"],
            "context_window": "32K tokens",
            "free": False,
            "notes": "Large reasoning model (paid)"
        }
    }
    
    def __init__(self, gemini_api_key: str = None, openrouter_api_key: str = None):
        """Initialize with both API keys"""
        self.gemini_api_key = gemini_api_key or os.getenv('GOOGLE_API_KEY')
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        
        # Setup Google Studio Gemini models
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_models = {
                    'gemini-2.5-flash': genai.GenerativeModel('gemini-2.5-flash'),
                    'gemini-2.5-flash-lite': genai.GenerativeModel('gemini-2.5-flash-lite')
                }
                logger.info("✅ Google Studio Gemini models initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Studio init failed: {e}")
                self.gemini_models = {}
        else:
            logger.warning("⚠️ No GOOGLE_API_KEY")
            self.gemini_models = {}
        
        if not self.openrouter_api_key:
            logger.warning("⚠️ No OPENROUTER_API_KEY - OpenRouter fallback unavailable")
    
    async def analyze_with_gemini_direct(self, image_bytes: Optional[bytes], prompt: str, model_name: str = 'gemini-2.5-flash') -> str:
        """Google Studio Gemini (PRIMARY)"""
        if model_name not in self.gemini_models:
            raise Exception(f"Gemini model {model_name} not initialized")
        
        try:
            model = self.gemini_models[model_name]
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                raise QuotaExceededError(f"Gemini quota exceeded: {error_msg}")
            raise Exception(f"Gemini API error: {error_msg}")
    
    async def analyze_with_openrouter(self, image_bytes: Optional[bytes], prompt: str, model_id: str) -> str:
        """OpenRouter (FALLBACK + other models)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://documind.app",
                "X-Title": "DocuMind CAD Analyzer"
            }
            
            if image_bytes:
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                message_content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            else:
                message_content = prompt
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": message_content}]
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"OpenRouter error ({e.response.status_code}): {e.response.text[:200]}")
        except Exception as e:
            raise Exception(f"OpenRouter failed: {e}")
    
    async def analyze_with_auto_fallback(self, image_bytes: Optional[bytes], prompt: str, model_id: str = "gemini-2.5-flash") -> tuple[str, str]:
        """Smart analysis with cascading fallback: Flash → Flash Lite → OpenRouter"""
        model_info = self.MODELS.get(model_id)
        if not model_info:
            raise ValueError(f"Unknown model: {model_id}")
        
        # GEMINI_DIRECT with cascading fallback
        if model_info['provider'] == 'GEMINI_DIRECT':
            # Try primary model first
            api_model = model_info.get('api_model', 'gemini-2.5-flash')
            try:
                logger.info(f"🔵 Trying Google Studio {api_model}...")
                response = await self.analyze_with_gemini_direct(image_bytes, prompt, api_model)
                logger.info(f"✅ Google Studio {api_model} succeeded")
                return response, f"Google Studio {api_model}"
            except QuotaExceededError as e:
                logger.warning(f"⚠️ {api_model} quota exceeded")
                
                # Try Gemini fallback (Flash Lite)
                fallback_model = model_info.get('fallback_model')
                if fallback_model and fallback_model in self.gemini_models:
                    try:
                        logger.info(f"🔄 Trying fallback: {fallback_model}...")
                        response = await self.analyze_with_gemini_direct(image_bytes, prompt, fallback_model)
                        logger.info(f"✅ Fallback {fallback_model} succeeded")
                        return response, f"Google Studio {fallback_model} (fallback)"
                    except QuotaExceededError:
                        logger.warning(f"⚠️ {fallback_model} also quota exceeded")
                    except Exception as e2:
                        logger.error(f"❌ Fallback error: {e2}")
                
                # Last resort: Try OpenRouter if available
                if self.openrouter_api_key:
                    or_fallback = "google/gemini-2.0-flash-exp:free"
                    try:
                        logger.info("🔄 Last resort: OpenRouter Gemini...")
                        response = await self.analyze_with_openrouter(image_bytes, prompt, or_fallback)
                        return response, "OpenRouter Gemini (fallback)"
                    except Exception as e3:
                        logger.error(f"❌ OpenRouter fallback failed: {e3}")
                
                # All fallbacks exhausted
                raise Exception("All Gemini sources exhausted (quota exceeded)")
                
            except Exception as e:
                logger.error(f"❌ Google Studio error: {e}")
                raise
        
        # For other models, use OpenRouter directly
        else:
            response = await self.analyze_with_openrouter(image_bytes, prompt, model_id)
            return response, model_info['name']
    
    async def comprehensive_analysis(self, png_path: str, model_id: str = "gemini-2.5-flash") -> Dict:
        """Run comprehensive 5-stage CAD analysis with cascading fallback"""
        if not Path(png_path).exists():
            raise FileNotFoundError(f"PNG not found: {png_path}")
        
        model_info = self.MODELS.get(model_id)
        if not model_info or 'vision' not in model_info['capabilities']:
            raise ValueError(f"Model {model_id} doesn't support vision")
        
        logger.info(f"🔍 5-stage analysis with {model_info['name']}...")
        
        with open(png_path, 'rb') as f:
            image_bytes = f.read()
        
        provider_used = None
        stages = {
            "stage_1_overview": "Analyze this CAD: 1) type 2) purpose 3) complexity 4) key features",
            "stage_2_technical": "Technical aspects: 1) dimensions 2) standards 3) annotations 4) units",
            "stage_3_components": "Components: 1) major parts 2) relationships 3) materials 4) features",
            "stage_4_measurements": "Measurements: 1) critical dims 2) tolerances 3) angles 4) constraints",
            "stage_5_quality": "Quality: 1) clarity 2) completeness 3) issues 4) recommendations"
        }
        
        results = {}
        for i, (stage_name, prompt) in enumerate(stages.items(), 1):
            logger.info(f"  Stage {i}/5: {stage_name.replace('_', ' ').title()}...")
            response, used_provider = await self.analyze_with_auto_fallback(image_bytes, prompt, model_id)
            results[stage_name] = response
            if not provider_used:
                provider_used = used_provider
        
        logger.info("  Executive summary...")
        summary_prompt = f"""Summarize in 2-3 sentences:
Overview: {results['stage_1_overview'][:200]}
Technical: {results['stage_2_technical'][:200]}"""
        
        summary, _ = await self.analyze_with_auto_fallback(None, summary_prompt, model_id)
        
        return {
            "model_used": model_info['name'],
            "model_id": model_id,
            "provider_used": provider_used,
            "executive_summary": summary,
            **results
        }
    
    def format_for_rag(self, analysis_results: Dict) -> str:
        """Format for RAG indexing"""
        provider_note = f" via {analysis_results.get('provider_used', 'unknown')}"
        
        return f"""CAD ANALYSIS ({analysis_results['model_used']}{provider_note})

SUMMARY: {analysis_results['executive_summary']}

OVERVIEW: {analysis_results['stage_1_overview']}

TECHNICAL: {analysis_results['stage_2_technical']}

COMPONENTS: {analysis_results['stage_3_components']}

MEASUREMENTS: {analysis_results['stage_4_measurements']}

QUALITY: {analysis_results['stage_5_quality']}"""

class QuotaExceededError(Exception):
    """Raised when API quota is exceeded"""
    pass
