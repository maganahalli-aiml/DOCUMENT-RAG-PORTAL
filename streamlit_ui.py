import streamlit as st
import requests
import json
from datetime import datetime
import time

st.set_page_config(
    page_title="Document RAG Portal",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, pleasing UX design with high specificity
st.markdown("""
<style>
    /* Force override Streamlit's default styling */
    .stApp, .stApp > div, .main, .main .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }
    
    /* Override any Streamlit dark mode classes */
    .stApp[data-theme="dark"], 
    .stApp[data-theme="dark"] .main,
    .stApp[data-theme="dark"] .main .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }
    
    /* Sidebar complete override */
    section[data-testid="stSidebar"],
    .css-1d391kg,
    .css-17eq0hr,
    .css-k1vhr4 {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    section[data-testid="stSidebar"] > div,
    .css-1d391kg > div,
    .css-17eq0hr > div {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] .css-1d391kg,
    section[data-testid="stSidebar"] .css-1d391kg > div {
        background: transparent !important;
    }
    
    /* Sidebar text colors */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .css-10trblm {
        color: white !important;
    }
    
    /* Sidebar navigation elements */
    section[data-testid="stSidebar"] .css-1629p8f h1,
    section[data-testid="stSidebar"] .css-1629p8f h2,
    section[data-testid="stSidebar"] .css-1629p8f h3 {
        color: white !important;
    }
    
    /* Main content area with glassmorphism */
    .main .block-container {
        padding: 3rem 2rem !important;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 25px !important;
        margin: 2rem !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Enhanced header styling */
    .main-header {
        font-size: 4rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        background-clip: text !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 1rem !important;
        font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif !important;
        letter-spacing: -0.03em !important;
        text-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    .main-subtitle {
        text-align: center !important;
        color: #6c757d !important;
        font-size: 1.3rem !important;
        margin-bottom: 4rem !important;
        font-weight: 400 !important;
        opacity: 0.9 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Feature cards with enhanced styling */
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
        padding: 2.5rem !important;
        border-radius: 25px !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
        margin: 2rem 0 !important;
        color: #2d3748 !important;
        box-shadow: 0 8px 40px rgba(102, 126, 234, 0.1) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .feature-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 5px !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        color: #155724 !important;
        padding: 1.5rem !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(21, 87, 36, 0.15) !important;
        font-weight: 600 !important;
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        color: #721c24 !important;
        padding: 1.5rem !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(114, 28, 36, 0.15) !important;
        font-weight: 600 !important;
    }
    
    /* Streamlit components override */
    .stButton > button {
        border-radius: 15px !important;
        font-weight: 700 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    /* File uploader styling */
    .uploadedFile, [data-testid="stFileUploader"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 3px dashed rgba(102, 126, 234, 0.3) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(102, 126, 234, 0.7) !important;
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 3px solid rgba(102, 126, 234, 0.2) !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 15px !important;
        border: 3px solid rgba(102, 126, 234, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem !important;
        background: rgba(255, 255, 255, 0.8) !important;
        padding: 1rem !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 15px !important;
        color: #667eea !important;
        font-weight: 700 !important;
        border: 2px solid transparent !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border: none !important;
        border-radius: 15px !important;
        color: #155724 !important;
        font-weight: 600 !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(21, 87, 36, 0.1) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border: none !important;
        border-radius: 15px !important;
        color: #721c24 !important;
        font-weight: 600 !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(114, 28, 36, 0.1) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border: none !important;
        border-radius: 15px !important;
        color: #0c5460 !important;
        font-weight: 600 !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(12, 84, 96, 0.1) !important;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Apply animations */
    .main .block-container > div {
        animation: fadeInUp 0.8s ease-out !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
</style>
""", unsafe_allow_html=True)

# Main title with modern styling
st.markdown('<div class="main-header">📄 Document RAG Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">🚀 Advanced Document Analysis & Conversational AI</div>', unsafe_allow_html=True)

# Configuration
FASTAPI_URL = "http://localhost:8080"

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# Check API status
@st.cache_data(ttl=30)
def check_api_status():
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=3)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

api_online, health_data = check_api_status()

