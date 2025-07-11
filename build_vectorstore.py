#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Store Builder for Monster Notebook RAG System
This script creates and saves a FAISS vectorstore from JSON documents
"""

import os
import json
import pickle
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

class VectorStoreBuilder:
    def __init__(self):
        """Initialize the vector store builder"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found!")
        
        self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.documents = []
        self.vectorstore = None
    
    def load_json_documents(self, json_dir: str = "documents/json") -> List[Document]:
        """Load all JSON documents from the specified directory"""
        documents = []
        
        if not os.path.exists(json_dir):
            raise FileNotFoundError(f"Documents directory not found: {json_dir}")
        
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        print(f"📁 Found {len(json_files)} JSON files")
        
        for file_name in json_files:
            file_path = os.path.join(json_dir, file_name)
            print(f"📄 Processing: {file_name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process the JSON structure
                if 'collection' in data:
                    # Format like Monster Model List.json
                    for idx, item in enumerate(data['collection']):
                        title = item.get('document', '')
                        content = item.get('content', '')
                        
                        formatted_content = f"Başlık: {title}\n\n"
                        formatted_content += f"Kategori: {self._get_category_from_filename(file_name)}\n\n"
                        formatted_content += f"İçerik: {content}\n\n"
                        formatted_content += f"Kaynak: {file_name}"
                        
                        doc = Document(
                            page_content=formatted_content,
                            metadata={
                                'source': file_name,
                                'title': title,
                                'category': self._get_category_from_filename(file_name),
                                'doc_id': f"{file_name}_{idx}",
                                'content_length': len(content)
                            }
                        )
                        documents.append(doc)
                        
                elif isinstance(data, list):
                    # Format like other JSON files (Q&A format)
                    for idx, item in enumerate(data):
                        question = item.get('soru', '')
                        answer = item.get('cevap', '')
                        
                        title = f"Soru {idx + 1}"
                        content = f"Soru: {question}\n\nCevap: {answer}"
                        
                        formatted_content = f"Başlık: {title}\n\n"
                        formatted_content += f"Kategori: {self._get_category_from_filename(file_name)}\n\n"
                        formatted_content += f"İçerik:\n{content}\n\n"
                        formatted_content += f"Kaynak: {file_name}"
                        
                        doc = Document(
                            page_content=formatted_content,
                            metadata={
                                'source': file_name,
                                'title': title,
                                'category': self._get_category_from_filename(file_name),
                                'doc_id': f"{file_name}_{idx}",
                                'question': question,
                                'answer': answer,
                                'content_length': len(content)
                            }
                        )
                        documents.append(doc)
                        
                    print(f"  ✅ Loaded {len(data)} Q&A pairs")
                else:
                    print(f"  ⚠️ Unexpected JSON structure in {file_name}")
                
            except Exception as e:
                print(f"  ❌ Error loading {file_name}: {str(e)}")
                continue
        
        print(f"\n✅ Total loaded: {len(documents)} documents from {len(json_files)} files")
        self.documents = documents
        return documents
    
    def _get_category_from_filename(self, filename: str) -> str:
        """Extract category from filename with enhanced mapping"""
        category_map = {
            'baglant_ag_sorunlar': 'Bağlantı ve Ağ Sorunları',
            'donanim_ekran_panel': 'Donanım - Ekran ve Panel Sorunları',
            'donanim_guc_batarya': 'Donanım - Güç ve Batarya Sorunları',
            'donanim_klavye_touchpad': 'Donanım - Klavye ve Touchpad Sorunları',
            'donanim_mentese_kasa': 'Donanım - Menteşe ve Kasa Sorunları',
            'donanim_usb_portlar': 'Donanım - USB Port Sorunları',
            'genel_bilgilendirmeler_diger': 'Genel Bilgilendirmeler ve Diğer Konular',
            'kurulum_ve_yazlm_sorunlar': 'Kurulum ve Yazılım Sorunları',
            'performans_sorunlar': 'Performans ve Hız Sorunları',
            'ses_hoparlor_problemleri': 'Ses ve Hoparlör Sorunları',
            'Monster Model List': 'Monster Notebook Model Listesi',
            'Technical Service Information': 'Teknik Servis Bilgi ve Prosedürleri',
            'Technical Service Office': 'Teknik Servis Ofis Lokasyonları'
        }
        
        for key, value in category_map.items():
            if key in filename:
                return value
        return 'Kategorize Edilmemiş'
    
    def create_chunks(self, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        """Keep documents whole without chunking for Q&A pairs"""
        if not self.documents:
            raise ValueError("No documents loaded! Call load_json_documents() first.")
        
        print(f"� Keeping documents whole (no chunking) to preserve complete Q&A pairs")
        
        # Add chunk information to metadata (even though we're not chunking)
        for i, doc in enumerate(self.documents):
            doc.metadata['chunk_id'] = i
            doc.metadata['chunk_size'] = len(doc.page_content)
            doc.metadata['is_complete'] = True  # Mark as complete document
        
        print(f"✅ Keeping {len(self.documents)} documents whole (no splits)")
        return self.documents
    
    def build_vectorstore(self, split_docs: List[Document]) -> FAISS:
        """Build FAISS vectorstore from document chunks"""
        print("🔄 Building FAISS vectorstore with OpenAI embeddings...")
        print("⏳ This may take a few minutes depending on document count...")
        
        try:
            # Create vectorstore in batches to avoid rate limits
            batch_size = 50
            vectorstores = []
            
            for i in range(0, len(split_docs), batch_size):
                batch = split_docs[i:i + batch_size]
                print(f"  📦 Processing batch {i//batch_size + 1}/{(len(split_docs) + batch_size - 1)//batch_size} ({len(batch)} docs)")
                
                if i == 0:
                    # Create first vectorstore
                    vectorstore = FAISS.from_documents(
                        documents=batch,
                        embedding=self.embeddings
                    )
                    vectorstores.append(vectorstore)
                else:
                    # Create additional vectorstore and merge
                    batch_vs = FAISS.from_documents(
                        documents=batch,
                        embedding=self.embeddings
                    )
                    vectorstores[0].merge_from(batch_vs)
            
            self.vectorstore = vectorstores[0]
            print("✅ FAISS vectorstore created successfully!")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error building vectorstore: {str(e)}")
            raise
    
    def save_vectorstore(self, save_path: str = "vectorstore"):
        """Save the vectorstore to disk"""
        if not self.vectorstore:
            raise ValueError("No vectorstore to save! Call build_vectorstore() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Save FAISS index
        faiss_path = os.path.join(save_path, "faiss_index")
        self.vectorstore.save_local(faiss_path)
        
        # Save metadata
        metadata = {
            'document_count': len(self.documents),
            'chunk_count': self.vectorstore.index.ntotal,
            'embedding_model': 'text-embedding-ada-002',
            'created_by': 'VectorStoreBuilder',
        }
        
        metadata_path = os.path.join(save_path, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Vectorstore saved to: {save_path}")
        print(f"📊 Documents: {metadata['document_count']}")
        print(f"📊 Chunks: {metadata['chunk_count']}")
    
    def load_vectorstore(self, load_path: str = "vectorstore") -> FAISS:
        """Load vectorstore from disk"""
        faiss_path = os.path.join(load_path, "faiss_index")
        
        if not os.path.exists(faiss_path):
            raise FileNotFoundError(f"Vectorstore not found at: {faiss_path}")
        
        print(f"📂 Loading vectorstore from: {load_path}")
        self.vectorstore = FAISS.load_local(
            faiss_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load metadata if available
        metadata_path = os.path.join(load_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"📊 Loaded vectorstore with {metadata.get('chunk_count', 'unknown')} chunks")
        
        print("✅ Vectorstore loaded successfully!")
        return self.vectorstore
    
    def test_search(self, query: str, k: int = 3):
        """Test search functionality"""
        if not self.vectorstore:
            raise ValueError("No vectorstore loaded!")
        
        print(f"🔍 Testing search: '{query}'")
        results = self.vectorstore.similarity_search(query, k=k)
        
        for i, doc in enumerate(results, 1):
            print(f"\n📄 Result {i}:")
            print(f"   Category: {doc.metadata.get('category', 'Unknown')}")
            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   Content: {doc.page_content[:200]}...")

def main():
    """Main function to build vectorstore"""
    print("🚀 Monster Notebook Vectorstore Builder")
    print("=" * 50)
    
    try:
        # Initialize builder
        builder = VectorStoreBuilder()
        
        # Load documents
        print("\n1️⃣ Loading JSON documents...")
        documents = builder.load_json_documents()
        
        # Create chunks
        print("\n2️⃣ Creating document chunks...")
        chunks = builder.create_chunks()
        
        # Build vectorstore
        print("\n3️⃣ Building vectorstore...")
        vectorstore = builder.build_vectorstore(chunks)
        
        # Save vectorstore
        print("\n4️⃣ Saving vectorstore...")
        builder.save_vectorstore()
        
        # Test search
        print("\n5️⃣ Testing search functionality...")
        builder.test_search("Tulpar model")
        builder.test_search("ekran sorunu")
        builder.test_search("teknik servis")
        
        print("\n✅ Vectorstore successfully created and saved!")
        print("💡 You can now use this vectorstore in your RAG chatbot.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
