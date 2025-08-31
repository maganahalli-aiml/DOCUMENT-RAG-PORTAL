from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
import uuid
import traceback
import logging
from typing import List, Optional, Any, Dict
from datetime import datetime
import json

# Initialize LangChain cache early
try:
    from src.cache.cache_manager import initialize_langchain_cache
    cache_manager = initialize_langchain_cache(cache_type="memory")
    print("✅ LangChain cache initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize LangChain cache: {e}")
    cache_manager = None

# Create FastAPI app
app = FastAPI(
    title="Document RAG Portal", 
    version="1.0.0",
    description="Enhanced RAG system with multi-format document support and LangChain caching"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
except Exception:
    templates = None

# Configuration
FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Serve the main UI"""
    if templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception:
            pass
    
    # Fallback HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document RAG Portal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .status { color: #28a745; font-weight: bold; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Document RAG Portal</h1>
            <p class="status">✅ Service is running successfully!</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <h3>🏥 Health Check</h3>
                <p><a href="/health">GET /health</a> - Check service status</p>
            </div>
            
            <div class="endpoint">
                <h3>📊 API Documentation</h3>
                <p><a href="/docs">GET /docs</a> - Interactive API documentation</p>
            </div>
            
            <div class="endpoint">
                <h3>🔍 System Information</h3>
                <p><a href="/system/info">GET /system/info</a> - Get system details</p>
            </div>
            
            <div class="endpoint">
                <h3>📄 Document Analysis</h3>
                <p><strong>POST /analyze-document</strong> - Upload and analyze documents</p>
                <p>Supports: PDF, PowerPoint, Excel, Word, Markdown, Text, CSV files</p>
            </div>
            
            <div class="endpoint">
                <h3>💬 Chat Interface</h3>
                <p><strong>POST /chat</strong> - Chat with your documents</p>
            </div>
            
            <div class="endpoint">
                <h3>📈 Evaluation</h3>
                <p><a href="/evaluation/run">GET /evaluation/run</a> - Run RAG evaluation tests</p>
            </div>
            
            <h2>🌐 Streamlit Web Interface</h2>
            <p>Visit <a href="http://localhost:8501">http://localhost:8501</a> for the full web interface</p>
            
            <hr>
            <p><em>Enhanced RAG Portal with multi-format support, table/image processing, and evaluation framework</em></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint with cache status"""
    health_info = {
        "status": "ok",
        "service": "document-portal",
        "version": "enhanced-rag-v1.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "multi-format-documents",
            "table-image-processing", 
            "deepeval-metrics",
            "conversational-rag",
            "langchain-cache"
        ]
    }
    
    # Add cache information if available
    if cache_manager:
        try:
            cache_stats = cache_manager.get_cache_stats()
            health_info["cache"] = cache_stats
        except Exception as e:
            health_info["cache"] = {"error": str(e)}
    else:
        health_info["cache"] = {"status": "disabled"}
    
    return health_info

