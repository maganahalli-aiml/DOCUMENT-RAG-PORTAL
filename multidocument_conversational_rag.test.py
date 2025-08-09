import sys
from pathlib import Path
from langchain_community.vectorstores import FAISS
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConversationalRAG
from utils.model_loader import ModelLoader

FAISS_INDEX_PATH = Path("faiss_index")

def test_multi_conversational_rag():
    try:
        test_files = [
            "data/multi_document_chat/sample.pdf",
            "data/multi_document_chat/NIPS-2017-attention.pdf",
            "data/multi_document_chat/state_of_the_union.txt",
            "data/multi_document_chat/market_analysis_report.docx"
        ]
        
        uploaded_files = []
        
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
                print(f"Added file: {file_path}")
            else:
                print(f"File does not exist: {file_path}")
                
        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)
            
        print(f"Processing {len(uploaded_files)} files...")
        ingestor = DocumentIngestor()
        retriever = ingestor.ingest_files(uploaded_files)
        
        # Close files after processing
        for f in uploaded_files:
            f.close()
                
        session_id = "test_multi_doc_chat"
        
        # Use context manager for proper cleanup
        with ConversationalRAG(session_id=session_id, retriever=retriever) as rag:
            question = "what is attention is all you need paper about?"
            answer = rag.invoke(question)
            print(f"\nQuestion: {question}")
            print(f"Answer: {answer}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Run the test
    test_multi_conversational_rag()
    # test_conversational_rag_on_pdf(pdf_path, "Safety Categories and Annotation Guidelines")