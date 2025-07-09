#!/usr/bin/env python3
"""
JSON RAG Test Script - Cost-Optimized Testing for All 187 Questions

This script tests the JSON-based RAG system using all questions from veriler.json
with cost-optimized settings.
"""

import json
import time
import os
from json_rag_system import JSONRAGSystem

def load_test_questions():
    """Load all test questions from veriler.json"""
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ veriler.json dosyası bulunamadı!")
        return []

def run_json_rag_test():
    """Run JSON RAG test on all 187 questions"""
    print("🚀 Monster Notebook JSON RAG - COST-OPTIMIZED TEST")
    print("=" * 70)
    
    # Initialize RAG system
    print("🔧 JSON RAG sistemi başlatılıyor...")
    rag = JSONRAGSystem()
    
    if not rag.setup_vector_store():
        print("❌ RAG sistemi kurulamadı!")
        return
    
    # Load test questions
    test_questions = load_test_questions()
    
    if not test_questions:
        print("❌ Test soruları yüklenemedi!")
        return
    
    print(f"📋 {len(test_questions)} soru test edilecek")
    
    # Estimate cost before starting
    estimated_cost = len(test_questions) * 0.000713  # Based on previous RAG test
    print(f"💰 Tahmini toplam maliyet: ${estimated_cost:.4f}")
    print("=" * 70)
    
    # Confirm before starting
    confirm = input("🤔 JSON RAG testine devam edilsin mi? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Test kullanıcı tarafından iptal edildi")
        return
    
    # Initialize statistics
    stats = {
        "total_queries": 0,
        "total_time": 0,
        "total_tokens": 0,
        "total_cost": 0,
        "successful_responses": 0,
        "errors": [],
        "response_times": []
    }
    
    # Results storage
    detailed_results = []
    
    # Progress tracking
    start_time = time.time()
    
    # Test each question
    for i, qa_pair in enumerate(test_questions, 1):
        question = qa_pair.get("soru", "")
        expected_answer = qa_pair.get("cevap", "")
        
        if not question.strip():
            continue
        
        # Calculate ETA
        if i > 1:
            elapsed = time.time() - start_time
            avg_time_per_question = elapsed / (i - 1)
            remaining_questions = len(test_questions) - i + 1
            eta_seconds = avg_time_per_question * remaining_questions
            eta_minutes = eta_seconds / 60
            print(f"\n📋 Test {i}/{len(test_questions)} - ETA: {eta_minutes:.1f} dakika")
        else:
            print(f"\n📋 Test {i}/{len(test_questions)}")
        
        print(f"❓ {question[:80]}...")
        
        # Test JSON RAG system
        print("  📚 JSON RAG...", end="", flush=True)
        result = rag.query(question)
        print(f" ✓ {result['response_time']:.1f}s")
        
        # Update statistics
        stats["total_queries"] += 1
        stats["total_time"] += result['response_time']
        stats["total_tokens"] += result['tokens']
        stats["total_cost"] += result['cost']
        stats["response_times"].append(result['response_time'])
        
        if result['success']:
            stats["successful_responses"] += 1
        else:
            stats["errors"].append(f"Question {i}: {result.get('answer', 'Unknown error')}")
        
        # Store detailed results
        detailed_result = {
            "question_id": i,
            "question": question,
            "expected_answer": expected_answer,
            "json_rag_result": result
        }
        detailed_results.append(detailed_result)
        
        # Save progress every 25 questions
        if i % 25 == 0:
            print(f"  💾 İlerleme kaydediliyor... ({i}/{len(test_questions)} tamamlandı)")
            save_progress_results(detailed_results, stats, i)
    
    # Save final results
    total_test_time = time.time() - start_time
    save_final_results(detailed_results, stats, total_test_time)
    
    # Print summary
    print_summary(stats, total_test_time, len(test_questions))

def save_progress_results(detailed_results, stats, current_question):
    """Save progress results"""
    filename = f"json_rag_progress_{current_question}.json"
    
    progress_data = {
        "test_summary": {
            "test_type": "JSON_RAG_COST_OPTIMIZED_PROGRESS",
            "questions_completed": len(detailed_results),
            "total_questions": 187,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "gpt-4o-mini",
            "data_source": "documents/json/*.json files"
        },
        "results": detailed_results,
        "current_statistics": stats.copy()
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def save_final_results(detailed_results, stats, total_test_time):
    """Save final comprehensive results"""
    final_results = {
        "test_summary": {
            "test_type": "JSON_RAG_COST_OPTIMIZED_ALL_187",
            "questions_tested": len(detailed_results),
            "total_questions_available": 187,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "gpt-4o-mini",
            "data_source": "documents/json/*.json files",
            "total_test_time_minutes": total_test_time / 60
        },
        "results": detailed_results,
        "final_statistics": stats
    }
    
    filename = "json_rag_all_187_results.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Final sonuçlar kaydedildi: {filename}")

def print_summary(stats, total_test_time, total_questions):
    """Print test summary"""
    successes = stats["successful_responses"]
    failures = len(stats["errors"])
    avg_response_time = stats["total_time"] / max(stats["total_queries"], 1)
    avg_cost = stats["total_cost"] / max(stats["total_queries"], 1)
    response_times = stats["response_times"]
    
    # Calculate response time distribution
    fast_responses = len([t for t in response_times if t < 3])
    medium_responses = len([t for t in response_times if 3 <= t <= 7])
    slow_responses = len([t for t in response_times if t > 7])
    
    print("\n" + "=" * 70)
    print("🎉 JSON RAG COST-OPTIMIZED TEST TAMAMLANDI!")
    print("=" * 70)
    print(f"📋 Test Edilen Sorular: {total_questions}")
    print(f"⏱️  Toplam Süre: {total_test_time/60:.1f} dakika")
    print(f"📊 Başarı Oranı: {successes}/{total_questions} ({successes/total_questions*100:.1f}%)")
    print(f"⚡ Ortalama Yanıt Süresi: {avg_response_time:.1f}s")
    print(f"📈 Medyan Yanıt Süresi: {sorted(response_times)[len(response_times)//2]:.1f}s")
    print(f"⚡ En Hızlı: {min(response_times):.1f}s")
    print(f"🐌 En Yavaş: {max(response_times):.1f}s")
    print(f"💰 Toplam Maliyet: ${stats['total_cost']:.4f}")
    print(f"💳 Sorgu Başına Maliyet: ${avg_cost:.6f}")
    print(f"🔤 Toplam Token: {stats['total_tokens']:,}")
    print(f"📈 Verimlilik: {total_questions/(total_test_time/60):.1f} soru/dakika")
    print(f"📊 Hızlı yanıtlar (<3s): {fast_responses} ({fast_responses/total_questions*100:.1f}%)")
    print(f"📊 Orta yanıtlar (3-7s): {medium_responses} ({medium_responses/total_questions*100:.1f}%)")
    print(f"📊 Yavaş yanıtlar (>7s): {slow_responses} ({slow_responses/total_questions*100:.1f}%)")
    
    if failures > 0:
        print(f"❌ Hatalar: {failures}")
        print("Hata detayları sonuç dosyasında kaydedildi")
    
    print("=" * 70)

if __name__ == "__main__":
    run_json_rag_test()
