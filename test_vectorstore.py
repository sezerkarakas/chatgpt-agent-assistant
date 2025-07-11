#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to compare vectorstore response with original JSON data
"""

from simple_rag_chatbot import SimpleRAGChatbot
import json

def test_vectorstore_accuracy():
    """Test if vectorstore returns complete answers from JSON"""
    
    # Initialize chatbot
    print('🤖 Chatbot başlatılıyor...')
    bot = SimpleRAGChatbot()
    
    # Test question from kurulum_ve_yazlm_sorunlar.json
    test_question = "Bilgisayarımı yeni aldım. Windows kurulumunu yapamıyorum. Bu konuda bana destek olabilir misiniz?"
    
    print(f'\n❓ Test Sorusu:')
    print(f'"{test_question}"')
    print('=' * 80)
    
    # Get chatbot response
    print('🔄 Chatbot\'tan cevap alınıyor...')
    response = bot.ask(test_question)
    
    print(f'\n🤖 Chatbot Cevabı:')
    print(response['answer'])
    print(f'\n📚 Kaynaklar: {response["sources"]}')
    
    # Load original JSON data
    print('\n' + '=' * 80)
    print('📄 Orijinal JSON Cevabını yüklüyor...')
    
    with open('documents/json/kurulum_ve_yazlm_sorunlar.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find the matching question
    original_answer = None
    for item in data:
        if "Windows kurulumunu yapamıyorum" in item['soru']:
            original_answer = item['cevap']
            break
    
    print(f'\n📋 Orijinal JSON Cevabı:')
    print(original_answer)
    
    # Compare lengths
    print('\n' + '=' * 80)
    print('📊 Karşılaştırma:')
    print(f'Chatbot cevap uzunluğu: {len(response["answer"])} karakter')
    print(f'Orijinal cevap uzunluğu: {len(original_answer)} karakter')
    
    # Check if key information is preserved
    key_terms = [
        'FreeDOS', 'Windows 10', 'Windows 11', 'USB bellek', 
        'Microsoft', 'RUFUS', 'F2', 'F11', 'ABRA', 'TULPAR', 'HUMA'
    ]
    
    print(f'\n🔍 Anahtar terimler kontrolü:')
    for term in key_terms:
        in_original = term in original_answer
        in_chatbot = term in response['answer']
        status = "✅" if in_chatbot else "❌"
        print(f'{status} {term}: Orijinal={in_original}, Chatbot={in_chatbot}')

if __name__ == "__main__":
    test_vectorstore_accuracy()
