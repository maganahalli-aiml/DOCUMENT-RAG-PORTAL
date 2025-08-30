import sys
import os
from operator import itemgetter
from typing import List, Optional
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
from src.cache.cache_manager import initialize_langchain_cache


class ConversationalRAG:
    def __init__(self,session_id:str, retriever=None, enable_cache: bool = True):
        try:
            self.log =  CustomLogger().get_logger(__name__)
            self.session_id = session_id
            
            # Initialize LangChain cache if enabled
            if enable_cache:
                try:
                    initialize_langchain_cache(cache_type="memory")
                    self.log.info("LangChain cache initialized for ConversationalRAG", session_id=self.session_id)
                except Exception as e:
                    self.log.warning(f"Failed to initialize cache, proceeding without: {str(e)}", session_id=self.session_id)
            
            self.llm =  self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            
            # Allow retriever to be None initially, but require it before building chain
            self.retriever = retriever
            
            # Only build chain if retriever is available
            if self.retriever is not None:
                self._build_lcel_chain()
                self.log.info("ConversationalRAG initialized with retriever", session_id=self.session_id)
            else:
                self.chain = None
                self.log.info("ConversationalRAG initialized without retriever", session_id=self.session_id)
            
        except Exception as e:
            self.log.error("Failed to initialize ConversationalRAG", error=str(e))
            raise DocumentPortalException("Initialization error in ConversationalRAG", sys)
            
    
    def load_retriever_from_faiss(self,index_path: str):
        """
        Load a FAISS vectorstore from disk and convert to retriever.
        """
        
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            # Try different FAISS loading approaches for compatibility
            try:
                # Try with allow_dangerous_deserialization parameter (newer versions)
                vectorstore = FAISS.load_local(
                    index_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                self.log.info("FAISS loaded with allow_dangerous_deserialization parameter", session_id=self.session_id)
            except TypeError as te:
                if "allow_dangerous_deserialization" in str(te):
                    # Fallback for older versions that don't support this parameter
                    self.log.info("Falling back to legacy FAISS loading method", session_id=self.session_id)
                    vectorstore = FAISS.load_local(index_path, embeddings)
                else:
                    raise te
            
            self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("FAISS retriever loaded successfully", index_path=index_path, session_id=self.session_id)
            
            # Build the chain now that we have a retriever
            self._build_lcel_chain()
            self.log.info("LCEL chain built after loading retriever", session_id=self.session_id)
        
            return self.retriever
        
        except Exception as e:
            self.log.error("Failed to load retriever from FAISS", error=str(e))
            raise DocumentPortalException("Loading error in ConversationalRAG", sys)

    def invoke(self,user_input:str,chat_history: Optional[List[BaseMessage]] = None) ->str:
        """
        Args:
            user_input (str): _description_
            chat_history (Optional[List[BaseMessage]], optional): _description_. Defaults to None.
        """
        try:
            # Ensure chain is built before invoking
            if self.chain is None:
                raise RuntimeError("Chain not built. Call load_retriever_from_faiss() first.")
                
            chat_history = chat_history or []
            payload={"input": user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning("No answer generated", user_input=user_input, session_id=self.session_id)
                return "no answer generated."
            
            self.log.info("Chain invoked successfully",
                session_id=self.session_id,
                user_input=user_input,
                answer_preview=answer[:150],
            )
            return answer
        except Exception as e:
            self.log.error("Failed to invoke ConversationalRAG", error=str(e))
            raise DocumentPortalException("Invocation error in ConversationalRAG", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            self.log.info("LLM loaded successfully", session_id=self.session_id)
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM", error=str(e))
            raise DocumentPortalException("LLM loading error in ConversationalRAG", sys)
    
    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)
    
    def _build_lcel_chain(self):
        try:
            # 1) Rewrite question using chat history
            question_rewriter = (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2) Retrieve docs for rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_docs

            # 3) Feed context + original input + chat history into answer prompt
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )

            self.log.info("LCEL graph built successfully", session_id=self.session_id)

        except Exception as e:
            self.log.error("Failed to build LCEL chain", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to build LCEL chain", sys)

    def cleanup(self):
        """Clean up resources to prevent threading issues"""
        try:
            # Clear any references to heavy objects
            if hasattr(self, 'chain'):
                self.chain = None
            if hasattr(self, 'retriever'):
                self.retriever = None
            if hasattr(self, 'llm'):
                self.llm = None
                
            self.log.info("ConversationalRAG cleanup completed", session_id=self.session_id)
        except Exception as e:
            # Silently handle cleanup errors to prevent sys.excepthook issues
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False