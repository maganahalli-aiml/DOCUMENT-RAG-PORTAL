import sys
from pathlib import Path
from langchain_community.vectorstores import FAISS
from src.single_document_chat.data_ingestion import SingleDocIngestor
from src.single_document_chat.retrieval import ConversationalRAG
from utils.model_loader import ModelLoader

FAISS_INDEX_PATH = Path("faiss_index")

def test_conversational_rag_on_pdf(pdf_path:str, question:str):
    try:
        model_loader = ModelLoader()
        
        if FAISS_INDEX_PATH.exists():
            print("Loading existing FAISS index...")
            embeddings = model_loader.load_embeddings()
            try:
                # Try with allow_dangerous_deserialization parameter
                vectorstore = FAISS.load_local(
                    folder_path=str(FAISS_INDEX_PATH), 
                    embeddings=embeddings,
                    allow_dangerous_deserialization=True
                )
            except TypeError:
                # Fallback for older versions that don't have this parameter
                vectorstore = FAISS.load_local(
                    folder_path=str(FAISS_INDEX_PATH), 
                    embeddings=embeddings
                )
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        else:
            # Step 2: Ingest document and create retriever
            print("FAISS index not found. Ingesting PDF and creating index...")
            with open(pdf_path, "rb") as f:
                uploaded_files = [f]
                ingestor = SingleDocIngestor()
                retriever = ingestor.ingest_files(uploaded_files)
        print("Running Conversational RAG...")
        session_id = "test_conversational_rag"
        rag = ConversationalRAG(retriever=retriever, session_id=session_id)
        
        response = rag.invoke(question)
        print(f"\nQuestion: {question}\nAnswer: {response}")
                    
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
if __name__ == "__main__":
    # Example PDF path and question
    pdf_path = "data/single_document_chat/sample.pdf"
    question = "What is the main topic of the document?"

    if not Path(pdf_path).exists():
        print(f"PDF file does not exist at: {pdf_path}")
        sys.exit(1)
    
    # Run the test
    test_conversational_rag_on_pdf(pdf_path, question)
    test_conversational_rag_on_pdf(pdf_path, "Safety Categories and Annotation Guidelines")