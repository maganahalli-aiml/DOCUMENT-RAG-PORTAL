from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import List, Optional, Any, Dict
from datetime import datetime

# Initialize LangChain cache early
try:
    from src.cache.cache_manager import initialize_langchain_cache
    cache_manager = initialize_langchain_cache(cache_type="redis")
    print("✅ LangChain cache initialized successfully")
except Exception as e:
    print(f"⚠️ Failed to initialize LangChain cache: {e}")
    cache_manager = None

from src.document_ingestion.data_ingestion import (
    DocHandler,
    DocumentComparator,
    ChatIngestor,
    FaissManager
)

from src.document_analyser.data_analysis import DocumentAnalyzer
from src.document_compare.document_comparator import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG

# BASE_DIR = Path(__file__).resolve().parent.parent  # project root

# app.mount(
#     "/static",
#     StaticFiles(directory=BASE_DIR / "static"),
#     name="static"
# )

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")

app = FastAPI(title="Document Portal API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
async def serve_ui(request: Request):
    # templates/index.html ko render karega
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, Any]:
    health_info = {
        "status": "ok", 
        "service": "document-portal",
        "version": "enhanced-rag-v1.0",
        "features": [
            "multi-format-documents",
            "table-image-processing", 
            "deepeval-metrics",
            "conversational-rag",
            "langchain-cache"
        ],
        "timestamp": datetime.now().isoformat()
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
async def analyze_document(file: UploadFile = File(...)) -> Any:
    """Enhanced document analysis with AI-powered insights"""
    try:
        # Import necessary modules
        from src.document_ingestion.document_processors import DocumentProcessorFactory
        from src.document_analyser.data_analysis import DocumentAnalyzer
        
        # Get file content and metadata
        file_content = await file.read()
        file_size = len(file_content)
        
        # Better file extension extraction
        if file.filename and '.' in file.filename:
            file_extension = file.filename.split('.')[-1].lower()
        else:
            # Try to detect from content type
            content_type = file.content_type or ""
            if "pdf" in content_type:
                file_extension = "pdf"
            elif "text" in content_type:
                file_extension = "txt"
            elif "doc" in content_type:
                file_extension = "docx"
            else:
                file_extension = "txt"  # Default fallback
        
        print(f"[ENHANCED ANALYSIS] Analyzing file: {file.filename}, extension: {file_extension}, size: {file_size}")
        
        # Save file temporarily
        temp_path = f"data/temp_{file.filename}"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Extract text content based on file type
        extracted_text = ""
        documents_count = 0
        
        try:
            # Try enhanced processor first
            processor = DocumentProcessorFactory.get_processor(temp_path)
            documents = processor.process(temp_path)
            extracted_text = "\n".join([doc.page_content for doc in documents])
            documents_count = len(documents)
            print(f"[PROCESSOR] Used enhanced processor, extracted {documents_count} chunks")
        except ValueError:
            # Fallback to basic text extraction
            if file_extension in ['txt', 'md', 'csv']:
                extracted_text = file_content.decode('utf-8', errors='ignore')
                documents_count = 1
                print(f"[FALLBACK] Extracted text content for {file_extension}")
            elif file_extension == 'pdf':
                try:
                    dh = DocHandler()
                    saved_path = dh.save_pdf(FastAPIFileAdapter(file))
                    extracted_text = _read_pdf_via_handler(dh, saved_path)
                    documents_count = 1
                    print(f"[FALLBACK] Extracted PDF content")
                except Exception as pdf_error:
                    print(f"[ERROR] PDF extraction failed: {pdf_error}")
                    extracted_text = ""
            else:
                print(f"[WARNING] Unsupported file type: {file_extension}")
                extracted_text = ""
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # If we have text content, run AI analysis
        ai_analysis = {}
        content_preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        
        if extracted_text.strip():
            try:
                print(f"[AI ANALYSIS] Running DocumentAnalyzer on {len(extracted_text)} characters")
                analyzer = DocumentAnalyzer()
                ai_analysis = analyzer.analyze_document(extracted_text)
                print(f"[AI ANALYSIS] Completed successfully with keys: {list(ai_analysis.keys())}")
            except Exception as analysis_error:
                print(f"[AI ANALYSIS ERROR] {analysis_error}")
                ai_analysis = {
                    "Summary": [f"Analysis of {file.filename}", f"File type: {file_extension}", f"Content length: {len(extracted_text)} characters"],
                    "Title": file.filename or "Unknown Document",
                    "Author": "Not Available",
                    "DateCreated": "Not Available",
                    "LastModifiedDate": "Not Available",
                    "Publisher": "Not Available",
                    "Language": "Unknown",
                    "PageCount": str(documents_count),
                    "SentimentTone": "neutral"
                }
        else:
            # Minimal analysis for unsupported files
            ai_analysis = {
                "Summary": [f"File upload successful: {file.filename}", f"File type: {file_extension}", "Content analysis not available for this file type"],
                "Title": file.filename or "Unknown Document",
                "Author": "Not Available",
                "DateCreated": "Not Available",
                "LastModifiedDate": "Not Available",
                "Publisher": "Not Available",
                "Language": "Unknown",
                "PageCount": "Not Available",
                "SentimentTone": "neutral"
            }
        
        # Build comprehensive response
        response = {
            "status": "success",
            "filename": file.filename,
            "file_info": {
                "extension": file_extension,
                "size_mb": file_size / (1024 * 1024),
                "processing_time": 2.5  # Placeholder for actual timing
            },
            "documents_processed": documents_count,
            "total_content_length": len(extracted_text),
            "content_preview": content_preview,
            "summary": ai_analysis.get("Summary", ["Analysis completed"])[0] if ai_analysis.get("Summary") else "Analysis completed",
            "ai_insights": ai_analysis,
            "metadata": {
                "title": ai_analysis.get("Title", file.filename),
                "author": ai_analysis.get("Author", "Not Available"),
                "language": ai_analysis.get("Language", "Unknown"),
                "sentiment": ai_analysis.get("SentimentTone", "neutral"),
                "page_count": ai_analysis.get("PageCount", "Not Available")
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[RESPONSE] Returning enhanced analysis for {file.filename}")
        return response
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

@app.post("/chat")
async def simple_chat(request: Dict[str, str]) -> Any:
    """Simplified chat endpoint for quick testing"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # For now, return a simple response
        # This would integrate with your ConversationalRAG system
        response = f"Received your message: '{message}'. RAG system integration in progress."
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "session_id": "demo-session"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

@app.get("/evaluation/run")
async def run_evaluation():
    """Run RAG evaluation (mock/dev) and return parsed results.

    Returns
    -------
    dict
        { status, message, eval_id, results_file, report_file, results, logs }
    """
    try:
        import subprocess
        import json
        import os
        import re

        project_root = os.getcwd()  # Use current working directory (/app in container)
        py_candidates = [
            os.path.join(project_root, ".venv/bin/python"),
            os.path.join(project_root, "venv/bin/python"),
            "python",
        ]

        python_exe = None
        for cand in py_candidates:
            if os.path.exists(cand) or cand == "python":
                python_exe = cand
                break
        if python_exe is None:
            python_exe = "python"

        # Run the evaluation script
        result = subprocess.run(
            [python_exe, "quick_rag_evaluation.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        logs = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")

        if result.returncode != 0:
            return {
                "status": "error",
                "message": "Evaluation failed",
                "error": result.stderr,
                "logs": logs,
            }

        # Try to extract results/report file paths from stdout
        results_file = None
        report_file = None
        eval_id = None

        for line in (result.stdout or "").splitlines():
            m = re.search(r"Results saved to:\s*(evaluation_results/[^\s]+)", line)
            if m:
                results_file = os.path.join(project_root, m.group(1))
            m2 = re.search(r"Report saved to:\s*(evaluation_results/[^\s]+)", line)
            if m2:
                report_file = os.path.join(project_root, m2.group(1))

        if results_file and os.path.exists(results_file):
            try:
                with open(results_file, "r") as f:
                    results = json.load(f)
                # derive eval_id from filename
                base = os.path.basename(results_file)
                eval_id = base.replace("_results.json", "")
                return {
                    "status": "success",
                    "message": "Evaluation completed successfully",
                    "eval_id": eval_id,
                    "results_file": results_file,
                    "report_file": report_file,
                    "results": results,
                    "logs": logs,
                }
            except Exception as parse_err:
                # Fallback: return raw logs
                return {
                    "status": "success",
                    "message": "Evaluation completed, but failed to parse results file",
                    "results_file": results_file,
                    "report_file": report_file,
                    "logs": logs,
                    "parse_error": str(parse_err),
                }
        else:
            # Could not find results file, return logs
            return {
                "status": "success",
                "message": "Evaluation completed, but results file not found",
                "logs": logs,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")

@app.get("/evaluation/latest")
async def evaluation_latest():
    """Return the latest evaluation results JSON from evaluation_results directory."""
    try:
        import glob
        import json
        import os

        results_dir = os.path.join(os.path.dirname(__file__), "..", "evaluation_results")
        results_dir = os.path.abspath(results_dir)
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
        raise HTTPException(status_code=500, detail=f"Failed to load latest evaluation: {e}")

@app.get("/system/info")
async def system_info():
    """Get system information and status"""
    try:
        import platform
        import psutil
        from datetime import datetime
        
        # Get system information
        system_data = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check service status
        services = {
            "fastapi": "running",
            "document_processors": "available",
            "evaluation_framework": "available"
        }
        
        return {
            "status": "ok",
            "system": system_data,
            "services": services,
            "features": {
                "multi_format_support": True,
                "table_image_processing": True,
                "evaluation_metrics": True,
                "conversational_rag": True
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

def _read_pdf_via_handler(handler: DocHandler, path: str) -> str:
    if hasattr(handler, "read_pdf"):
        return handler.read_pdf(path)  # type: ignore
    if hasattr(handler, "read_"):
        return handler.read_(path)  # type: ignore
    raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")
    
@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = _read_pdf_via_handler(dh, saved_path)
        analyzer=DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    
@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        dc = DocumentComparator()
        ref_path, act_path = dc.save_uploaded_files(FastAPIFileAdapter(reference), FastAPIFileAdapter(actual))
        
        # Read both documents based on file type
        def read_document(file_path):
            if str(file_path).endswith('.pdf'):
                return dc.read_pdf(file_path)
            else:
                # Read as text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        ref_text = read_document(ref_path)
        act_text = read_document(act_path)
        
        # Calculate similarity metrics
        from src.document_compare.similarity_calculator import SimilarityCalculator
        calc = SimilarityCalculator()
        
        # Calculate metrics
        similarity_score = calc.calculate_similarity(ref_text, act_text)
        common_words, unique_words = calc.calculate_word_metrics(ref_text, act_text)
        
        # Generate a simple summary
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
        
        return {
            "similarity_score": float(similarity_score),
            "common_words": int(common_words),
            "unique_words": int(unique_words),
            "summary": summary,
            "session_id": dc.session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "similarity_score": 0.0,
            "common_words": 0,
            "unique_words": 0,
            "summary": f"Comparison failed: {str(e)}",
            "error": str(e)
        }

@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        ci.build_retriever(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        return {
            "status": "success",
            "session_id": ci.session_id, 
            "k": k, 
            "use_session_dirs": use_session_dirs,
            "message": f"Successfully processed {len(files)} file(s) and built search index."
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "session_id": session_id,
            "message": f"Indexing failed: {str(e)}"
        }
    
@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        # Prepare FAISS index path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        # Initialize LCEL-style RAG pipeline
        rag = ConversationalRAG(session_id=session_id) #type: ignore
        rag.load_retriever_from_faiss(index_dir)

        # Optional: For now we pass empty chat history
        response = rag.invoke(question, chat_history=[])

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


# command for executing the fast api
# uvicorn api.main:app --port 8000 --reload# TEST COMMENT Sat Aug 30 16:28:57 EDT 2025
