#!/usr/bin/env python3
import sys

# Read current routes.py
with open('app/api/routes.py', 'r') as f:
    content = f.read()

# Find and extract everything before the advanced-analysis endpoint
start_marker = '@router.post("/conversations/{conv_id}/advanced-analysis")'
start_pos = content.find(start_marker)

if start_pos == -1:
    print("ERROR: Could not find advanced-analysis endpoint!")
    sys.exit(1)

# Find the next @router after this endpoint
next_router_pos = content.find('\n@router.', start_pos + 100)
if next_router_pos == -1:
    next_router_pos = len(content)

# Extract parts
before_endpoint = content[:start_pos]
after_endpoint = content[next_router_pos:]

# New endpoint code
new_endpoint = '''@router.post("/conversations/{conv_id}/advanced-analysis")
async def run_advanced_analysis(conv_id: str, request: ChatRequest):
    """
    Run advanced 5-stage vision analysis on CAD documents
    Supports multiple AI models (Gemini and OpenRouter)
    """
    try:
        logger.info(f"🤖 Advanced analysis request for conversation: {conv_id}")
        
        conversation = conversation_service.get_conversation(conv_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        doc_ids = request.document_ids or conversation.document_ids
        if not doc_ids:
            raise HTTPException(status_code=400, detail="No documents selected")
        
        # Extract model selection (default: gemini-2.5-flash)
        selected_model = getattr(request, 'model', 'gemini-2.5-flash')
        
        # Check for CAD documents
        from app.services.document_service import document_service
        cad_docs = []
        for doc_id in doc_ids:
            doc = document_service.get_document(doc_id)
            if doc and doc.get('is_cad', False):
                cad_docs.append(doc)
        
        if not cad_docs:
            raise HTTPException(status_code=400, detail="No CAD documents selected for advanced analysis")
        
        # Import multi-model analyzer
        from app.cad.multi_model_analyzer import MultiModelCADAnalyzer
        from app.core.config import get_settings
        from pathlib import Path
        import json
        
        settings = get_settings()
        analyzer = MultiModelCADAnalyzer(
            gemini_api_key=settings.GOOGLE_API_KEY,
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY')
        )
        
        # Validate model
        if selected_model not in analyzer.MODELS:
            logger.warning(f"Unknown model {selected_model}, using default")
            selected_model = 'gemini-2.5-flash'
        
        all_analyses = []
        
        for doc in cad_docs:
            doc_id = doc['id']
            doc_name = doc['name']
            
            logger.info(f"Running advanced analysis for: {doc_name} with {selected_model}")
            
            # Find PNG
            png_path = Path(f"cad_renders/{doc_id}_analysis.png")
            
            if not png_path.exists():
                logger.warning(f"PNG not found for {doc_id}, skipping")
                all_analyses.append(f"⚠️ **{doc_name}**: Analysis PNG not available. Please re-upload this file.")
                continue
            
            try:
                # Run comprehensive analysis
                analysis_results = await analyzer.comprehensive_analysis(str(png_path), selected_model)
                
                # Save analysis
                analysis_path = Path(f"cad_manifests/{doc_id}_analysis.json")
                with open(analysis_path, 'w') as f:
                    json.dump(analysis_results, f, indent=2)
                
                # Format response
                model_info = analyzer.MODELS[selected_model]
                formatted = f"""
# 🔍 ADVANCED CAD ANALYSIS: {doc_name}

**Model**: {model_info['name']} ({model_info['provider'].upper()})
**Capabilities**: {', '.join(model_info['capabilities'])}

{analyzer.format_for_rag(analysis_results)}
"""
                all_analyses.append(formatted)
                
            except Exception as e:
                logger.error(f"Error analyzing {doc_name}: {e}", exc_info=True)
                all_analyses.append(f"❌ **{doc_name}**: Analysis failed - {str(e)}")
        
        if not all_analyses:
            combined_response = "⚠️ No analyses could be completed. Please ensure CAD files have been properly uploaded."
        else:
            combined_response = "\\n\\n---\\n\\n".join(all_analyses)
        
        # Save to conversation
        model_name = analyzer.MODELS[selected_model]['name']
        user_message = Message(
            role="user",
            content=f"🤖 Advanced Analysis with {model_name}",
            timestamp=datetime.now().isoformat()
        )
        conversation_service.add_message(conv_id, user_message)
        
        assistant_message = Message(
            role="assistant",
            content=combined_response,
            timestamp=datetime.now().isoformat(),
            has_mindmap=False,
            mermaid_code=None,
            sources=[]
        )
        conversation_service.add_message(conv_id, assistant_message, auto_title=False)
        
        return ChatResponse(
            response=combined_response,
            has_mindmap=False,
            mermaid_code=None,
            sources=[],
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Get list of available AI models for CAD analysis"""
    try:
        from app.cad.multi_model_analyzer import MultiModelCADAnalyzer
        
        analyzer = MultiModelCADAnalyzer(
            gemini_api_key=os.getenv('GOOGLE_API_KEY'),
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY')
        )
        
        return {
            "models": [
                {
                    "id": model_id,
                    **model_info
                }
                for model_id, model_info in analyzer.MODELS.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {"models": []}

'''

# Combine
new_content = before_endpoint + new_endpoint + after_endpoint

# Write new file
with open('app/api/routes.py', 'w') as f:
    f.write(new_content)

print("✅ Successfully updated routes.py!")
print(f"   - Replaced advanced-analysis endpoint")
print(f"   - Added /models endpoint")
