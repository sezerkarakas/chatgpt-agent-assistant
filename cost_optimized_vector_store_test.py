#!/usr/bin/env python3
"""
Cost-Optimized Vector Store Testing Script for Monster Notebook Technical Support AI

This script tests Vector Store approach with cost optimizations similar to the RAG test.
"""

import json
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Cost optimization settings for Vector Store
VECTOR_STORE_OPTIMIZATION = {
    "model": "gpt-4o-mini",           # Cheapest model
    "max_tokens": 1000,               # Increased from 500
    "temperature": 0.1,               # Lower temperature for consistency
    "use_lightweight_context": True,  # Use reduced context
    "context_limit": 15000,           # Limit context tokens to reduce cost
    "prioritize_veriler": True        # Prioritize Q&A pairs over other docs
}

# Track statistics
stats = {
    "total_queries": 0,
    "total_time": 0,
    "total_tokens": 0,
    "total_cost": 0,
    "successful_responses": 0,
    "errors": []
}

def temizle_citation(cevap):
    """Remove citation markers from responses"""
    return re.sub(r"【\d+:\d+†.*?】", "", cevap)

def estimate_tokens(text):
    """Estimate token count for text"""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    return len(encoding.encode(text))

def estimate_cost(prompt_tokens, completion_tokens, model="gpt-4o-mini"):
    """Estimate cost based on token usage"""
    if model == "gpt-4o-mini":
        prompt_cost = prompt_tokens * 0.00000015  # $0.15 per 1M tokens
        completion_cost = completion_tokens * 0.0000006  # $0.60 per 1M tokens
    return prompt_cost + completion_cost

def load_optimized_context():
    """Load optimized context for Vector Store system"""
    print("🔧 Loading optimized context for Vector Store...")
    
    context_parts = []
    total_tokens = 0
    target_tokens = VECTOR_STORE_OPTIMIZATION["context_limit"]
    
    # Priority 1: Load all Q&A pairs from veriler.json (most important)
    if os.path.exists("veriler.json"):
        with open("veriler.json", 'r', encoding='utf-8') as f:
            veriler_data = json.load(f)
            qa_context = []
            for qa_pair in veriler_data:
                qa_text = f"S: {qa_pair.get('soru', '')}\nC: {qa_pair.get('cevap', '')}"
                qa_context.append(qa_text)
            
            qa_full_text = "=== SIK SORULAN SORULAR ===\n" + "\n\n".join(qa_context)
            qa_tokens = estimate_tokens(qa_full_text)
            
            if qa_tokens <= target_tokens:
                context_parts.append(qa_full_text)
                total_tokens += qa_tokens
                print(f"✓ Loaded Q&A pairs: {qa_tokens} tokens")
            else:
                # If Q&A is too large, truncate smartly
                truncated_qa = qa_context[:int(len(qa_context) * target_tokens / qa_tokens)]
                qa_truncated_text = "=== SIK SORULAN SORULAR (TRUNCATED) ===\n" + "\n\n".join(truncated_qa)
                context_parts.append(qa_truncated_text)
                total_tokens = estimate_tokens(qa_truncated_text)
                print(f"✓ Loaded Q&A pairs (truncated): {total_tokens} tokens")
    
    # Priority 2: Add essential technical documents if space allows
    remaining_tokens = target_tokens - total_tokens
    
    if remaining_tokens > 1000:  # Only add if significant space remains
        essential_files = [
            "documents/Problems and Solutions.txt",
            "documents/Technical Service Information.txt"
        ]
        
        for file_path in essential_files:
            if os.path.exists(file_path) and remaining_tokens > 500:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Take a portion that fits in remaining space
                    content_tokens = estimate_tokens(content)
                    if content_tokens <= remaining_tokens - 100:  # Leave some buffer
                        context_parts.append(f"=== {file_path} ===\n{content}")
                        total_tokens += content_tokens
                        remaining_tokens -= content_tokens
                        print(f"✓ Added {file_path}: {content_tokens} tokens")
                    else:
                        # Truncate content to fit
                        truncate_ratio = (remaining_tokens - 100) / content_tokens
                        truncated_content = content[:int(len(content) * truncate_ratio)]
                        truncated_text = f"=== {file_path} (TRUNCATED) ===\n{truncated_content}"
                        context_parts.append(truncated_text)
                        used_tokens = estimate_tokens(truncated_text)
                        total_tokens += used_tokens
                        remaining_tokens -= used_tokens
                        print(f"✓ Added {file_path} (truncated): {used_tokens} tokens")
    
    full_context = "\n\n".join(context_parts)
    final_tokens = estimate_tokens(full_context)
    
    print(f"📊 Total context tokens: {final_tokens:,}")
    print(f"🎯 Target was: {target_tokens:,}")
    print(f"💰 Estimated context cost per query: ${estimate_cost(final_tokens, 0):.6f}")
    
    return full_context

