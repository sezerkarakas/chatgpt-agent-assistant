#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RAG Chatbot - Returns original content from vectorstore
"""

import os
import json
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

class SimpleRAGChatbot:
    def __init__(self):
        """Initialize the simple RAG chatbot"""
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
        self.conversation_history = []
        
        # Load vectorstore
        self._load_vectorstore()
        self._setup_chain()
    
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
    
    def _setup_chain(self):
        """Setup the RAG chain"""
        
        # Create prompt template
        template = """Sen Monster Notebook için özelleşmiş bir teknik destek asistanısın.

ÇOK ÖNEMLİ KURAL: Aşağıdaki dokümanlarda verilen cevapları AYNEN, EKSIKSIZ olarak kullan. Hiçbir şeyi değiştirme, özetleme, çıkarma!

Görevin:
- Dokümanlardan ilgili sorunun cevabını bul
- O cevabı TAMAMEN, AYNEN kullan 
- Hiçbir bilgiyi eksiltme, değiştirme
- Sadece nazik bir giriş cümlesi ekle
- Tüm linkleri, adımları, modelleri aynen koru

Sohbet Geçmişi:
{chat_history}

İlgili Dokümanlar:
{context}

Kullanıcı Sorusu: {question}

Yanıt (Dokümandaki cevabı AYNEN kopyala, hiçbir şeyi değiştirme):"""
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Top 3 relevant documents
        )
        
        # Create chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        def format_chat_history(history):
            if not history:
                return ""
            formatted = []
            for item in history[-5:]:  # Last 5 conversations
                formatted.append(f"Kullanıcı: {item['question']}")
                formatted.append(f"Asistan: {item['answer'][:200]}...")
            return "\n".join(formatted)
        
        self.rag_chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: format_chat_history(self.conversation_history)
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("✅ RAG Chain setup completed!")
    
    def ask(self, question: str) -> dict:
        """Ask a question and get response with sources"""
        try:
            # Get relevant documents first
            relevant_docs = self.retriever.invoke(question)
            
            # Get response from chain
            response = self.rag_chain.invoke(question)
            
            # Add to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": response
            })
            
            return {
                "answer": response,
                "source_documents": relevant_docs,
                "sources": [doc.metadata.get("source", "Unknown") for doc in relevant_docs]
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
        self.conversation_history = []
        print("✅ Conversation memory cleared!")

def main():
    """Main chat loop"""
    print("🤖 Monster Notebook Simple RAG Chatbot")
    print("💡 LangChain + OpenAI + FAISS - Tam İçerik Sistemi")
    print("=" * 60)
    
    try:
        # Initialize chatbot
        print("🔄 Chatbot başlatılıyor...")
        chatbot = SimpleRAGChatbot()
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
                
                print("-" * 60)
                
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
