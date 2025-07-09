import os
import re
import time
import json
from typing import List, Dict
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI()

class RAGSystem:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.document_chunks = []
        self.load_documents()
        self.create_embeddings()
        
        # Load system prompt
        try:
            with open('gpt_prompt_v333.md', 'r', encoding='utf-8') as file:
                self.system_prompt = file.read()
        except FileNotFoundError:
            print("Hata: gpt_prompt_v333.md dosyası bulunamadı!")
            self.system_prompt = "Sen Monster Notebook teknik destek asistanısın."

    def load_documents(self):
        """Load all documents from the documents folder"""
        document_files = [
            'documents/Technical Service Information.txt',
            'documents/Monster Model List.txt', 
            'documents/Problems and Solutions.txt',
            'documents/Technical Service Office.txt'
        ]
        
        # Add JSON files from the json subfolder
        json_files = [
            'documents/json/baglant_ag_sorunlar.json',
            'documents/json/donanim_ekran_panel.json',
            'documents/json/donanim_guc_batarya.json',
            'documents/json/donanim_klavye_touchpad.json',
            'documents/json/donanim_mentese_kasa.json',
            'documents/json/donanim_usb_portlar.json',
            'documents/json/genel_bilgilendirmeler_diger.json',
            'documents/json/kurulum_ve_yazlm_sorunlar.json',
            'documents/json/Monster Model List.json',
            'documents/json/performans_sorunlar.json',
            'documents/json/ses_hoparlor_problemleri.json',
            'documents/json/Technical Service Information.json',
            'documents/json/Technical Service Office.json'
        ]
        
        all_files = document_files + json_files
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Split into chunks of ~1000 characters
                    chunks = self.split_text(content, 1000)
                    for chunk in chunks:
                        self.documents.append({
                            'source': file_path,
                            'content': chunk
                        })
                print(f"✓ Loaded: {file_path}")
            except FileNotFoundError:
                print(f"✗ Not found: {file_path}")
            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}")

    def split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def create_embeddings(self):
        """Create embeddings for all document chunks"""
        print("Creating embeddings...")
        start_time = time.time()
        
        for doc in self.documents:
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=doc['content']
                )
                self.embeddings.append(response.data[0].embedding)
                self.document_chunks.append(doc['content'])
            except Exception as e:
                print(f"Error creating embedding: {e}")
                
        end_time = time.time()
        print(f"✓ Created {len(self.embeddings)} embeddings in {end_time - start_time:.2f} seconds")

    def search_similar_documents(self, query: str, top_k: int = 3) -> List[str]:
        """Search for similar documents using cosine similarity"""
        if not self.embeddings:
            return []
            
        # Create query embedding
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Get top k most similar documents
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        return [self.document_chunks[i] for i in top_indices if similarities[i] > 0.3]

    def generate_response(self, user_query: str, conversation_history: List[Dict] = None) -> Dict:
        """Generate response using RAG"""
        start_time = time.time()
        
        # Search for relevant documents
        search_start = time.time()
        relevant_docs = self.search_similar_documents(user_query)
        search_time = time.time() - search_start
        
        # Create context from relevant documents
        context = "\n\n".join(relevant_docs) if relevant_docs else "Relevanter Belgeler bulunamadı."
        
        # Create messages
        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n\nBağlam Bilgileri:\n{context}"}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
            
        messages.append({"role": "user", "content": user_query})
        
        # Generate response
        generation_start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        generation_time = time.time() - generation_start
        
        total_time = time.time() - start_time
        
        # Calculate cost based on GPT-4o-mini pricing
        # Input: $0.00015 per 1K tokens, Output: $0.0006 per 1K tokens
        input_cost = (response.usage.prompt_tokens / 1000) * 0.00015
        output_cost = (response.usage.completion_tokens / 1000) * 0.0006
        total_cost = input_cost + output_cost
        
        return {
            'response': response.choices[0].message.content,
            'total_time': total_time,
            'search_time': search_time,
            'generation_time': generation_time,
            'relevant_docs_count': len(relevant_docs),
            'total_tokens': response.usage.total_tokens,
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'cost_estimate': total_cost
        }

def temizle_citation(cevap):
    return re.sub(r"【\d+:\d+†.*?】", "", cevap)

def chat_rag():
    print("\n🤖 Monster Terminal Asistanı (RAG Versiyonu) - Başlatılıyor...")
    
    # Initialize RAG system
    rag = RAGSystem()
    conversation_history = []
    
    print(f"\n✓ RAG sistemi hazır! {len(rag.documents)} belge yüklendi.")
    print("Çıkmak için 'exit' yazın, istatistikleri görmek için 'stats' yazın\n")
    
    # Stats tracking
    total_queries = 0
    total_time = 0
    total_tokens = 0
    
    while True:
        try:
            user_input = input("Siz: ")
            
            if user_input.lower() == 'exit':
                print(f"\n📊 Oturum İstatistikleri:")
                print(f"Toplam sorgu: {total_queries}")
                print(f"Ortalama yanıt süresi: {total_time/max(total_queries,1):.2f} saniye")
                print(f"Toplam token kullanımı: {total_tokens}")
                print("\nAsistan: Görüşmek üzere! Monster Terminal Asistanı her zaman yanınızda.\n")
                break
                
            if user_input.lower() == 'stats':
                print(f"\n📊 Anlık İstatistikler:")
                print(f"Toplam sorgu: {total_queries}")
                print(f"Ortalama yanıt süresi: {total_time/max(total_queries,1):.2f} saniye")
                print(f"Toplam token kullanımı: {total_tokens}")
                continue
            
            if not user_input.strip():
                continue
                
            # Generate response
            result = rag.generate_response(user_input, conversation_history[-10:])  # Keep last 10 messages
            
            # Update stats
            total_queries += 1
            total_time += result['total_time']
            total_tokens += result['total_tokens']
            
            # Display response
            print(f"\nAsistan: {result['response']}")
            print(f"\n⚡ Yanıt süresi: {result['total_time']:.2f}s | Token: {result['total_tokens']} | Belge: {result['relevant_docs_count']}\n")
            
            # Update conversation history
            conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": result['response']}
            ])
            
        except KeyboardInterrupt:
            print("\nAsistan: Görüşmek üzere!\n")
            break
        except Exception as e:
            print(f"\nHata oluştu: {str(e)}\n")

if __name__ == "__main__":
    chat_rag()