def load_system_prompt():
    """Load system prompt from file"""
    try:
        with open("gpt_prompt_v333.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Sen Monster Notebook teknik destek uzmanısın. Kullanıcıların teknik sorunlarına yardımcı ol."

def vector_store_query(question, system_prompt, full_context):
    """Process query using optimized Vector Store approach"""
    try:
        start_time = time.time()
        
        # Create optimized messages for chat completion
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Kullanılabilir Dokümanlar:
{full_context}

Kullanıcı Sorusu: {question}

Lütfen yukarıdaki dokümanları kullanarak soruya detaylı ve yararlı bir yanıt ver."""}
        ]
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model=VECTOR_STORE_OPTIMIZATION["model"],
            messages=messages,
            temperature=VECTOR_STORE_OPTIMIZATION["temperature"],
            max_tokens=VECTOR_STORE_OPTIMIZATION["max_tokens"]
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        answer = response.choices[0].message.content
        answer = temizle_citation(answer)
        
        # Estimate tokens and cost
        prompt_tokens = estimate_tokens(str(messages))
        completion_tokens = estimate_tokens(answer)
        cost = estimate_cost(prompt_tokens, completion_tokens, VECTOR_STORE_OPTIMIZATION["model"])
        
        # Update stats
        stats["total_queries"] += 1
        stats["total_time"] += response_time
        stats["total_tokens"] += prompt_tokens + completion_tokens
        stats["total_cost"] += cost
        stats["successful_responses"] += 1
        
        return {
            "answer": answer,
            "response_time": response_time,
            "tokens": prompt_tokens + completion_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": cost,
            "success": True
        }
        
    except Exception as e:
        stats["errors"].append(str(e))
        return {
            "answer": f"Hata oluştu: {str(e)}",
            "response_time": 0,
            "tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost": 0,
            "success": False
        }

def load_test_questions():
    """Load all test questions from veriler.json"""
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ veriler.json dosyası bulunamadı!")
        return []

def run_vector_store_test():
    """Run optimized Vector Store test on all 187 questions"""
    print("🚀 Monster Notebook AI - COST-OPTIMIZED VECTOR STORE TEST")
    print("=" * 70)
    
    # Load components
    system_prompt = load_system_prompt()
    full_context = load_optimized_context()
    test_questions = load_test_questions()
    
    if not test_questions:
        print("❌ Test soruları yüklenemedi!")
        return
    
    # Estimate total cost before starting
    context_tokens = estimate_tokens(full_context)
    system_tokens = estimate_tokens(system_prompt)
    avg_question_tokens = 50  # Approximate
    avg_response_tokens = 300  # Based on max_tokens=500
    
    estimated_tokens_per_query = context_tokens + system_tokens + avg_question_tokens + avg_response_tokens
    total_estimated_cost = len(test_questions) * estimate_cost(
        estimated_tokens_per_query - avg_response_tokens,
        avg_response_tokens
    )
    
    print(f"📋 Testing ALL {len(test_questions)} questions")
    print(f"🔧 Model: {VECTOR_STORE_OPTIMIZATION['model']}")
    print(f"📊 Context tokens: {context_tokens:,}")
    print(f"💰 Estimated total cost: ${total_estimated_cost:.4f}")
    print(f"💳 Estimated cost per query: ${total_estimated_cost/len(test_questions):.6f}")
    print("=" * 70)
    
    # Confirm before starting
    confirm = input("🤔 Continue with Vector Store test? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Test cancelled by user")
        return
    
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
            print(f"\n📋 Test {i}/{len(test_questions)} - ETA: {eta_minutes:.1f} min")
        else:
            print(f"\n📋 Test {i}/{len(test_questions)}")
        
        print(f"❓ {question[:80]}...")
        
        # Test Vector Store system
        print("  📚 Vector Store...", end="", flush=True)
        vs_result = vector_store_query(question, system_prompt, full_context)
        print(f" ✓ {vs_result['response_time']:.1f}s")
        
        # Store detailed results
        result = {
            "question_id": i,
            "question": question,
            "expected_answer": expected_answer,
            "vector_store_result": vs_result
        }
        detailed_results.append(result)
        
        # Save progress every 25 questions
        if i % 25 == 0:
            print(f"  💾 Saving progress... ({i}/{len(test_questions)} completed)")
            save_progress_results(detailed_results, i)
    
    # Save final results
    total_test_time = time.time() - start_time
    save_final_results(detailed_results, total_test_time)
    
    # Print summary
    print_summary(total_test_time, len(test_questions))

def save_progress_results(detailed_results, current_question):
    """Save progress results"""
    filename = f"vector_store_progress_{current_question}.json"
    
    progress_data = {
        "test_summary": {
            "test_type": "VECTOR_STORE_COST_OPTIMIZED_PROGRESS",
            "questions_completed": len(detailed_results),
            "total_questions": 187,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": VECTOR_STORE_OPTIMIZATION["model"],
            "optimizations": VECTOR_STORE_OPTIMIZATION
        },
        "results": detailed_results,
        "current_statistics": stats.copy()
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def save_final_results(detailed_results, total_test_time):
    """Save final comprehensive results"""
    final_results = {
        "test_summary": {
            "test_type": "VECTOR_STORE_COST_OPTIMIZED_ALL_187",
            "questions_tested": len(detailed_results),
            "total_questions_available": 187,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": VECTOR_STORE_OPTIMIZATION["model"],
            "total_test_time_minutes": total_test_time / 60,
            "optimizations_applied": VECTOR_STORE_OPTIMIZATION
        },
        "results": detailed_results,
        "final_statistics": stats
    }
    
    filename = "cost_optimized_vector_store_all_187.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Final results saved to: {filename}")

def print_summary(total_test_time, total_questions):
    """Print test summary"""
    successes = stats["successful_responses"]
    failures = len(stats["errors"])
    avg_response_time = stats["total_time"] / max(stats["total_queries"], 1)
    avg_cost = stats["total_cost"] / max(stats["total_queries"], 1)
    
    print("\n" + "=" * 70)
    print("🎉 VECTOR STORE COST-OPTIMIZED TEST COMPLETED!")
    print("=" * 70)
    print(f"📋 Questions Tested: {total_questions}")
    print(f"⏱️  Total Time: {total_test_time/60:.1f} minutes")
    print(f"📊 Success Rate: {successes}/{total_questions} ({successes/total_questions*100:.1f}%)")
    print(f"⚡ Avg Response Time: {avg_response_time:.1f}s")
    print(f"💰 Total Cost: ${stats['total_cost']:.4f}")
    print(f"💳 Cost per Query: ${avg_cost:.6f}")
    print(f"🔧 Model Used: {VECTOR_STORE_OPTIMIZATION['model']}")
    print(f"📈 Throughput: {total_questions/(total_test_time/60):.1f} questions/minute")
    
    if failures > 0:
        print(f"❌ Errors: {failures}")
        print("Error details saved in results file")
    
    print("=" * 70)

if __name__ == "__main__":
    run_vector_store_test()
