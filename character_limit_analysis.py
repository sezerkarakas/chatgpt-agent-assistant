#!/usr/bin/env python3
"""
Character Limit Analysis for AI Response Systems
Analyzes character counts and token usage in both JSON RAG and Vector Store systems
"""

import json
import statistics

def analyze_character_limits():
    """Analyze character limits in both systems"""
    print("📊 Character Limit Analysis - Monster Notebook AI Systems")
    print("=" * 70)
    
    # Load results from both systems
    try:
        with open("json_rag_all_187_results.json", "r", encoding="utf-8") as f:
            json_rag_data = json.load(f)
        
        with open("cost_optimized_vector_store_all_187.json", "r", encoding="utf-8") as f:
            vector_store_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Dosya bulunamadı: {e}")
        return
    
    # Extract responses and analyze character counts
    json_rag_responses = []
    vector_store_responses = []
    
    # JSON RAG analysis
    for result in json_rag_data.get("results", []):
        if "json_rag_result" in result:
            answer = result["json_rag_result"].get("answer", "")
            completion_tokens = result["json_rag_result"].get("completion_tokens", 0)
            json_rag_responses.append({
                "character_count": len(answer),
                "completion_tokens": completion_tokens,
                "question_id": result.get("question_id", 0)
            })
    
    # Vector Store analysis
    for result in vector_store_data.get("results", []):
        if "vector_store_result" in result:
            answer = result["vector_store_result"].get("answer", "")
            completion_tokens = result["vector_store_result"].get("completion_tokens", 0)
            vector_store_responses.append({
                "character_count": len(answer),
                "completion_tokens": completion_tokens,
                "question_id": result.get("question_id", 0)
            })
    
    # Calculate statistics
    def calculate_stats(responses, system_name):
        if not responses:
            return {}
        
        char_counts = [r["character_count"] for r in responses]
        token_counts = [r["completion_tokens"] for r in responses]
        
        # Find max character responses
        max_char_response = max(responses, key=lambda x: x["character_count"])
        min_char_response = min(responses, key=lambda x: x["character_count"])
        
        # Find max token responses
        max_token_response = max(responses, key=lambda x: x["completion_tokens"])
        
        # Count responses hitting token limit (500 tokens)
        token_limit_hits = len([r for r in responses if r["completion_tokens"] >= 500])
        
        return {
            "system": system_name,
            "total_responses": len(responses),
            "character_stats": {
                "min": min(char_counts),
                "max": max(char_counts),
                "avg": statistics.mean(char_counts),
                "median": statistics.median(char_counts),
                "min_response_id": min_char_response["question_id"],
                "max_response_id": max_char_response["question_id"]
            },
            "token_stats": {
                "min": min(token_counts),
                "max": max(token_counts),
                "avg": statistics.mean(token_counts),
                "median": statistics.median(token_counts),
                "max_response_id": max_token_response["question_id"]
            },
            "token_limit_analysis": {
                "max_tokens_setting": 500,
                "responses_hitting_limit": token_limit_hits,
                "percentage_hitting_limit": (token_limit_hits / len(responses)) * 100,
                "responses_near_limit_450_499": len([r for r in responses if 450 <= r["completion_tokens"] < 500]),
                "responses_under_250": len([r for r in responses if r["completion_tokens"] < 250])
            },
            "character_to_token_ratio": {
                "avg_chars_per_token": statistics.mean([r["character_count"] / max(r["completion_tokens"], 1) for r in responses])
            }
        }
    
    # Calculate stats for both systems
    json_rag_stats = calculate_stats(json_rag_responses, "JSON RAG")
    vector_store_stats = calculate_stats(vector_store_responses, "Vector Store")
    
    # Create comprehensive analysis
    analysis = {
        "analysis_date": "2025-07-09",
        "configuration": {
            "max_tokens_setting": 500,
            "model": "gpt-4o-mini",
            "purpose": "Cost optimization while maintaining quality"
        },
        "json_rag_analysis": json_rag_stats,
        "vector_store_analysis": vector_store_stats,
        "comparison": {
            "character_limits": {
                "json_rag_max_chars": json_rag_stats["character_stats"]["max"],
                "vector_store_max_chars": vector_store_stats["character_stats"]["max"],
                "winner": "JSON RAG" if json_rag_stats["character_stats"]["max"] > vector_store_stats["character_stats"]["max"] else "Vector Store"
            },
            "token_usage": {
                "json_rag_avg_tokens": json_rag_stats["token_stats"]["avg"],
                "vector_store_avg_tokens": vector_store_stats["token_stats"]["avg"],
                "more_efficient": "JSON RAG" if json_rag_stats["token_stats"]["avg"] < vector_store_stats["token_stats"]["avg"] else "Vector Store"
            },
            "token_limit_hits": {
                "json_rag_hits": json_rag_stats["token_limit_analysis"]["responses_hitting_limit"],
                "vector_store_hits": vector_store_stats["token_limit_analysis"]["responses_hitting_limit"],
                "json_rag_percentage": json_rag_stats["token_limit_analysis"]["percentage_hitting_limit"],
                "vector_store_percentage": vector_store_stats["token_limit_analysis"]["percentage_hitting_limit"]
            }
        },
        "insights": {
            "character_limit_exists": "YES - Limited by max_tokens=500 setting",
            "typical_response_length": "300-2000 characters depending on complexity",
            "token_limit_impact": "Responses are truncated when they would exceed 500 tokens",
            "optimization_effectiveness": "Both systems stay within token limits while providing useful responses"
        },
        "recommendations": {
            "current_setting": "max_tokens=500 is appropriate for cost optimization",
            "for_longer_responses": "Increase max_tokens to 750-1000 if detailed responses needed",
            "for_cost_optimization": "Current 500 token limit provides good balance",
            "monitoring": "Track token limit hits to ensure response quality"
        }
    }
    
    # Save analysis
    with open("character_limit_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n🎯 CHARACTER LIMIT SUMMARY")
    print("=" * 50)
    print(f"📏 Max Tokens Setting: {analysis['configuration']['max_tokens_setting']}")
    print(f"🔤 JSON RAG Max Characters: {json_rag_stats['character_stats']['max']:,}")
    print(f"🔤 Vector Store Max Characters: {vector_store_stats['character_stats']['max']:,}")
    print(f"📊 JSON RAG Avg Characters: {json_rag_stats['character_stats']['avg']:.0f}")
    print(f"📊 Vector Store Avg Characters: {vector_store_stats['character_stats']['avg']:.0f}")
    print(f"🎯 JSON RAG Token Limit Hits: {json_rag_stats['token_limit_analysis']['responses_hitting_limit']}/187 ({json_rag_stats['token_limit_analysis']['percentage_hitting_limit']:.1f}%)")
    print(f"🎯 Vector Store Token Limit Hits: {vector_store_stats['token_limit_analysis']['responses_hitting_limit']}/187 ({vector_store_stats['token_limit_analysis']['percentage_hitting_limit']:.1f}%)")
    print(f"💡 Character per Token Ratio: ~{json_rag_stats['character_to_token_ratio']['avg_chars_per_token']:.1f} chars/token")
    
    print("\n✅ Detailed analysis saved to: character_limit_analysis.json")

if __name__ == "__main__":
    analyze_character_limits()