if api_online:
    st.sidebar.markdown('<div class="status-success">API Server Online</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-error">API Server Offline</div>', unsafe_allow_html=True)
    st.sidebar.error("Make sure FastAPI server is running on port 8080")

page = st.sidebar.selectbox("Choose a page", [
    "Home & Quick Start", 
    "Document Upload & Chat", 
    "Document Analysis",
    "Document Comparison", 
    "System Dashboard"
])

if page == "Home & Quick Start":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Welcome to Document RAG Portal")
        st.markdown("""
        **A powerful document analysis and chat system with enhanced RAG capabilities.**
        
        ### 🎯 Key Features:
        """)
        
        features = [
            ("📄 Multi-Format Support", "PDF, Word, PowerPoint, Excel, CSV, Markdown, Text files"),
            ("🧠 Advanced RAG", "Contextual question answering with document retrieval"),
            ("🔍 Smart Analysis", "Table and image processing with OCR capabilities"),
            ("📈 Evaluation Framework", "DeepEval integration for quality assessment"),
            ("💬 Conversational Chat", "Interactive chat with your documents"),
            ("⚡ Real-time Processing", "Fast document ingestion and retrieval")
        ]
        
        for title, desc in features:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.header("🚀 Quick Start")
        
        if api_online:
            st.success("System Ready!")
            st.markdown("""
            **Steps to get started:**
            
            1. 📤 Go to **Document Upload & Chat**
            2. 📁 Upload your documents (PDF, DOCX, etc.)
            3. 🔄 Process documents to create index
            4. 💬 Start chatting with your documents!
            
            **Sample Questions:**
            - "What is this document about?"
            - "Summarize the key points"
            - "What are the main findings?"
            """)
            
            if health_data:
                st.subheader("System Info")
                st.json({
                    "Service": health_data.get("service", "Unknown"),
                    "Version": health_data.get("version", "Unknown"),
                    "Features": health_data.get("features", [])
                })
        else:
            st.error("⚠️ API server is not running. Please start the FastAPI server first.")
            st.markdown("""
            **To start the server:**
            ```bash
            ./run_local.sh
            ```
            """)

