"""
Quick test script to verify RAG system is working correctly
"""

import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

try:
    from chat_assistant_rag import RAGSystem
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("rag_module", "chat-assistant-rag.py")
    rag_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rag_module)
    RAGSystem = rag_module.RAGSystem

def test_rag():
    print("🔍 RAG sistemi test ediliyor...")
    
    try:
        # Initialize RAG system
        rag = RAGSystem()
        
        print(f"✅ RAG sistemi başlatıldı:")
        print(f"   - {len(rag.documents)} belge yüklendi")
        print(f"   - {len(rag.embeddings)} embedding oluşturuldu")
        
        # Test with a simple question
        test_question = "Monster notebook modellerini listeleyebilir misin?"
        print(f"\n📝 Test sorusu: {test_question}")
        
        result = rag.generate_response(test_question)
        
        print(f"\n✅ RAG Yanıtı:")
        print(f"Yanıt: {result['response'][:200]}...")
        print(f"Süre: {result['total_time']:.2f} saniye")
        print(f"Token: {result['total_tokens']}")
        print(f"Bulunan belge sayısı: {result['relevant_docs_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test hatası: {e}")
        return False

if __name__ == "__main__":
    test_rag()
