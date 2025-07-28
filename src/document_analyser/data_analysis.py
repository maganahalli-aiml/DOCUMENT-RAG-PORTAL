import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import Metadata
from prompt.prompt_library import prompt
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import *

class DocumentAnalyzer:
    """
    Analyzes documents using a pre-trained model.
    Automatically logs all actions and supports session-based organization.
    """
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader=ModelLoader()
            self.llm=self.loader.load_llm()
            
            # Prepare parsers
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            
            self.prompt = prompt
            
            self.log.info("DocumentAnalyzer initialized successfully")
            
            
        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Error in DocumentAnalyzer initialization", sys)
        
        
    def _chunk_text(self, text: str, max_chars: int = 15000) -> str:
        """
        Chunk text to fit within model limits. Takes first chunk and last chunk for context.
        """
        if len(text) <= max_chars:
            return text
        
        # Take first half and last half to maintain context
        chunk_size = max_chars // 2
        first_chunk = text[:chunk_size]
        last_chunk = text[-chunk_size:]
        
        return f"{first_chunk}\n\n... [DOCUMENT CONTINUES] ...\n\n{last_chunk}"
    
    def analyze_document(self, document_text:str)-> dict:
        """
        Analyze a document's text and extract structured metadata & summary.
        """
        try:
            # Chunk the document if it's too large
            chunked_text = self._chunk_text(document_text)
            
            chain = self.prompt | self.llm | self.fixing_parser
            
            self.log.info("Meta-data analysis chain initialized")
            self.log.info(f"Document text length: {len(document_text)} chars, chunked to: {len(chunked_text)} chars")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": chunked_text
            })

            self.log.info("Metadata extraction successful", keys=list(response.keys()))
            
            return response

        except Exception as e:
            self.log.error("Metadata analysis failed", error=str(e))
            raise DocumentPortalException("Metadata extraction failed", sys) from e