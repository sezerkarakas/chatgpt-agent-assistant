"""
Monster Notebook Technical Assistant - Performance Comparison Tool
Compares RAG vs Vector Store implementations for cost, speed, and quality
"""

import os
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Tuple

# Test questions for comparison
TEST_QUESTIONS = [
    "Monster notebook modellerini listeleyebilir misin?",
    "Garantili ürün nasıl servise gönderilir?",
    "Kargo ücreti kim tarafından karşılanır?",
    "Teknik servis süreci ne kadar sürer?",
    "Servis takip numarası nasıl alınır?",
    "Hangi kargo firması kullanılmalı?",
    "Veri yedeği neden önemli?",
    "Servis adresi nedir?",
    "Arıza tespit ücreti alınır mı?",
    "WhatsApp üzerinden destek alabilir miyim?"
]

class PerformanceComparison:
    def __init__(self):
        self.results = {
            'vector_store': [],
            'rag': [],
            'timestamp': datetime.now().isoformat()
        }
        
    def test_vector_store_system(self) -> List[Dict]:
        """Test Vector Store alternative (Chat Completions without Assistant)"""
        print("🔍 Vector Store alternatifi test ediliyor...")
        
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            import os
            
            # Load environment variables
            load_dotenv()
            
            client = OpenAI()
            
            # Load documents for context (simulating vector store)
            documents_text = ""
            document_files = [
                'documents/Technical Service Information.txt',
                'documents/Monster Model List.txt', 
                'documents/Problems and Solutions.txt',
                'documents/Technical Service Office.txt'
            ]
            
            for file_path in document_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        documents_text += f"\n\n=== {file_path} ===\n{file.read()}"
                except FileNotFoundError:
                    continue
            
            # Load system prompt
            try:
                with open('gpt_prompt_v4.md', 'r', encoding='utf-8') as file:
                    system_prompt = file.read()
            except FileNotFoundError:
                system_prompt = "Sen Monster Notebook teknik destek asistanısın."
            
            results = []
            
            for i, question in enumerate(TEST_QUESTIONS, 1):
                print(f"  📝 Test {i}/{len(TEST_QUESTIONS)}: {question[:50]}...")
                
                start_time = time.time()
                
                # Create messages with full context (simulating vector store)
                messages = [
                    {"role": "system", "content": f"{system_prompt}\n\nKnowledge Base:\n{documents_text}"},
                    {"role": "user", "content": question}
                ]
                
                # Generate response
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                end_time = time.time()
                
                # Calculate cost (similar to RAG system)
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                # GPT-4o-mini pricing
                input_cost = (prompt_tokens / 1000) * 0.00015
                output_cost = (completion_tokens / 1000) * 0.0006
                total_cost = input_cost + output_cost
                
                results.append({
                    'question': question,
                    'response': response.choices[0].message.content,
                    'response_time': end_time - start_time,
                    'method': 'vector_store_alternative',
                    'tokens': total_tokens,
                    'cost_estimate': total_cost,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens
                })
                
                # Small delay between requests
                time.sleep(0.5)
                
            print(f"✅ Vector Store alternatifi test tamamlandı - {len(results)} yanıt alındı")
            return results
            
        except Exception as e:
            print(f"❌ Vector Store alternatifi test hatası: {e}")
            return []
    
    def test_rag_system(self) -> List[Dict]:
        """Test RAG implementation"""
        print("🔍 RAG sistemi test ediliyor...")
        
        try:
            # Import RAG system
            import sys
            sys.path.append('.')
            
            # Import the actual RAG system
            from dotenv import load_dotenv
            load_dotenv()
            
            # Import RAG classes
            import importlib.util
            spec = importlib.util.spec_from_file_location("rag_module", "chat-assistant-rag.py")
            rag_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rag_module)
            
            # Initialize RAG system
            rag_system = rag_module.RAGSystem()
            
            results = []
            
            for i, question in enumerate(TEST_QUESTIONS, 1):
                print(f"  📝 Test {i}/{len(TEST_QUESTIONS)}: {question[:50]}...")
                
                try:
                    # Get actual RAG response
                    result = rag_system.generate_response(question)
                    
                    results.append({
                        'question': question,
                        'response': result['response'],
                        'response_time': result['total_time'],
                        'method': 'rag',
                        'tokens': result['total_tokens'],
                        'cost_estimate': result['cost_estimate'],  # Use actual cost from RAG system
                        'search_time': result['search_time'],
                        'generation_time': result['generation_time'],
                        'relevant_docs_count': result['relevant_docs_count'],
                        'prompt_tokens': result['prompt_tokens'],
                        'completion_tokens': result['completion_tokens']
                    })
                    
                    # Small delay between requests
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    ⚠️ Test {i} hatası: {e}")
                    continue
                
            print(f"✅ RAG test tamamlandı - {len(results)} yanıt alındı")
            return results
            
        except Exception as e:
            print(f"❌ RAG test hatası: {e}")
            return []
    
    def run_comparison(self) -> Dict:
        """Run full comparison between both systems"""
        print("🚀 Performance Comparison başlatılıyor...\n")
        
        # Test both systems
        vector_results = self.test_vector_store_system()
        rag_results = self.test_rag_system()
        
        # Store results
        self.results['vector_store'] = vector_results
        self.results['rag'] = rag_results
        
        # Generate comparison report
        report = self.generate_report()
        
        # Save results
        self.save_results()
        
        return report
    
    def generate_report(self) -> Dict:
        """Generate detailed comparison report"""
        print("\n📊 Rapor oluşturuluyor...")
        
        vector_results = self.results['vector_store']
        rag_results = self.results['rag']
        
        if not vector_results or not rag_results:
            # If one of the tests failed, create a simplified report
            if not vector_results and rag_results:
                return {
                    "error": "Vector Store test failed, only RAG results available",
                    "rag_only_results": {
                        "test_count": len(rag_results),
                        "avg_response_time": sum(r['response_time'] for r in rag_results) / len(rag_results),
                        "avg_tokens": sum(r['tokens'] for r in rag_results) / len(rag_results),
                        "total_cost": sum(r['cost_estimate'] for r in rag_results)
                    }
                }
            else:
                return {"error": "Insufficient data for comparison"}
        
        # Calculate metrics
        vector_times = [r['response_time'] for r in vector_results]
        rag_times = [r['response_time'] for r in rag_results]
        
        rag_tokens = [r['tokens'] for r in rag_results if isinstance(r['tokens'], (int, float))]
        rag_costs = [r['cost_estimate'] for r in rag_results if isinstance(r['cost_estimate'], (int, float))]
        
        report = {
            'summary': {
                'test_count': len(TEST_QUESTIONS),
                'vector_store_success': len(vector_results),
                'rag_success': len(rag_results)
            },
            'speed_comparison': {
                'vector_store': {
                    'avg_response_time': statistics.mean(vector_times),
                    'min_response_time': min(vector_times),
                    'max_response_time': max(vector_times),
                    'median_response_time': statistics.median(vector_times)
                },
                'rag': {
                    'avg_response_time': statistics.mean(rag_times),
                    'min_response_time': min(rag_times),
                    'max_response_time': max(rag_times),
                    'median_response_time': statistics.median(rag_times)
                }
            },
            'cost_analysis': {
                'vector_store': {
                    'pricing_model': 'Assistant API - Fixed monthly cost',
                    'token_visibility': 'Limited',
                    'cost_predictability': 'High'
                },
                'rag': {
                    'avg_tokens_per_query': statistics.mean(rag_tokens) if rag_tokens else 0,
                    'total_estimated_cost': sum(rag_costs) if rag_costs else 0,
                    'cost_per_query': statistics.mean(rag_costs) if rag_costs else 0,
                    'pricing_model': 'Pay-per-token',
                    'cost_predictability': 'Variable'
                }
            },
            'winner_analysis': self.determine_winners(vector_times, rag_times, rag_costs)
        }
        
        return report
    
    def determine_winners(self, vector_times: List[float], rag_times: List[float], rag_costs: List[float]) -> Dict:
        """Determine winners in each category"""
        winners = {}
        
        # Speed winner
        vector_avg = statistics.mean(vector_times)
        rag_avg = statistics.mean(rag_times)
        
        if rag_avg < vector_avg:
            winners['speed'] = {
                'winner': 'RAG',
                'difference': f"{((vector_avg - rag_avg) / vector_avg * 100):.1f}% faster",
                'vector_avg': f"{vector_avg:.2f}s",
                'rag_avg': f"{rag_avg:.2f}s"
            }
        else:
            winners['speed'] = {
                'winner': 'Vector Store',
                'difference': f"{((rag_avg - vector_avg) / rag_avg * 100):.1f}% faster",
                'vector_avg': f"{vector_avg:.2f}s",
                'rag_avg': f"{rag_avg:.2f}s"
            }
        
        # Cost winner (theoretical)
        if rag_costs:
            avg_rag_cost = statistics.mean(rag_costs)
            winners['cost'] = {
                'winner': 'Depends on usage volume',
                'rag_cost_per_query': f"${avg_rag_cost:.6f}",
                'vector_store_cost': 'Fixed monthly fee',
                'note': 'RAG better for low volume, Vector Store better for high volume'
            }
        
        # Quality winner (subjective analysis needed)
        winners['quality'] = {
            'winner': 'Needs manual evaluation',
            'note': 'Both use same knowledge base, quality depends on implementation'
        }
        
        return winners
    
    def save_results(self):
        """Save results to JSON file"""
        filename = f"comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"💾 Sonuçlar kaydedildi: {filename}")
    
    def print_report(self, report: Dict):
        """Print formatted comparison report"""
        print("\n" + "="*80)
        print("🏆 MONSTER NOTEBOOK ASSISTANT - PERFORMANCE COMPARISON REPORT")
        print("="*80)
        
        if "error" in report:
            print(f"\n⚠️  UYARI: {report['error']}")
            
            if "rag_only_results" in report:
                rag = report["rag_only_results"]
                print(f"\n📊 RAG SONUÇLARI:")
                print(f"Test Sayısı: {rag['test_count']}")
                print(f"Ortalama Yanıt Süresi: {rag['avg_response_time']:.2f} saniye")
                print(f"Ortalama Token: {rag['avg_tokens']:.0f}")
                print(f"Toplam Maliyet: ${rag['total_cost']:.4f}")
                print(f"\n✅ RAG sistemi başarıyla test edildi!")
                print(f"Vector Store testi için API key ve assistant ID kontrol edilmeli.")
            return
        
        print(f"\n📈 ÖZET:")
        print(f"Test Sayısı: {report['summary']['test_count']}")
        print(f"Vector Store Başarı: {report['summary']['vector_store_success']}/{report['summary']['test_count']}")
        print(f"RAG Başarı: {report['summary']['rag_success']}/{report['summary']['test_count']}")
        
        print(f"\n⚡ HIZ KARŞILAŞTIRMASI:")
        speed = report['speed_comparison']
        print(f"Vector Store - Ortalama: {speed['vector_store']['avg_response_time']:.2f}s")
        print(f"RAG - Ortalama: {speed['rag']['avg_response_time']:.2f}s")
        print(f"Hız Galibi: {report['winner_analysis']['speed']['winner']}")
        print(f"Fark: {report['winner_analysis']['speed']['difference']}")
        
        print(f"\n💰 MALİYET ANALİZİ:")
        cost = report['cost_analysis']
        print(f"Vector Store: {cost['vector_store']['pricing_model']}")
        print(f"RAG: {cost['rag']['pricing_model']}")
        if 'cost' in report['winner_analysis']:
            print(f"Maliyet: {report['winner_analysis']['cost']['note']}")
        
        print(f"\n🏅 GENEL DEĞERLENDİRME:")
        print(f"Hız: {report['winner_analysis']['speed']['winner']}")
        print(f"Maliyet: {report['winner_analysis']['cost']['winner'] if 'cost' in report['winner_analysis'] else 'Değerlendirme gerekli'}")
        print(f"Kalite: {report['winner_analysis']['quality']['winner']}")
        
        print("\n" + "="*80)

def main():
    """Main comparison function"""
    print("🤖 Monster Notebook Assistant - Performance Comparison Tool")
    print("Bu araç RAG ve Vector Store implementasyonlarını karşılaştırır.\n")
    
    comparison = PerformanceComparison()
    
    try:
        report = comparison.run_comparison()
        comparison.print_report(report)
        
        print(f"\n✅ Karşılaştırma tamamlandı!")
        print(f"Detaylı sonuçlar JSON dosyasına kaydedildi.")
        
    except Exception as e:
        print(f"❌ Karşılaştırma hatası: {e}")

if __name__ == "__main__":
    main()
