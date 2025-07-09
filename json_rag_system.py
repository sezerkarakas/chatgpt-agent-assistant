#!/usr/bin/env python3
"""
JSON-based RAG System for Monster Notebook Technical Support

This system creates a RAG (Retrieval-Augmented Generation) using JSON files
from the documents/json directory for cost-optimized technical support.
"""

import json
import os
import time
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Cost optimization settings
RAG_CONFIG = {
    "model": "gpt-4o-mini",
    "max_tokens": 1000,
    "temperature": 0.1,
    "top_k_documents": 8,  # Number of documents to retrieve
    "chunk_size": 1000,    # Size of text chunks
    "collection_name": "monster_support_json"
}

class JSONRAGSystem:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./json_chroma_db")
        self.collection = None
        self.system_prompt = self.load_system_prompt()
        self.encoding = tiktoken.encoding_for_model(RAG_CONFIG["model"])
        
    def load_system_prompt(self):
        """Load system prompt from file"""
        try:
            with open("gpt_prompt_v333.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """Sen Monster Notebook teknik destek uzmanısın. 
            Kullanıcıların teknik sorunlarına yardımcı ol ve aşağıdaki belgeleri kullanarak 
            detaylı ve yararlı yanıtlar ver."""
    
    def load_json_documents(self):
        """Load all JSON documents from documents/json directory"""
        json_dir = "documents/json"
        documents = []
        
        if not os.path.exists(json_dir):
            print(f"❌ {json_dir} dizini bulunamadı!")
            return documents
        
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        print(f"📁 {len(json_files)} JSON dosyası bulundu")
        
        for filename in json_files:
            filepath = os.path.join(json_dir, filename)
            print(f"📄 Yükleniyor: {filename}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        # Array of Q&A pairs
                        for i, item in enumerate(data):
                            if isinstance(item, dict) and 'soru' in item and 'cevap' in item:
                                doc_text = f"SORU: {item['soru']}\n\nCEVAP: {item['cevap']}"
                                documents.append({
                                    'id': f"{filename}_{i}",
                                    'text': doc_text,
                                    'source': filename,
                                    'type': 'qa_pair'
                                })
                    elif isinstance(data, dict):
                        # Single document or structured data
                        doc_text = json.dumps(data, ensure_ascii=False, indent=2)
                        documents.append({
                            'id': filename.replace('.json', ''),
                            'text': doc_text,
                            'source': filename,
                            'type': 'structured_data'
                        })
                    
            except Exception as e:
                print(f"❌ {filename} yüklenirken hata: {e}")
        
        print(f"✅ Toplam {len(documents)} belge yüklendi")
        return documents
    
    def create_chunks(self, documents):
        """Create text chunks from documents"""
        chunks = []
        
        for doc in documents:
            text = doc['text']
            
            # For Q&A pairs, keep them as single chunks (don't split)
            if doc['type'] == 'qa_pair':
                chunks.append({
                    'id': doc['id'],
                    'text': text,
                    'source': doc['source'],
                    'metadata': {
                        'type': doc['type'],
                        'source': doc['source']
                    }
                })
            else:
                # For structured data, split into smaller chunks if needed
                if len(text) <= RAG_CONFIG["chunk_size"]:
                    chunks.append({
                        'id': doc['id'],
                        'text': text,
                        'source': doc['source'],
                        'metadata': {
                            'type': doc['type'],
                            'source': doc['source']
                        }
                    })
                else:
                    # Split large documents into chunks
                    words = text.split()
                    current_chunk = []
                    chunk_id = 0
                    
                    for word in words:
                        current_chunk.append(word)
                        
                        if len(' '.join(current_chunk)) >= RAG_CONFIG["chunk_size"]:
                            chunk_text = ' '.join(current_chunk)
                            chunks.append({
                                'id': f"{doc['id']}_chunk_{chunk_id}",
                                'text': chunk_text,
                                'source': doc['source'],
                                'metadata': {
                                    'type': f"{doc['type']}_chunk",
                                    'source': doc['source'],
                                    'chunk_id': chunk_id
                                }
                            })
                            current_chunk = []
                            chunk_id += 1
                    
                    # Add remaining text as final chunk
                    if current_chunk:
                        chunk_text = ' '.join(current_chunk)
                        chunks.append({
                            'id': f"{doc['id']}_chunk_{chunk_id}",
                            'text': chunk_text,
                            'source': doc['source'],
                            'metadata': {
                                'type': f"{doc['type']}_chunk",
                                'source': doc['source'],
                                'chunk_id': chunk_id
                            }
                        })
        
        print(f"📦 {len(chunks)} chunk oluşturuldu")
        return chunks
    
    def setup_vector_store(self):
        """Setup ChromaDB vector store with JSON documents"""
        print("🔧 JSON tabanlı vektör deposu kuruluyor...")
        
        # Try to get existing collection or create new one
        try:
            self.collection = self.chroma_client.get_collection(RAG_CONFIG["collection_name"])
            print("✅ Mevcut koleksiyon bulundu")
            return True
        except:
            print("📁 Yeni koleksiyon oluşturuluyor...")
        
        # Load and process documents
        documents = self.load_json_documents()
        
        if not documents:
            print("❌ Belge bulunamadı!")
            return False
        
        # Create chunks
        chunks = self.create_chunks(documents)
        
        # Create new collection
        self.collection = self.chroma_client.create_collection(
            name=RAG_CONFIG["collection_name"],
            metadata={"description": "Monster Notebook JSON Support Documents"}
        )
        
        # Add documents to collection in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            batch_ids = [chunk['id'] for chunk in batch]
            batch_texts = [chunk['text'] for chunk in batch]
            batch_metadatas = [chunk['metadata'] for chunk in batch]
            
            self.collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            
            print(f"📥 Batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} eklendi")
        
        print("✅ Vektör deposu başarıyla kuruldu!")
        return True
    
    def retrieve_relevant_documents(self, query, top_k=None):
        """Retrieve relevant documents for a query"""
        if not self.collection:
            return []
        
        if top_k is None:
            top_k = RAG_CONFIG["top_k_documents"]
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    documents.append({
                        'text': doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return documents
        
        except Exception as e:
            print(f"❌ Belge arama hatası: {e}")
            return []
    
    def estimate_tokens(self, text):
        """Estimate token count for text"""
        return len(self.encoding.encode(text))
    
    def estimate_cost(self, prompt_tokens, completion_tokens):
        """Estimate cost based on token usage"""
        prompt_cost = prompt_tokens * 0.00000015  # $0.15 per 1M tokens
        completion_cost = completion_tokens * 0.0000006  # $0.60 per 1M tokens
        return prompt_cost + completion_cost
    
    def query(self, question):
        """Process a query using RAG"""
        start_time = time.time()
        
        # Retrieve relevant documents
        print(f"🔍 Soru: {question[:100]}...")
        relevant_docs = self.retrieve_relevant_documents(question)
        
        if not relevant_docs:
            return {
                "answer": "Üzgünüm, bu konuda yardımcı olabilecek belge bulunamadı.",
                "response_time": time.time() - start_time,
                "sources": [],
                "tokens": 0,
                "cost": 0,
                "success": False
            }
        
        # Build context from relevant documents
        context_parts = []
        sources = []
        
        for doc in relevant_docs:
            context_parts.append(doc['text'])
            source = doc['metadata'].get('source', 'unknown')
            if source not in sources:
                sources.append(source)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Create messages for chat completion
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Aşağıdaki belgeleri kullanarak soruya detaylı ve yararlı bir yanıt ver:

BELGELER:
{context}

SORU: {question}

Lütfen yanıtında kullandığın belge kaynaklarını belirt."""}
        ]
        
        try:
            # Get response from OpenAI
            response = client.chat.completions.create(
                model=RAG_CONFIG["model"],
                messages=messages,
                temperature=RAG_CONFIG["temperature"],
                max_tokens=RAG_CONFIG["max_tokens"]
            )
            
            answer = response.choices[0].message.content
            
            # Calculate metrics
            response_time = time.time() - start_time
            prompt_tokens = self.estimate_tokens(str(messages))
            completion_tokens = self.estimate_tokens(answer)
            cost = self.estimate_cost(prompt_tokens, completion_tokens)
            
            return {
                "answer": answer,
                "response_time": response_time,
                "sources": sources,
                "documents_used": len(relevant_docs),
                "tokens": prompt_tokens + completion_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost": cost,
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": f"Hata oluştu: {str(e)}",
                "response_time": time.time() - start_time,
                "sources": [],
                "tokens": 0,
                "cost": 0,
                "success": False
            }

def main():
    """Main function to test the JSON RAG system"""
    print("🚀 Monster Notebook JSON RAG Sistemi")
    print("=" * 50)
    
    # Initialize system
    rag = JSONRAGSystem()
    
    # Setup vector store
    if not rag.setup_vector_store():
        print("❌ Sistem kurulamadı!")
        return
    
    # Test with a sample question
    test_question = "Bilgisayarım yavaş açılıyor, ne yapabilirim?"
    print(f"\n🧪 Test sorusu: {test_question}")
    
    result = rag.query(test_question)
    
    print(f"\n✅ Yanıt ({result['response_time']:.1f}s):")
    print(result['answer'])
    print(f"\n📊 Kullanılan belgeler: {result['documents_used']}")
    print(f"📚 Kaynaklar: {', '.join(result['sources'])}")
    print(f"💰 Maliyet: ${result['cost']:.6f}")
    print(f"🔤 Token: {result['tokens']}")

if __name__ == "__main__":
    main()