elif page == "Document Upload & Chat":
    st.header("Document Upload & Chat")
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Documents")
        
        # Quick demo option with modern styling
        demo_html = """
        <div class="demo-button" onclick="window.location.reload()">
            🚀 Try Demo with Sample Document
        </div>
        """
        
        if st.button("Try Demo with Sample Document", type="primary"):
            st.session_state.documents_processed = True
            st.session_state.current_session = "mlops_session_1756431984"
            st.success("✅ Demo mode activated! You can now chat with the sample MLOps document.")
            st.rerun()
        
        st.markdown("**OR**")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose documents",
            type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv', 'md'],
            help="Upload multiple documents in supported formats",
            accept_multiple_files=True
        )
        
        # Session configuration
        st.subheader("Configuration")
        session_id = st.text_input("Session ID (optional)", placeholder="Auto-generated if empty")
        
        col_chunk, col_overlap = st.columns(2)
        with col_chunk:
            chunk_size = st.number_input("Chunk Size", min_value=200, max_value=2000, value=1000, step=100)
        with col_overlap:
            chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=500, value=200, step=50)
        
        top_k = st.slider("Retrieval Top-K", min_value=1, max_value=20, value=5)
        
        # Process documents
        if uploaded_files and st.button("Process Documents & Build Index", type="primary"):
            if not api_online:
                st.error("API server is not available!")
            else:
                with st.spinner("Processing documents and building search index..."):
                    try:
                        # Prepare files for upload
                        files = []
                        for uploaded_file in uploaded_files:
                            files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)))
                        
                        # Prepare form data
                        form_data = {
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap,
                            "k": top_k,
                            "use_session_dirs": "true"
                        }
                        
                        if session_id:
                            form_data["session_id"] = session_id
                        
                        # Make API call
                        response = requests.post(
                            f"{FASTAPI_URL}/chat/index", 
                            files=files, 
                            data=form_data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Documents processed successfully!")
                            
                            # Store session info in session state
                            st.session_state.current_session = result.get("session_id")
                            st.session_state.documents_processed = True
                            
                            st.info(f"""
                            **Session ID:** {result.get('session_id')}  
                            **Files Processed:** {result.get('files_processed', 0)}  
                            **Chunks Created:** {result.get('chunks_created', 0)}
                            """)
                            
                        else:
                            st.error(f"Error processing documents: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
    
    with col2:
        st.subheader("💬 Chat with Documents")
        
        # Check if documents are processed
        if not hasattr(st.session_state, 'documents_processed'):
            st.session_state.documents_processed = False
        
        if not st.session_state.documents_processed:
            st.warning("📋 Please upload and process documents first to enable chat functionality.")
            st.info("👆 Use the upload section on the left to get started!")
        
        # Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history (only latest conversation unless history is requested)
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                show_full = st.session_state.get('show_full_history', False)
                
                if show_full:
                    # Show all conversations
                    st.subheader("📜 Full Chat History")
                    for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
                        st.markdown(f"**Conversation {i+1}:**")
                        
                        # User message
                        with st.container():
                            st.markdown("**🧑 You:**")
                            st.info(user_msg)
                        
                        # Bot response
                        with st.container():
                            st.markdown("**🤖 Assistant:**")
                            st.success(bot_msg)
                        
                        st.markdown("---")
                else:
                    # Show only the latest conversation
                    latest_conversation = st.session_state.chat_history[-1]
                    user_msg, bot_msg = latest_conversation
                    
                    # User message with Streamlit container
                    with st.container():
                        st.markdown("**🧑 You:**")
                        st.info(user_msg)
                    
                    # Bot response with Streamlit container  
                    with st.container():
                        st.markdown("**🤖 Assistant:**")
                        st.success(bot_msg)
                    
                    # Show conversation count if there are multiple
                    if len(st.session_state.chat_history) > 1:
                        st.caption(f"💬 Showing latest conversation (Total: {len(st.session_state.chat_history)} conversations)")
                
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; color: #666; background: #f9f9f9; border-radius: 15px; margin: 1rem 0;">
                    <h4>No conversation yet</h4>
                    <p>Upload documents and start asking questions to begin chatting!</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input("Ask a question about your documents:", key="chat_input")
        
        col_send, col_clear, col_history = st.columns([2, 1, 1])
        with col_send:
            send_button = st.button("Send", type="primary", use_container_width=True)
        with col_clear:
            clear_button = st.button("Clear", use_container_width=True)
        with col_history:
            if len(st.session_state.chat_history) > 1:
                if st.button("History", use_container_width=True):
                    st.session_state.show_full_history = not st.session_state.get('show_full_history', False)
                    st.rerun()
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        # Handle send button
        if send_button and user_question:
            
            if not api_online:
                st.error("API server is not available!")
            else:
                with st.spinner("Generating response..."):
                    try:
                        # Use the simple chat endpoint
                        chat_data = {
                            "message": user_question,
                            "session_id": st.session_state.get('current_session', 'default_session')
                        }
                        
                        response = requests.post(
                            f"{FASTAPI_URL}/chat",
                            json=chat_data,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            answer = result.get("response", "No response received")
                            
                            # Add to chat history
                            st.session_state.chat_history.append((user_question, answer))
                            st.rerun()
                            
                        else:
                            st.error(f"Error: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")

elif page == "Document Analysis":
    st.markdown("""
        <style>
        .tech-details {
            font-size: 0.8rem;
            color: #666;
        }
        .small-section {
            font-size: 0.9rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            font-size: 1.1rem;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Document Analysis")
    
    # Create tabs for different analysis views
    tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Details"])
    
    with tab1:
        st.subheader("Document Upload")
        
        # Add a clear session button
        col_upload, col_clear = st.columns([3, 1])
        with col_clear:
            if st.button("Clear Session", type="secondary", help="Clear previous analysis results"):
                # Clear all analysis-related session state
                keys_to_clear = ['analysis_result', 'analyzed_file', 'current_analysis_file', 'analysis_timestamp', 
                               'current_file_hash', 'analyzed_file_hash']
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                st.success("Session cleared!")
                st.rerun()
        
        with col_upload:
            # Single file upload for analysis
            analysis_file = st.file_uploader(
                "Choose a document for detailed analysis",
                type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv', 'md'],
                help="Upload a single document for comprehensive analysis",
                key="document_analysis_uploader"
            )
        
        if analysis_file is not None:
            st.success(f"File selected: {analysis_file.name}")
            
            # Generate file hash for tracking
            import hashlib
            file_content = analysis_file.getvalue()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Clear previous analysis results when new file is uploaded
            current_file_hash = st.session_state.get('current_file_hash', '')
            if current_file_hash != file_hash:
                # New file detected, clear old results
                keys_to_clear = ['analysis_result', 'analyzed_file', 'analysis_timestamp']
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                st.session_state['current_file_hash'] = file_hash
                st.session_state['current_analysis_file'] = analysis_file.name
                st.info("New file detected. Previous analysis results cleared.")
            
            # Display file details
            file_details = {
                "Filename": analysis_file.name,
                "File Size": f"{len(file_content):,} bytes",
                "File Type": analysis_file.type,
                "File Hash": file_hash[:8] + "..."
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.json(file_details)
            
            # Analyze button
            if st.button("Analyze Document", type="primary", key="analyze_btn"):
                if not api_online:
                    st.error("API server is not available!")
                else:
                    with st.spinner("Analyzing document..."):
                        try:
                            # Generate unique request ID for debugging
                            import uuid
                            request_id = str(uuid.uuid4())[:8]
                            
                            files = {"file": (analysis_file.name, file_content, analysis_file.type)}
                            
                            # Add debug headers
                            headers = {
                                "X-Request-ID": request_id,
                                "X-File-Hash": file_hash[:8]
                            }
                            
                            response = requests.post(
                                f"{FASTAPI_URL}/analyze-document", 
                                files=files,
                                headers=headers
                            )
                            
                            if response.status_code == 200:
                                st.success("Document analyzed successfully!")
                                result = response.json()
                                
                                # Add request tracking to result
                                result['request_id'] = request_id
                                result['client_file_hash'] = file_hash
                                
                                # Store results in session state with file reference and hash
                                st.session_state['analysis_result'] = result
                                st.session_state['analyzed_file'] = analysis_file.name
                                st.session_state['analyzed_file_hash'] = file_hash
                                st.session_state['analysis_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                st.session_state['request_id'] = request_id
                                
                                st.info(f"Analysis completed with Request ID: {request_id}")
                                st.rerun()
                            else:
                                st.error(f"Analysis failed: {response.text}")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
    
    with tab2:
        if 'analysis_result' in st.session_state and 'analyzed_file' in st.session_state:
            result = st.session_state['analysis_result']
            filename = st.session_state['analyzed_file']
            file_hash = st.session_state.get('analyzed_file_hash', 'unknown')
            current_hash = st.session_state.get('current_file_hash', 'unknown')
            timestamp = st.session_state.get('analysis_timestamp', 'Unknown')
            request_id = st.session_state.get('request_id', 'Unknown')
            
            # Debug information at the top
            with st.expander("🔍 Debug Information", expanded=False):
                st.write(f"**Request ID:** {request_id}")
                st.write(f"**Analysis Timestamp:** {timestamp}")
                st.write(f"**Analyzed File:** {filename}")
                st.write(f"**Analysis Hash:** {file_hash[:16] if file_hash != 'unknown' else file_hash}")
                st.write(f"**Current Hash:** {current_hash[:16] if current_hash != 'unknown' else current_hash}")
                
                # Show first few lines of analysis content for verification
                if 'summary' in result:
                    st.write("**Analysis Content Preview:**")
                    summary_preview = result['summary'][:200] + "..." if len(result['summary']) > 200 else result['summary']
                    st.code(summary_preview)
            
            # Verify the results match the current file
            if file_hash != current_hash:
                st.error("⚠️ ANALYSIS MISMATCH DETECTED!")
                st.warning("The displayed analysis results are for a different file. Please re-analyze the current document.")
                st.info(f"**Current file hash:** {current_hash[:16]}...")
                st.info(f"**Analysis file hash:** {file_hash[:16]}...")
                st.stop()
            else:
                st.success("✅ Analysis results match current file")
                st.subheader(f"Analysis Results")
                st.markdown(f"**File:** {filename}")
                st.markdown(f"**Analyzed:** {timestamp}")
                st.markdown(f"**File Hash:** {file_hash[:8]}...")
                st.markdown(f"**Request ID:** {request_id}")
                
                # Key metrics in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Processor Used", result.get("processor", "Unknown"))
                with col2:
                    st.metric("File Size", f"{result.get('file_size', 0):,} bytes")
                with col3:
                    if "documents_processed" in result:
                        st.metric("Documents Processed", result.get("documents_processed", 0))
                
                # Content preview
                if "content_preview" in result:
                    st.subheader("Content Preview")
                    preview_text = result["content_preview"]
                    if len(preview_text) > 500:
                        preview_text = preview_text[:500] + "..."
                    st.text_area("Document Content (first 500 characters)", 
                               preview_text,
                               height=200, disabled=True)
                elif "preview" in result:
                    st.subheader("Content Preview")
                    st.text_area("Document Preview", result["preview"], height=200, disabled=True)
        else:
            st.info("No analysis results available. Please analyze a document first.")
    
    with tab3:
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            filename = st.session_state.get('analyzed_file', 'Unknown')
            
            st.markdown('<div class="small-section">', unsafe_allow_html=True)
            st.subheader("Technical Details")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"**Analyzed File:** {filename}")
            
            # Display detailed technical information
            if "total_content_length" in result:
                st.markdown(f'<div class="tech-details">Content Length: {result.get("total_content_length", 0):,} characters</div>', unsafe_allow_html=True)
            
            if "processing_time" in result:
                st.markdown(f'<div class="tech-details">Processing Time: {result.get("processing_time", 0):.2f} seconds</div>', unsafe_allow_html=True)
            
            if "metadata" in result:
                st.markdown('<div class="small-section">', unsafe_allow_html=True)
                st.subheader("Document Metadata")
                st.markdown('</div>', unsafe_allow_html=True)
                st.json(result["metadata"])
            
            # Full analysis result
            st.markdown('<div class="tech-details">', unsafe_allow_html=True)
            st.subheader("Full Analysis Result")
            st.json(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No analysis results available. Please analyze a document first.")

elif page == "Document Comparison":
    st.markdown("""
        <style>
        .tech-details {
            font-size: 0.8rem;
            color: #666;
        }
        .small-section {
            font-size: 0.9rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            font-size: 1.1rem;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Document Comparison")
    
    # Create tabs for different comparison views
    tab1, tab2, tab3 = st.tabs(["Upload", "Compare", "Results"])
    
    with tab1:
        st.subheader("Upload Documents for Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Document 1**")
            doc1 = st.file_uploader(
                "Choose first document",
                type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv', 'md'],
                help="Upload the first document for comparison",
                key="doc1_uploader"
            )
            
        with col2:
            st.markdown("**Document 2**")
            doc2 = st.file_uploader(
                "Choose second document",
                type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv', 'md'],
                help="Upload the second document for comparison",
                key="doc2_uploader"
            )
        
        if doc1 and doc2:
            st.success("Both documents uploaded successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Document 1 Details**")
                doc1_details = {
                    "Filename": doc1.name,
                    "File Size": f"{len(doc1.getvalue()):,} bytes",
                    "File Type": doc1.type
                }
                st.json(doc1_details)
                
            with col2:
                st.markdown("**Document 2 Details**")
                doc2_details = {
                    "Filename": doc2.name,
                    "File Size": f"{len(doc2.getvalue()):,} bytes",
                    "File Type": doc2.type
                }
                st.json(doc2_details)
    
    with tab2:
        if 'doc1' in locals() and 'doc2' in locals() and doc1 and doc2:
            st.subheader("Document Comparison Options")
            
            comparison_type = st.selectbox(
                "Select comparison type:",
                ["Content Similarity", "Structural Analysis", "Key Differences"]
            )
            
            if st.button("Compare Documents", type="primary"):
                if not api_online:
                    st.error("API server is not available!")
                else:
                    with st.spinner("Comparing documents..."):
                        try:
                            # Create files for API endpoint
                            files = [
                                ("reference", (doc1.name, doc1.getvalue(), doc1.type)),
                                ("actual", (doc2.name, doc2.getvalue(), doc2.type))
                            ]
                            
                            # Call comparison API
                            response = requests.post(f"{FASTAPI_URL}/compare", files=files, timeout=30)
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.session_state['comparison_result'] = {
                                    "doc1_name": doc1.name,
                                    "doc2_name": doc2.name,
                                    "comparison_type": comparison_type,
                                    "similarity_score": result.get("similarity_score", 0.0),
                                    "differences": result.get("differences", []),
                                    "common_elements": result.get("common_elements", []),
                                    "analysis": result.get("analysis", ""),
                                    "word_counts": result.get("word_counts", {}),
                                    "content_overlap": result.get("content_overlap", 0.0)
                                }
                                st.success("Documents compared successfully!")
                                st.rerun()
                            else:
                                st.error(f"Comparison failed: {response.text}")
                        except Exception as e:
                            st.error(f"Error during comparison: {str(e)}")
                            # Fallback to placeholder for now
                            st.session_state['comparison_result'] = {
                                "doc1_name": doc1.name,
                                "doc2_name": doc2.name,
                                "comparison_type": comparison_type,
                                "similarity_score": 0.0,
                                "differences": ["Comparison service unavailable"],
                                "common_elements": ["Unable to analyze"],
                                "analysis": "Error occurred during comparison",
                                "word_counts": {},
                                "content_overlap": 0.0
                            }
        else:
            st.info("Please upload both documents first.")
    
    with tab3:
        if 'comparison_result' in st.session_state:
            result = st.session_state['comparison_result']
            
            st.markdown('<div class="small-section">', unsafe_allow_html=True)
            st.subheader(f"Comparison Results")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"**Documents:** {result['doc1_name']} vs {result['doc2_name']}")
            st.markdown(f"**Comparison Type:** {result['comparison_type']}")
            
            # Similarity score
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Similarity Score", f"{result['similarity_score']:.2%}")
            
            # Differences and similarities
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="small-section">', unsafe_allow_html=True)
                st.subheader("Key Differences")
                st.markdown('</div>', unsafe_allow_html=True)
                for diff in result.get('differences', []):
                    st.markdown(f"• {diff}")
            
            with col2:
                st.markdown('<div class="small-section">', unsafe_allow_html=True)
                st.subheader("Common Elements")
                st.markdown('</div>', unsafe_allow_html=True)
                for common in result.get('common_elements', []):
                    st.markdown(f"• {common}")
            
            # Technical details
            st.markdown('<div class="tech-details">', unsafe_allow_html=True)
            st.subheader("Full Comparison Result")
            st.json(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No comparison results available. Please compare documents first.")

elif page == "System Dashboard":
    st.header("System Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 System Health")
        
        if api_online and health_data:
            st.success("✅ All systems operational")
            
            # System metrics
            st.metric("Service Status", "Online")
            st.metric("Version", health_data.get("version", "Unknown"))
            
            # Features
            st.subheader("🎯 Available Features")
            features = health_data.get("features", [])
            for feature in features:
                st.write(f"✅ {feature.replace('-', ' ').title()}")
                
        else:
            st.error("❌ System offline")
    
    with col2:
        st.subheader("🔧 System Information")
        
        try:
            response = requests.get(f"{FASTAPI_URL}/system/info", timeout=5)
            if response.status_code == 200:
                system_info = response.json()
                st.json(system_info)
            else:
                st.error("Could not retrieve system information")
        except:
            st.error("System info endpoint not available")
    
    # API Endpoints
    st.subheader("🔌 Available API Endpoints")
    endpoints = [
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "API documentation"),
        ("POST", "/analyze-document", "Document analysis"),
        ("POST", "/chat", "Chat interface"),
        ("POST", "/chat/index", "Build document index"),
        ("POST", "/chat/query", "Query documents"),
        ("GET", "/evaluation/run", "Run evaluation tests"),
        ("GET", "/system/info", "System information")
    ]
    
    for method, endpoint, description in endpoints:
        st.write(f"**{method}** `{endpoint}` - {description}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🚀 Document RAG Portal**")
with col2:
    st.markdown("Enhanced with multi-format support")
with col3:
    st.markdown(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh for API status
if not api_online:
    time.sleep(2)
    st.rerun()
