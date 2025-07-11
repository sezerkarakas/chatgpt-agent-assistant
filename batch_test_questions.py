#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monster Notebook RAG System - Batch Question Evaluator
Tests all questions from veriler.json and creates a comparison report
"""

import json
import time
from datetime import datetime
from simple_rag_chatbot import SimpleRAGChatbot

def batch_test_questions():
    """Test all questions from veriler.json and create comparison report"""
    
    # Load test questions
    print("📄 Loading test questions from veriler.json...")
    try:
        with open('veriler.json', 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        print(f"✅ Loaded {len(test_data)} questions")
    except Exception as e:
        print(f"❌ Error loading veriler.json: {str(e)}")
        return
    
    # Initialize chatbot
    print("🤖 Initializing RAG chatbot...")
    try:
        chatbot = SimpleRAGChatbot()
        print("✅ Chatbot ready!")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {str(e)}")
        return
    
    # Prepare results
    results = []
    total_questions = len(test_data)
    
    print(f"\n🚀 Starting batch test of {total_questions} questions...")
    print("⏱️ Estimated time: ~{:.1f} minutes".format(total_questions * 3 / 60))
    print("💰 Estimated cost: ~$0.13 (3.5 TL)")
    
    input("\n🔶 Press Enter to continue or Ctrl+C to cancel...")
    
    start_time = time.time()
    
    for i, item in enumerate(test_data, 1):
        question = item.get('soru', '')
        expected_answer = item.get('cevap', '')
        
        print(f"\n📝 Processing question {i}/{total_questions}")
        print(f"Question: {question[:100]}...")
        
        try:
            # Get chatbot response
            response = chatbot.ask(question)
            actual_answer = response['answer']
            sources = response.get('sources', [])
            
            # Calculate similarity metrics
            expected_length = len(expected_answer)
            actual_length = len(actual_answer)
            length_ratio = actual_length / expected_length if expected_length > 0 else 0
            
            # Check for key terms preservation
            key_terms_preserved = []
            key_terms = ['Monster', 'Windows', 'USB', 'F2', 'F11', 'ABRA', 'TULPAR', 'HUMA', 'teknik servis']
            for term in key_terms:
                if term.lower() in expected_answer.lower() and term.lower() in actual_answer.lower():
                    key_terms_preserved.append(term)
            
            result = {
                'question_id': i,
                'question': question,
                'expected_answer': expected_answer,
                'actual_answer': actual_answer,
                'sources': sources,
                'metrics': {
                    'expected_length': expected_length,
                    'actual_length': actual_length,
                    'length_ratio': round(length_ratio, 2),
                    'key_terms_preserved': key_terms_preserved,
                    'key_terms_count': len(key_terms_preserved),
                    'has_links': 'http' in actual_answer,
                    'has_phone': '0850' in actual_answer or '255' in actual_answer
                },
                'timestamp': datetime.now().isoformat()
            }
            
            results.append(result)
            
            print(f"✅ Completed {i}/{total_questions} - Length ratio: {length_ratio:.2f}")
            
            # Rate limiting - wait 1 second between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing question {i}: {str(e)}")
            result = {
                'question_id': i,
                'question': question,
                'expected_answer': expected_answer,
                'actual_answer': f"ERROR: {str(e)}",
                'sources': [],
                'metrics': {
                    'expected_length': len(expected_answer),
                    'actual_length': 0,
                    'length_ratio': 0,
                    'key_terms_preserved': [],
                    'key_terms_count': 0,
                    'has_links': False,
                    'has_phone': False
                },
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            continue
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate overall statistics
    successful_tests = len([r for r in results if not r['actual_answer'].startswith('ERROR')])
    avg_length_ratio = sum(r['metrics']['length_ratio'] for r in results if r['metrics']['length_ratio'] > 0) / successful_tests if successful_tests > 0 else 0
    questions_with_links = len([r for r in results if r['metrics']['has_links']])
    questions_with_phone = len([r for r in results if r['metrics']['has_phone']])
    
    # Create summary report
    summary = {
        'test_info': {
            'total_questions': total_questions,
            'successful_tests': successful_tests,
            'failed_tests': total_questions - successful_tests,
            'test_duration_seconds': round(total_time, 2),
            'test_duration_minutes': round(total_time / 60, 2),
            'test_date': datetime.now().isoformat()
        },
        'performance_metrics': {
            'average_length_ratio': round(avg_length_ratio, 2),
            'questions_with_links': questions_with_links,
            'questions_with_phone_numbers': questions_with_phone,
            'success_rate': round(successful_tests / total_questions * 100, 2)
        },
        'detailed_results': results
    }
    
    # Save results to JSON file
    output_filename = f"rag_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 Test completed successfully!")
        print(f"📊 Results saved to: {output_filename}")
        print(f"⏱️ Total time: {total_time / 60:.1f} minutes")
        print(f"✅ Success rate: {successful_tests}/{total_questions} ({successful_tests/total_questions*100:.1f}%)")
        print(f"📏 Average length ratio: {avg_length_ratio:.2f}")
        print(f"🔗 Questions with links: {questions_with_links}")
        print(f"📞 Questions with phone numbers: {questions_with_phone}")
        
        # Create a simple summary file
        summary_filename = f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("Monster Notebook RAG System - Test Summary\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Total Questions: {total_questions}\\n")
            f.write(f"Successful Tests: {successful_tests}\\n")
            f.write(f"Success Rate: {successful_tests/total_questions*100:.1f}%\\n")
            f.write(f"Average Length Ratio: {avg_length_ratio:.2f}\\n")
            f.write(f"Test Duration: {total_time/60:.1f} minutes\\n")
            f.write(f"\\nDetailed results saved in: {output_filename}\\n")
        
        print(f"📋 Summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

if __name__ == "__main__":
    batch_test_questions()
