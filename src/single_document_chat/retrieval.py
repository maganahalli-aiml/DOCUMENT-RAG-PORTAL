import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

# Try to import streamlit, but don't fail if it's not available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
    
    # Suppress Streamlit warnings when running outside of Streamlit context
    import warnings
    import logging
    import sys
    
    # Disable specific Streamlit warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
    
    # Also disable specific loggers that cause the warnings
    streamlit_logger = logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context")
    streamlit_logger.setLevel(logging.ERROR)
    
    session_state_logger = logging.getLogger("streamlit.runtime.state.session_state_proxy")
    session_state_logger.setLevel(logging.ERROR)
    
    # Additional safety: suppress thread-related warnings that might cause sys.excepthook errors
    import threading
    
    # Override threading excepthook if available (Python 3.8+)
    if hasattr(threading, 'excepthook'):
        def safe_thread_excepthook(args):
            # Silently handle thread exceptions to prevent sys.excepthook errors
            pass
        threading.excepthook = safe_thread_excepthook
    
except ImportError:
    STREAMLIT_AVAILABLE = False

load_dotenv()

class ConversationalRAG:
    def __init__(self, session_id: str, retriever):
        self.log = CustomLogger().get_logger(__name__)
        self.session_id = session_id
        self.retriever = retriever
        
        # Initialize session store for non-Streamlit contexts
        if not STREAMLIT_AVAILABLE:
            self._session_store = {}

        try:
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.log.info("Created history-aware retriever", session_id=session_id)

            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
            self.log.info("Created RAG chain", session_id=session_id)

            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            self.log.info("Wrapped chain with message history", session_id=session_id)

        except Exception as e:
            self.log.error("Error initializing ConversationalRAG", error=str(e), session_id=session_id)
            raise DocumentPortalException("Failed to initialize ConversationalRAG", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info("LLM loaded successfully", class_name=llm.__class__.__name__)
            return llm
        except Exception as e:
            self.log.error("Error loading LLM via ModelLoader", error=str(e))
            raise DocumentPortalException("Failed to load LLM", sys)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        try:
            if STREAMLIT_AVAILABLE:
                # Use Streamlit session state if available (warnings are suppressed globally)
                if "store" not in st.session_state:
                    st.session_state.store = {}

                if session_id not in st.session_state.store:
                    st.session_state.store[session_id] = ChatMessageHistory()
                    self.log.info("New chat session history created (Streamlit)", session_id=session_id)

                return st.session_state.store[session_id]
            else:
                # Use local session store for non-Streamlit contexts
                if session_id not in self._session_store:
                    self._session_store[session_id] = ChatMessageHistory()
                    self.log.info("New chat session history created (local)", session_id=session_id)

                return self._session_store[session_id]
                
        except Exception as e:
            self.log.error("Failed to access session history", session_id=session_id, error=str(e))
            raise DocumentPortalException("Failed to retrieve session history", sys)

    def load_retriever_from_faiss(self, index_path: str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")

            vectorstore = FAISS.load_local(index_path, embeddings)
            self.log.info("Loaded retriever from FAISS index", index_path=index_path)
            return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

        except Exception as e:
            self.log.error("Failed to load retriever from FAISS", error=str(e))
            raise DocumentPortalException("Error loading retriever from FAISS", sys)
        
    def invoke(self, user_input: str) -> str:
        try:
            response = self.chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}}
            )
            answer = response.get("answer", "No answer.")

            if not answer:
                self.log.warning("Empty answer received", session_id=self.session_id)

            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
            return answer

        except Exception as e:
            self.log.error("Failed to invoke conversational RAG", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to invoke RAG chain", sys)
    
    def cleanup(self):
        """Clean up resources to prevent threading issues"""
        try:
            # Clear session store if using local storage
            if not STREAMLIT_AVAILABLE and hasattr(self, '_session_store'):
                self._session_store.clear()
                
            # Clear any references to heavy objects
            if hasattr(self, 'chain'):
                self.chain = None
            if hasattr(self, 'rag_chain'):
                self.rag_chain = None
            if hasattr(self, 'qa_chain'):
                self.qa_chain = None
            if hasattr(self, 'history_aware_retriever'):
                self.history_aware_retriever = None
                
            self.log.info("ConversationalRAG cleanup completed", session_id=self.session_id)
        except Exception as e:
            # Silently handle cleanup errors to prevent sys.excepthook issues
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False