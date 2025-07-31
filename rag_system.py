# rag_system.py

import logging
import fitz
import docx
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List
from config import Config
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

embedding_model = None
chroma_client = None
collection = None
openai_client = None

FALLBACK_RESPONSE = "I'm not sure how to answer that. Can you please rephrase your question?"

def initialize_rag_system():
    global embedding_model, chroma_client, collection, openai_client
    
    if embedding_model:
        return

    logger.info("Initializing Sentence Transformer model (all-MiniLM-L6-v2)...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    script_dir = os.path.dirname(__file__)
    db_path = os.path.abspath(os.path.join(script_dir, "chroma_db"))
    
    logger.info(f"Initializing ChromaDB persistent client at: {db_path}")
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(
        name="zoom_meeting_docs",
        metadata={"hnsw:space": "cosine"}
    )
    
    logger.info("Initializing OpenAI client...")
    openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    logger.info("✅ RAG System Initialized.")

class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str, filename: str) -> str:
        if filename.lower().endswith('.pdf'):
            with fitz.open(file_path) as doc:
                return "".join(page.get_text() for page in doc)
        elif filename.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 250, overlap: int = 50) -> List[str]:
        words = text.split()
        if not words: return []
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(' '.join(words[i:i + chunk_size]))
        return chunks

class RAGSystem:

    def add_document_chunk(self, document_text: str, source_id: str, metadata: dict):
        try:
            embedding = embedding_model.encode([document_text], show_progress_bar=False)
            chunk_id = f"{source_id}_{hash(document_text)}"
            collection.add(
                embeddings=embedding.tolist(),
                documents=[document_text],
                ids=[chunk_id],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            logger.error(f"Error adding single chunk from '{source_id}': {e}")
            return False

    def add_document(self, source_id: str, file_path: str, filename: str):
        try:
            text = DocumentProcessor.extract_text(file_path, filename)
            if not text.strip():
                return False
            chunks = DocumentProcessor.chunk_text(text)
            embeddings = embedding_model.encode(chunks, show_progress_bar=False)
            chunk_ids = [f"{source_id}_{filename}_{i}" for i in range(len(chunks))]
            collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                ids=chunk_ids,
                metadatas=[{"source_document": filename, "type": "generic"} for _ in chunks]
            )
            return True
        except Exception as e:
            logger.error(f"Error adding document '{filename}': {e}")
            return False

    def generate_response(self, question: str) -> str:
        logger.info(f"Unified search for question: '{question}'")
        try:
            query_embedding = embedding_model.encode([question], show_progress_bar=False)
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=5,
                include=["documents"]
            )
            context_docs = results.get('documents', [[]])[0]

            if not context_docs:
                logger.warning(f"Vector search returned no documents for: '{question}'. Using fallback.")
                return FALLBACK_RESPONSE

            context_str = "\n\n---\n\n".join(context_docs)
            
            system_prompt = (
                "You are an expert AI assistant for 'The Fitness Doctor'. Your persona is friendly, professional, and helpful. "
                "Your task is to answer the user's question based on the provided CONTEXT. "
                "Follow these rules precisely:\n"
                "1.  **Synthesize, Don't Just Copy:** Read the entire CONTEXT. For factual questions (e.g., 'what is...', 'how do I...'), create a natural, conversational answer by combining information from the context. Do not just copy-paste sentences.\n"
                "2.  **Handle Conversational Rules Gracefully:** The CONTEXT may contain rules (e.g., for 'who are you' or 'how are you'). Use the bot's response from the rule as your primary guidance, but rephrase it to sound like a genuine conversation, not a script.\n"
                "3.  **Be Honest About Your Limits:** The context is your entire world. If the information needed to answer the question is not in the CONTEXT, you MUST state that you don't have that specific information and suggest the user schedule a consultation for more details. NEVER make up prices, schedules, or medical advice.\n"
                "4.  **Stay Concise:** Keep your answers clear and to the point (2-4 sentences is ideal)."
            )

            user_prompt = f"CONTEXT:\n{context_str}\n\nUSER QUESTION: {question}\n\nAnswer:"

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=250,
                temperature=0.4
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"LLM generated answer: '{answer}'")
            return answer

        except Exception as e:
            logger.error(f"Error in generate_response: {e}", exc_info=True)
            return "I seem to be having a technical issue. Please try asking again in a moment."

def is_a_meaningful_message(message: str) -> bool:
    """A simpler, more effective filter."""
    # Filters out single-character messages or just "ok", "hi", etc.
    # but allows short commands like "stop".
    return len(message.strip()) > 2 or message.strip().lower() == 'stop'