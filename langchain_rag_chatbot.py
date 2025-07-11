#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monster Notebook Teknik Destek Chatbot
LangChain + OpenAI + FAISS RAG Implementation
"""

import os
import json
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain

# Load environment variables
load_dotenv()

class MonsterRAGChatbot:
    def __init__(self):
        """Initialize the RAG chatbot with LangChain components"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found!")
        
        # Initialize components
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.1,
            api_key=self.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 interactions
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Load and process documents
        self._load_vectorstore()
        self._setup_qa_chain()
    
    def _load_vectorstore(self, vectorstore_path: str = "vectorstore"):
        """Load pre-built vectorstore from disk"""
        faiss_path = os.path.join(vectorstore_path, "faiss_index")
        
        if not os.path.exists(faiss_path):
            raise FileNotFoundError(f"Vectorstore not found at: {faiss_path}")
        
        print(f"📂 Loading vectorstore from: {vectorstore_path}")
        self.vectorstore = FAISS.load_local(
            faiss_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load metadata if available
        metadata_path = os.path.join(vectorstore_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"📊 Loaded vectorstore with {metadata.get('chunk_count', 'unknown')} chunks from {metadata.get('document_count', 'unknown')} documents")
        
        print("✅ Vectorstore loaded successfully!")
        return self.vectorstore
    
    def _get_category_from_filename(self, filename: str) -> str:
        """Extract category from filename"""
        category_map = {
            'baglant_ag_sorunlar': 'Bağlantı ve Ağ Sorunları',
            'donanim_ekran_panel': 'Donanım - Ekran ve Panel',
            'donanim_guc_batarya': 'Donanım - Güç ve Batarya',
            'donanim_klavye_touchpad': 'Donanım - Klavye ve Touchpad',
            'donanim_mentese_kasa': 'Donanım - Menteşe ve Kasa',
            'donanim_usb_portlar': 'Donanım - USB Portlar',
            'genel_bilgilendirmeler_diger': 'Genel Bilgilendirmeler',
            'kurulum_ve_yazlm_sorunlar': 'Kurulum ve Yazılım Sorunları',
            'performans_sorunlar': 'Performans Sorunları',
            'ses_hoparlor_problemleri': 'Ses ve Hoparlör Problemleri',
            'Monster Model List': 'Monster Model Listesi',
            'Technical Service Information': 'Teknik Servis Bilgileri',
            'Technical Service Office': 'Teknik Servis Ofisleri'
        }
        
        for key, value in category_map.items():
            if key in filename:
                return value
        return 'Diğer'
    
    def _create_vectorstore(self):
        """Create FAISS vectorstore from documents"""
        if not self.documents:
            raise ValueError("No documents loaded!")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(self.documents)
        print(f"✅ Split into {len(split_docs)} chunks")
        
        # Create vectorstore
        print("🔄 Creating FAISS vectorstore...")
        self.vectorstore = FAISS.from_documents(
            documents=split_docs,
            embedding=self.embeddings
        )
        print("✅ Vectorstore created successfully!")
    
    def _setup_qa_chain(self):
        """Setup the QA chain with custom prompt"""
        
        # Create custom prompt template
        prompt_template = """Sen Monster Notebook için özelleşmiş bir teknik destek asistanısın. 
        
        Görevin:
        - Sadece verilen dokümanlar içindeki bilgileri kullan
        - Türkçe yanıt ver
        - Eğer sorunun cevabı dokümanlarda yoksa, bunu belirt
        - Adım adım çözüm önerileri sun
        - Nazik ve profesyonel ol
        - Benzer sorular varsa bunları da öner
        
        Verilen dokümanlar:
        {context}
        
        Geçmiş sohbet:
        {chat_history}
        
        Kullanıcı sorusu: {question}
        
        Yanıt:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question", "chat_history"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Return top 5 relevant documents
            ),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=False
        )
        
        print("✅ QA Chain setup completed!")
    
    def ask(self, question: str) -> dict:
        """Ask a question and get response with sources"""
        if not self.qa_chain:
            raise ValueError("QA chain not initialized!")
        
        try:
            response = self.qa_chain.invoke({"question": question})
            
            return {
                "answer": response["answer"],
                "source_documents": response.get("source_documents", []),
                "sources": [doc.metadata.get("source", "Unknown") for doc in response.get("source_documents", [])]
            }
        
        except Exception as e:
            return {
                "answer": f"Üzgünüm, bir hata oluştu: {str(e)}",
                "source_documents": [],
                "sources": []
            }
    
    def get_relevant_documents(self, query: str, k: int = 3) -> List[Document]:
        """Get relevant documents for a query"""
        if not self.vectorstore:
            return []
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("✅ Conversation memory cleared!")

def main():
    """Main chat loop"""
    print("🤖 Monster Notebook Teknik Destek Chatbot")
    print("💡 LangChain + OpenAI + FAISS RAG Sistemi")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        print("🔄 Chatbot başlatılıyor...")
        chatbot = MonsterRAGChatbot()
        print("✅ Chatbot hazır!\n")
        
        # Welcome message
        print("🎯 Merhaba! Monster Notebook teknik destek asistanınızım.")
        print("📝 Size nasıl yardımcı olabilirim?")
        print("💬 (Çıkmak için 'exit', hafızayı temizlemek için 'clear' yazın)\n")
        
        while True:
            try:
                # Get user input
                user_input = input("👤 Siz: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'çıkış']:
                    print("\n🤖 Asistan: Görüşmek üzere! Monster Notebook desteği her zaman yanınızda.\n")
                    break
                
                if user_input.lower() in ['clear', 'temizle']:
                    chatbot.clear_memory()
                    print("🤖 Asistan: Sohbet geçmişi temizlendi. Yeni bir konuşma başlayabiliriz.\n")
                    continue
                
                # Get response
                print("🔄 Yanıt hazırlanıyor...")
                response = chatbot.ask(user_input)
                
                # Display response
                print(f"\n🤖 Asistan: {response['answer']}")
                
                # Show sources if available
                if response['sources']:
                    unique_sources = list(set(response['sources']))
                    print(f"\n📚 Kaynak dokümanlar: {', '.join(unique_sources)}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n🤖 Asistan: Görüşmek üzere!\n")
                break
            except Exception as e:
                print(f"\n❌ Bir hata oluştu: {str(e)}\n")
                
    except Exception as e:
        print(f"❌ Chatbot başlatılamadı: {str(e)}")
        print("💡 OPENAI_API_KEY environment variable'ının ayarlandığından emin olun.")

if __name__ == "__main__":
    main()