@app.get("/cache/status")
def cache_status() -> Dict[str, Any]:
    """Cache status and statistics endpoint"""
    if not cache_manager:
        return {"error": "Cache not initialized"}
    
    try:
        stats = cache_manager.get_cache_stats()
        info = cache_manager.get_cache_info()
        
        return {
            "cache_enabled": True,
            "statistics": stats,
            "info": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "cache_enabled": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/cache/clear")
def clear_cache() -> Dict[str, Any]:
    """Clear the LangChain cache"""
    if not cache_manager:
        return {"error": "Cache not initialized"}
    
    try:
        cache_manager.clear_cache()
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...), request: Request = None) -> Any:
    """Enhanced document analysis with multi-format support"""
    try:
        # Extract debug headers
        request_id = request.headers.get("X-Request-ID", "unknown") if request else "unknown"
        client_file_hash = request.headers.get("X-File-Hash", "unknown") if request else "unknown"
        
        print(f"[ANALYSIS START] Request ID: {request_id}, File: {file.filename}, Client Hash: {client_file_hash}")
        
        # Create upload directory
        os.makedirs(UPLOAD_BASE, exist_ok=True)
        
        # Get file info
        file_content = await file.read()
        file_size = len(file_content)
        file_extension = file.filename.split('.')[-1].lower() if file.filename else 'unknown'
        
        # Calculate server-side file hash for verification
        import hashlib
        server_file_hash = hashlib.md5(file_content).hexdigest()
        print(f"[HASH CHECK] Client: {client_file_hash}, Server: {server_file_hash[:8]}")
        
        # Save file
        file_path = os.path.join(UPLOAD_BASE, f"uploaded_{file.filename}")
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        print(f"[FILE SAVED] Path: {file_path}, Size: {file_size} bytes")
        
        # Try to use enhanced document processors
        try:
            import sys
            # Add the project root to Python path
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            from src.document_ingestion.document_processors import DocumentProcessorFactory
            
            processor = DocumentProcessorFactory.get_processor(file_path)
            if processor:
                print(f"[PROCESSING] Using enhanced processor for {file.filename}")
                documents = processor.process(file_path)
                
                # Get summary content for verification
                summary_content = ""
                if documents and documents[0].page_content:
                    summary_content = documents[0].page_content[:500]
                
                print(f"[ANALYSIS COMPLETE] Documents: {len(documents)}, Content preview: {summary_content[:100]}...")
                
                return {
                    "status": "success",
                    "processor": "enhanced",
                    "filename": file.filename,
                    "file_type": file_extension,
                    "file_size": file_size,
                    "documents_processed": len(documents),
                    "total_content_length": sum(len(doc.page_content) for doc in documents),
                    "metadata": documents[0].metadata if documents else {},
                    "summary": summary_content,
                    "preview": documents[0].page_content[:300] + "..." if documents and documents[0].page_content else "No content extracted",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id,
                    "server_file_hash": server_file_hash,
                    "client_file_hash": client_file_hash
                }
        except Exception as e:
            print(f"[ERROR] Enhanced processor failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback: basic file analysis
        print(f"[FALLBACK] Using basic processing for {file.filename}")
        content_preview = ""
        if file_extension in ['txt', 'md']:
            content_preview = file_content.decode('utf-8', errors='ignore')[:300] + "..."
        elif file_extension == 'pdf':
            content_preview = "PDF file uploaded - content extraction requires PDF processing library"
        else:
            content_preview = f"File type: {file_extension} - specialized processing available"
        
        return {
            "status": "success",
            "processor": "basic",
            "filename": file.filename,
            "file_type": file_extension,
            "file_size": file_size,
            "summary": content_preview,
            "content_preview": content_preview,
            "message": f"File uploaded successfully. Enhanced processing for {file_extension} files available with full processors.",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "server_file_hash": server_file_hash,
            "client_file_hash": client_file_hash
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def process_file_basic(file_path: str) -> List[Any]:
    """Basic file processing fallback when enhanced processors fail"""
    try:
        from langchain.schema import Document as LangChainDocument
        from pathlib import Path
        
        file_name = Path(file_path).name
        file_extension = Path(file_path).suffix.lower()
        
        print(f"Attempting basic processing for {file_name}")
        
        # Basic text extraction based on file type
        content = ""
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        elif file_extension == '.md':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        elif file_extension == '.pdf':
            try:
                # Try PyPDF2 for basic PDF reading
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    content = ""
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
            except Exception as pdf_error:
                print(f"Basic PDF processing failed: {pdf_error}")
                content = f"PDF file: {file_name} - content extraction requires enhanced processors"
        
        else:
            # For other file types, create a placeholder document
            content = f"File: {file_name} (Type: {file_extension}) - Enhanced processing required for full content extraction"
        
        if content.strip():
            # Create a basic document
            doc = LangChainDocument(
                page_content=content,
                metadata={
                    "source": file_path,
                    "filename": file_name,
                    "type": file_extension,
                    "processing": "basic"
                }
            )
            return [doc]
        else:
            print(f"No content extracted from {file_name}")
            return []
            
    except Exception as e:
        print(f"Basic processing failed for {file_path}: {e}")
        return []

async def get_document_metadata(index_path: str) -> Optional[Dict[str, Any]]:
    """Get metadata about documents in the index"""
    try:
        metadata_file = os.path.join(index_path, 'ingested_meta.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                return metadata
    except Exception as e:
        print(f"Error reading metadata: {e}")
    return None

async def get_document_overview(index_path: str) -> str:
    """Get an overview of all documents in the index"""
    try:
        metadata = await get_document_metadata(index_path)
        if metadata and 'files' in metadata:
            files = metadata.get('files', [])
            chunks_per_file = metadata.get('chunks_per_file', {})
            total_chunks = metadata.get('total_chunks', 0)
            
            if files:
                overview = f"📄 **Document Overview**\n\n"
                overview += f"I have access to {len(files)} documents with a total of {total_chunks} content chunks:\n\n"
                
                for i, file in enumerate(files, 1):
                    chunks = chunks_per_file.get(file, 0)
                    overview += f"{i}. **{file}** - {chunks} content chunks\n"
                
                overview += f"\n💬 **You can ask me questions about:**\n"
                overview += f"- Content from any specific document\n"
                overview += f"- Comparisons between documents\n"
                overview += f"- Summaries of individual or all documents\n"
                overview += f"- Specific information contained in these files\n"
                
                return overview
            else:
                return "I have access to your uploaded documents, but the file list is not available at the moment."
        else:
            # Fallback: try to get basic info from the index directory
            try:
                # Look for any files in the data directory that match this session
                session_id = os.path.basename(index_path)
                data_dir = f"data/{session_id}"
                if os.path.exists(data_dir):
                    files = [f for f in os.listdir(data_dir) if not f.startswith('.')]
                    if files:
                        overview = f"📄 **Document Overview**\n\n"
                        overview += f"I have access to {len(files)} uploaded documents:\n\n"
                        for i, file in enumerate(files, 1):
                            overview += f"{i}. **{file}**\n"
                        overview += f"\n💬 **Ask me questions about these documents!**"
                        return overview
                
                return "I have access to your uploaded documents. You can ask me questions about their content!"
            except Exception:
                return "I have access to your uploaded documents. You can ask me questions about their content!"
    except Exception as e:
        print(f"Error in get_document_overview: {e}")
        return "I have access to your uploaded documents. You can ask me questions about their content!"

@app.post("/chat")
async def simple_chat(request: Dict[str, str]) -> Any:
    """Enhanced chat endpoint for RAG interactions with multi-document awareness"""
    try:
        message = request.get("message", request.get("query", ""))
        session_id = request.get("session_id", "default_session")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Try to use actual RAG functionality
        try:
            # Import RAG components
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from src.document_chat.retrieval import ConversationalRAG
            
            # Look for available FAISS indices and corresponding data directories
            faiss_base = "/Users/alampata/Desktop/LLMOPS/DOCUMENT-RAG-PORTAL/faiss_index"
            data_base = "/Users/alampata/Desktop/LLMOPS/DOCUMENT-RAG-PORTAL/data"
            available_indices = []
            
            if os.path.exists(faiss_base):
                for item in os.listdir(faiss_base):
                    index_path = os.path.join(faiss_base, item)
                    if os.path.isdir(index_path):
                        # Check if corresponding data directory exists and has files
                        data_path = os.path.join(data_base, item)
                        if os.path.exists(data_path):
                            files_in_data = [f for f in os.listdir(data_path) if not f.startswith('.')]
                            if files_in_data:  # Only include if it has actual documents
                                available_indices.append(index_path)
            
            if available_indices:
                # Use the most recent index that has corresponding documents
                latest_index = max(available_indices, key=os.path.getmtime)
                print(f"Using most recent index with documents: {latest_index}")
                
                # Check if this is a question about document overview or specific documents
                overview_keywords = ["what documents", "what files", "list documents", "document overview", "all documents", "each document talk about", "documents do i have"]
                is_overview_request = any(keyword in message.lower() for keyword in overview_keywords)
                
                if is_overview_request:
                    # Provide document overview
                    response = await get_document_overview(latest_index)
                else:
                    # Regular RAG query with enhanced error handling
                    try:
                        rag = ConversationalRAG(session_id=session_id)
                        rag.load_retriever_from_faiss(latest_index)
                        
                        # Enhanced response that includes document context
                        enhanced_message = f"""
                        Based on the uploaded documents, please answer: {message}
                        
                        If the question is about a specific document or person mentioned in the documents, 
                        please provide information from the relevant document and mention which document 
                        contains this information.
                        """
                        
                        response = rag.invoke(user_input=enhanced_message, chat_history=[])
                        
                        # Add document context to response safely
                        try:
                            doc_info = await get_document_metadata(latest_index)
                            if doc_info and 'files' in doc_info and doc_info['files']:
                                files_list = doc_info['files']
                                response += f"\n\n📄 **Available Documents**: {', '.join(files_list)}"
                        except Exception as context_error:
                            print(f"Error adding document context: {context_error}")
                            # Continue without document context
                            pass
                            
                    except Exception as rag_error:
                        # Handle specific FAISS loading errors
                        error_msg = str(rag_error)
                        if "allow_dangerous_deserialization" in error_msg or "FAISS" in error_msg:
                            response = f"I understand your question: '{message}'. There's a compatibility issue with the document index that I'm working to resolve. The documents are available but the search system needs to be updated. Please try re-uploading your documents to create a fresh index."
                        else:
                            response = f"I received your question: '{message}'. There was an issue accessing the document index ({error_msg}), but I'm working to provide you with relevant information from available documents."
                        
                        print(f"RAG error for query '{message}': {rag_error}")
                        
                        # Try to get document overview as fallback
                        try:
                            overview = await get_document_overview(latest_index)
                            response += f"\n\n{overview}"
                        except:
                            pass
                
                return {
                    "response": response,
                    "query": message,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "status": "rag-active",
                    "index_used": os.path.basename(latest_index)
                }
                
            else:
                # No indices available, return informative message
                return {
                    "response": f"I understand your question: '{message}'. However, no document indices are currently available. Please upload and process documents first to enable RAG functionality.",
                    "query": message,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "status": "no-documents"
                }
                
        except Exception as rag_error:
            # Fallback to simple response if RAG fails
            fallback_response = f"I received your question: '{message}'. There was an issue with the RAG system ({str(rag_error)}), but I'm working to provide you with relevant information from available documents."
            
            return {
                "response": fallback_response,
                "query": message,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "status": "fallback-mode",
                "error": str(rag_error)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/evaluation/run")
async def run_evaluation():
    """Run RAG evaluation suite"""
    try:
        import subprocess
        
        # Try to run the evaluation script
        result = subprocess.run(
            [".venv/bin/python", "quick_rag_evaluation.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Evaluation completed successfully",
                "output": result.stdout[-1000:],  # Last 1000 chars
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error", 
                "message": "Evaluation script failed",
                "error": result.stderr[-500:],  # Last 500 chars of error
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "Evaluation timed out after 60 seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Evaluation failed: {str(e)}"
        }

@app.get("/evaluation/latest")
async def evaluation_latest():
    """Return the latest evaluation results JSON from evaluation_results directory."""
    try:
        import glob
        import json
        import os

        # evaluation_results is at project root
        results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evaluation_results"))
        pattern = os.path.join(results_dir, "*_results.json")
        files = glob.glob(pattern)
        if not files:
            return {"status": "empty", "message": "No evaluation results found"}

        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "r") as f:
            data = json.load(f)
        return {
            "status": "ok",
            "results_file": latest_file,
            "results": data,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to load latest evaluation: {e}"}

@app.get("/system/info")
async def system_info():
    """Get system information and status"""
    try:
        import platform
        import psutil
        
        # Basic system information
        system_data = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count() if psutil else "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        # Check available features
        features = {}
        
        try:
            from src.document_ingestion.document_processors import DocumentProcessorFactory
            features["enhanced_document_processing"] = True
        except:
            features["enhanced_document_processing"] = False
        
        try:
            from src.evaluation.mock_deepeval_metrics import MockRAGEvaluationMetrics
            features["evaluation_framework"] = True
        except:
            features["evaluation_framework"] = False
        
        # Check file counts
        file_counts = {
            "uploaded_files": len(os.listdir(UPLOAD_BASE)) if os.path.exists(UPLOAD_BASE) else 0,
            "faiss_indices": len(os.listdir(FAISS_BASE)) if os.path.exists(FAISS_BASE) else 0
        }
        
        return {
            "status": "ok",
            "system": system_data,
            "features": features,
            "file_counts": file_counts,
            "endpoints": [
                "GET /health",
                "POST /analyze-document", 
                "POST /chat",
                "GET /evaluation/run",
                "GET /system/info"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Legacy endpoints for the original beautiful frontend
@app.post("/analyze")
async def legacy_analyze(file: UploadFile = File(...)) -> Any:
    """Legacy analyze endpoint for original frontend"""
    return await analyze_document(file)


@app.post("/chat/index")
async def legacy_chat_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5)
) -> Any:
    """Legacy chat index endpoint - creates FAISS index from uploaded files"""
    try:
        import time
        import json
        from pathlib import Path
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        # Create session directory
        session_dir = Path("data") / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded files with validation
        file_paths = []
        upload_errors = []
        
        for file in files:
            try:
                # Validate file
                if not file.filename:
                    upload_errors.append("File with empty filename")
                    continue
                    
                if file.size == 0:
                    upload_errors.append(f"Empty file: {file.filename}")
                    continue
                
                # Read file content
                file_content = await file.read()
                if not file_content:
                    upload_errors.append(f"No content in file: {file.filename}")
                    continue
                
                # Save file
                file_path = session_dir / file.filename
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                    
                file_paths.append(str(file_path))
                print(f"✅ Uploaded: {file.filename} ({len(file_content)} bytes)")
                
            except Exception as upload_error:
                error_msg = f"Upload error for {getattr(file, 'filename', 'unknown')}: {str(upload_error)}"
                upload_errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        if not file_paths:
            error_detail = "No files could be uploaded successfully."
            if upload_errors:
                error_detail += f"\nErrors: {'; '.join(upload_errors)}"
            return {
                "status": "error",
                "session_id": session_id,
                "message": error_detail,
                "upload_errors": upload_errors
            }
        
        print(f"Successfully uploaded {len(file_paths)} files to {session_dir}")
        
        # Create FAISS index with improved error handling
        try:
            # Import enhanced document processors with fallback
            import sys
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Try enhanced processors first, fallback to basic processing
            all_documents = []
            processed_files = []
            failed_files = []
            
            # Try to import enhanced processors
            try:
                from src.document_ingestion.document_processors import DocumentProcessorFactory
                processor_factory = DocumentProcessorFactory()
                enhanced_processing = True
                print("Using enhanced document processors")
            except Exception as import_error:
                print(f"Enhanced processors not available: {import_error}")
                import traceback
                traceback.print_exc()
                enhanced_processing = False
            
            # Process each file
            for file_path in file_paths:
                file_name = Path(file_path).name
                print(f"Processing file: {file_name}")
                
                try:
                    if enhanced_processing:
                        # Use enhanced processors
                        processor = processor_factory.get_processor(file_path)
                        if processor:
                            documents = processor.process(file_path)  # Fixed: use process() not process_document()
                            all_documents.extend(documents)
                            processed_files.append(file_name)
                            print(f"✅ Enhanced processing: {len(documents)} chunks from {file_name}")
                        else:
                            print(f"⚠️ No enhanced processor for {file_name}, trying basic processing")
                            basic_docs = await process_file_basic(file_path)
                            if basic_docs:
                                all_documents.extend(basic_docs)
                                processed_files.append(file_name)
                    else:
                        # Use basic processing
                        basic_docs = await process_file_basic(file_path)
                        if basic_docs:
                            all_documents.extend(basic_docs)
                            processed_files.append(file_name)
                            print(f"✅ Basic processing: {len(basic_docs)} chunks from {file_name}")
                        
                except Exception as file_error:
                    print(f"❌ Error processing {file_name}: {file_error}")
                    failed_files.append(f"{file_name}: {str(file_error)}")
                    continue
            
            # Check if we have any successfully processed documents
            if not all_documents:
                error_details = "\n".join(failed_files) if failed_files else "Unknown processing errors"
                return {
                    "status": "error",
                    "session_id": session_id,
                    "message": f"No documents could be processed successfully.\nErrors:\n{error_details}",
                    "failed_files": failed_files
                }
            
            print(f"Successfully processed {len(processed_files)} files with {len(all_documents)} total chunks")
            
            # Import required components for FAISS
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            from utils.model_loader import ModelLoader
            
            # Split documents if needed
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
            
            # Re-split any large documents
            final_splits = []
            for doc in all_documents:
                if len(doc.page_content) > chunk_size * 1.5:
                    # Document is too large, split it further
                    sub_splits = text_splitter.split_documents([doc])
                    final_splits.extend(sub_splits)
                else:
                    # Document is already appropriately sized
                    final_splits.append(doc)
            
            print(f"Final document chunks: {len(final_splits)}")
            
            # Create embeddings and FAISS index
            model_loader = ModelLoader()
            embeddings = model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(final_splits, embeddings)
            
            # Save index
            index_dir = Path("faiss_index") / session_id
            index_dir.mkdir(parents=True, exist_ok=True)
            vectorstore.save_local(str(index_dir))
            
            # Calculate chunks per file more accurately
            chunks_per_file = {}
            for file_name in processed_files:
                file_chunks = [d for d in final_splits if file_name in d.metadata.get('source', '')]
                chunks_per_file[file_name] = len(file_chunks)
            
            # Save enhanced metadata
            metadata = {
                'rows': {f"{fp}::": True for fp in file_paths if Path(fp).name in processed_files},
                'files': processed_files,
                'chunks_per_file': chunks_per_file,
                'total_chunks': len(final_splits),
                'processed_files': processed_files,
                'failed_files': failed_files,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(index_dir / 'ingested_meta.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            result = {
                "status": "success",
                "session_id": session_id,
                "files_processed": len(processed_files),
                "files": processed_files,
                "chunks_created": len(final_splits),
                "chunks_per_file": chunks_per_file,
                "message": f"Index created successfully with {len(final_splits)} chunks from {len(processed_files)} files"
            }
            
            if failed_files:
                result["warnings"] = f"Some files failed to process: {failed_files}"
                result["failed_files"] = failed_files
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e),
                "message": "Failed to create FAISS index"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index creation failed: {str(e)}")


@app.post("/chat/query")
async def legacy_chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5)
) -> Any:
    """Legacy chat query endpoint"""
    try:
        # Import RAG components
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from src.document_chat.retrieval import ConversationalRAG
        
        # Find the appropriate index
        if session_id:
            index_path = f"faiss_index/{session_id}"
        else:
            # Use the most recent index
            faiss_base = "faiss_index"
            available_indices = []
            
            if os.path.exists(faiss_base):
                for item in os.listdir(faiss_base):
                    index_path_full = os.path.join(faiss_base, item)
                    if os.path.isdir(index_path_full):
                        available_indices.append(index_path_full)
            
            if not available_indices:
                return {
                    "answer": "No document indices available. Please upload and index documents first.",
                    "session_id": None,
                    "status": "no_index"
                }
            
            index_path = max(available_indices, key=os.path.getmtime)
            session_id = os.path.basename(index_path)
        
        # Initialize RAG and get response
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_path)
        
        response = rag.invoke(user_input=question, chat_history=[])
        
        return {
            "answer": response,
            "session_id": session_id,
            "question": question,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "answer": f"Error processing question: {str(e)}",
            "session_id": session_id,
            "question": question,
            "status": "error"
        }


@app.post("/compare")
async def compare_documents(
    reference: UploadFile = File(...),
    actual: UploadFile = File(...)
) -> Any:
    """Compare two documents and calculate similarity"""
    request_id = str(uuid.uuid4())[:8]
    print(f"[{request_id}] Document comparison request - Reference: {reference.filename}, Actual: {actual.filename}")
    
    try:
        # Check file sizes to prevent timeout on very large files
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
        
        # Read document contents directly
        ref_content = await reference.read()
        act_content = await actual.read()
        
        if len(ref_content) > MAX_FILE_SIZE or len(act_content) > MAX_FILE_SIZE:
            return {
                "similarity_score": 0.0,
                "common_words": 0,
                "unique_words": 0,
                "summary": "File too large for comparison. Please use files smaller than 50MB.",
                "error": "File size limit exceeded"
            }
        
        print(f"[{request_id}] File sizes - Reference: {len(ref_content)} bytes, Actual: {len(act_content)} bytes")
        
        # Convert bytes to text with timeout protection
        try:
            ref_text = ref_content.decode('utf-8')
        except UnicodeDecodeError:
            ref_text = ref_content.decode('utf-8', errors='ignore')
            
        try:
            act_text = act_content.decode('utf-8')
        except UnicodeDecodeError:
            act_text = act_content.decode('utf-8', errors='ignore')
        
        # Truncate very long texts to prevent timeout - increased to 500k characters
        MAX_TEXT_LENGTH = 500000  # 500k characters
        if len(ref_text) > MAX_TEXT_LENGTH:
            ref_text = ref_text[:MAX_TEXT_LENGTH] + "..."
            print(f"[{request_id}] Reference text truncated to {MAX_TEXT_LENGTH} characters")
            
        if len(act_text) > MAX_TEXT_LENGTH:
            act_text = act_text[:MAX_TEXT_LENGTH] + "..."
            print(f"[{request_id}] Actual text truncated to {MAX_TEXT_LENGTH} characters")
        
        # Calculate similarity using our similarity calculator
        from src.document_compare.similarity_calculator import SimilarityCalculator
        calc = SimilarityCalculator()
        
        print(f"[{request_id}] Starting similarity calculation...")
        similarity_score = calc.calculate_similarity(ref_text, act_text)
        common_words, unique_words = calc.calculate_word_metrics(ref_text, act_text)
        print(f"[{request_id}] Similarity calculation completed")
        
        # Generate summary
        summary = f"Documents have {similarity_score:.1%} similarity. "
        summary += f"Found {common_words} common words and {unique_words} unique words. "
        
        if similarity_score > 0.8:
            summary += "Documents are very similar with minor differences."
        elif similarity_score > 0.5:
            summary += "Documents share significant content but have notable differences."
        elif similarity_score > 0.2:
            summary += "Documents have some common elements but are largely different."
        else:
            summary += "Documents are very different with minimal overlap."
        
        print(f"[{request_id}] Comparison completed - Similarity: {similarity_score:.2f}, Common: {common_words}, Unique: {unique_words}")
        
        return {
            "similarity_score": float(similarity_score),
            "common_words": int(common_words),
            "unique_words": int(unique_words),
            "summary": summary
        }
        
    except Exception as e:
        print(f"[{request_id}] Comparison failed: {e}")
        return {
            "similarity_score": 0.0,
            "common_words": 0,
            "unique_words": 0,
            "summary": f"Comparison failed: {str(e)}",
            "error": str(e)
        }


# File upload helper
class FastAPIFileAdapter:
    """Adapter for FastAPI UploadFile to match expected interface"""
    def __init__(self, upload_file: UploadFile):
        self._upload_file = upload_file
        self.name = upload_file.filename
    
    def getbuffer(self) -> bytes:
        self._upload_file.file.seek(0)
        return self._upload_file.file.read()

@app.post("/rebuild-index")
async def rebuild_index_with_enhanced_processing() -> Any:
    """Rebuild FAISS index using enhanced document processors for current session"""
    try:
        session_id = "session_1756437542"  # Current active session
        session_dir = os.path.join("data", session_id)
        
        if not os.path.exists(session_dir):
            return {"error": f"Session directory {session_id} not found"}
        
        # Get all files in session directory
        files = []
        for filename in os.listdir(session_dir):
            filepath = os.path.join(session_dir, filename)
            if os.path.isfile(filepath):
                files.append(filepath)
        
        if not files:
            return {"error": "No files found in session directory"}
        
        # Process files with enhanced processors and rebuild FAISS index manually
        from src.document_ingestion.document_processors import DocumentProcessorFactory
        from src.document_ingestion.data_ingestion import FaissManager
        from utils.model_loader import ModelLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        # Process all files with enhanced processors
        all_documents = []
        processed_files = []
        
        for filepath in files:
            try:
                processor = DocumentProcessorFactory.get_processor(filepath)
                docs = processor.process(filepath)
                all_documents.extend(docs)
                processed_files.append(os.path.basename(filepath))
                print(f"Enhanced processing: {os.path.basename(filepath)} -> {len(docs)} chunks")
            except Exception as e:
                print(f"Enhanced processor failed for {filepath}: {e}")
                # Fallback to basic processing would go here
                
        if not all_documents:
            return {"error": "No documents could be processed"}
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(all_documents)
        
        # Rebuild FAISS index - delete existing index first to force recreation
        model_loader = ModelLoader()
        faiss_dir = os.path.join("faiss_index", session_id)
        
        # Delete existing index to force recreation
        if os.path.exists(faiss_dir):
            import shutil
            shutil.rmtree(faiss_dir)
            print(f"Deleted existing FAISS index at {faiss_dir}")
        
        faiss_manager = FaissManager(faiss_dir, model_loader)
        
        texts = [c.page_content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        
        # Create new vector store (will create since we deleted the old one)
        vector_store = faiss_manager.load_or_create(texts=texts, metadatas=metadatas)
        
        return {
            "status": "success",
            "message": f"Index rebuilt with enhanced processing for session {session_id}",
            "files_processed": len(processed_files),
            "processed_files": processed_files,
            "total_documents": len(all_documents),
            "total_chunks": len(chunks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to rebuild index: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
