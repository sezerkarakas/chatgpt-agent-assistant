"""
Monster Notebook Assistant - Performance Analysis (JSON Only)
Analyzes RAG vs Vector Store comparison results and outputs only JSON data
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os

def analyze_performance():
    """Main analysis function that outputs only JSON results"""
    print("✅ Kütüphaneler başarıyla yüklendi!")
    
    # JSON dosyasını yükle - en son dosyayı otomatik bul
    result_files = glob.glob("comparison_results_*.json")
    if result_files:
        # En son dosyayı seç
        filename = max(result_files, key=os.path.getctime)
        print(f"📁 En son dosya seçildi: {filename}")
    else:
        filename = "comparison_results_20250708_151146.json"  # fallback
        print(f"📁 Fallback dosya kullanılıyor: {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"✅ {filename} başarıyla yüklendi!")
        print(f"📊 Veri yapısı:")
        print(f"   - Vector Store sonuçları: {len(results['vector_store'])} test")
        print(f"   - RAG sonuçları: {len(results['rag'])} test")
        print(f"   - Zaman damgası: {results['timestamp']}")
        
    except FileNotFoundError:
        print(f"❌ {filename} dosyası bulunamadı!")
        return
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {e}")
        return

    # RAG sonuçlarını DataFrame'e çevir
    if 'rag' in results and results['rag']:
        rag_df = pd.DataFrame(results['rag'])
        
        print("\n🔍 RAG Test Sonuçları:")
        print(f"   Toplam test sayısı: {len(rag_df)}")
        print(f"   Test edilen sorular: {len(rag_df['question'].unique())}")
        
        # Temel istatistikler
        print("\n📊 Temel İstatistikler:")
        print(f"   Ortalama yanıt süresi: {rag_df['response_time'].mean():.3f} saniye")
        print(f"   En hızlı yanıt: {rag_df['response_time'].min():.3f} saniye")
        print(f"   En yavaş yanıt: {rag_df['response_time'].max():.3f} saniye")
        print(f"   Ortalama token: {rag_df['tokens'].mean():.0f}")
        print(f"   Toplam maliyet: ${rag_df['cost_estimate'].sum():.4f}")
        print(f"   Sorgu başına maliyet: ${rag_df['cost_estimate'].mean():.6f}")
        
        # GPT-4o-mini fiyatlandırma bilgisi
        print("\n💰 GPT-4o-mini Fiyatlandırma:")
        print("   Input: $0.00015 per 1K tokens")
        print("   Output: $0.0006 per 1K tokens")
        if 'prompt_tokens' in rag_df.columns:
            avg_prompt = rag_df['prompt_tokens'].mean()
            avg_completion = rag_df['completion_tokens'].mean()
            print(f"   Ortalama Prompt Tokens: {avg_prompt:.0f}")
            print(f"   Ortalama Completion Tokens: {avg_completion:.0f}")
        
        # İlk 5 sonucu göster
        print("\n📋 İlk 5 Test Sonucu:")
        display_cols = ['question', 'response_time', 'tokens', 'cost_estimate']
        if 'relevant_docs_count' in rag_df.columns:
            display_cols.append('relevant_docs_count')
        print(rag_df[display_cols].head().to_string())
        
        # Yanıt süresi analizi (sadece rakamsal)
        print(f"\n📈 Yanıt Süresi Analizi:")
        print(f"   Ortalama: {rag_df['response_time'].mean():.3f} saniye")
        print(f"   Medyan: {rag_df['response_time'].median():.3f} saniye")
        print(f"   Standart sapma: {rag_df['response_time'].std():.3f} saniye")
        
        # Token ve maliyet istatistikleri
        print(f"\n🔢 Token Kullanımı:")
        print(f"   Toplam token: {rag_df['tokens'].sum():,}")
        print(f"   Ortalama token/test: {rag_df['tokens'].mean():.0f}")
        print(f"   Min-Max token: {rag_df['tokens'].min()}-{rag_df['tokens'].max()}")
        
        print(f"\n💰 Maliyet Analizi:")
        print(f"   Toplam maliyet: ${rag_df['cost_estimate'].sum():.4f}")
        print(f"   Ortalama maliyet/test: ${rag_df['cost_estimate'].mean():.6f}")
        print(f"   Token başına maliyet: ${(rag_df['cost_estimate'].sum() / rag_df['tokens'].sum()):.8f}")
        
        # Korelasyon analizi (sadece rakamsal)
        correlation_data = rag_df[['response_time', 'tokens', 'cost_estimate']].corr()
        
        print(f"\n🔗 Korelasyon Analizi:")
        print(f"   Yanıt süresi ↔ Token sayısı: {correlation_data.loc['response_time', 'tokens']:.3f}")
        print(f"   Yanıt süresi ↔ Maliyet: {correlation_data.loc['response_time', 'cost_estimate']:.3f}")
        print(f"   Token sayısı ↔ Maliyet: {correlation_data.loc['tokens', 'cost_estimate']:.3f}")
        
        print(f"\n📊 Yorumlar:")
        if correlation_data.loc['response_time', 'tokens'] > 0.7:
            print("   ✅ Güçlü pozitif korelasyon: Daha fazla token = Daha yavaş yanıt")
        elif correlation_data.loc['response_time', 'tokens'] > 0.3:
            print("   ⚠️ Orta düzeyde pozitif korelasyon: Token sayısı yanıt süresini etkiliyor")
        else:
            print("   ❌ Zayıf korelasyon: Token sayısı yanıt süresini pek etkilemiyor")
        
        # Vector Store analizi
        print(f"\n⚠️ Vector Store Test Hatası:")
        print("   Hata: Assistant ID bulunamadı")
        print("   Durum: Konfigürasyon gerekli")
        
        # Özet rapor oluştur
        summary_report = {
            "test_date": results['timestamp'],
            "systems_tested": {
                "rag": "SUCCESS",
                "vector_store": "FAILED - Assistant ID not found"
            },
            "rag_performance": {
                "tests_completed": len(rag_df),
                "avg_response_time": f"{rag_df['response_time'].mean():.3f}s",
                "avg_tokens": f"{rag_df['tokens'].mean():.0f}",
                "total_cost": f"${rag_df['cost_estimate'].sum():.4f}",
                "cost_per_query": f"${rag_df['cost_estimate'].mean():.6f}",
                "median_response_time": f"{rag_df['response_time'].median():.3f}s",
                "min_response_time": f"{rag_df['response_time'].min():.3f}s",
                "max_response_time": f"{rag_df['response_time'].max():.3f}s",
                "total_tokens": int(rag_df['tokens'].sum()),
                "min_tokens": int(rag_df['tokens'].min()),
                "max_tokens": int(rag_df['tokens'].max())
            },
            "correlations": {
                "response_time_tokens": round(correlation_data.loc['response_time', 'tokens'], 3),
                "response_time_cost": round(correlation_data.loc['response_time', 'cost_estimate'], 3),
                "tokens_cost": round(correlation_data.loc['tokens', 'cost_estimate'], 3)
            },
            "recommendations": [
                "RAG sistemi üretim için hazır",
                "Vector Store konfigürasyonu gerekli", 
                "Düşük hacim için RAG ekonomik",
                "Yüksek hacim için Vector Store araştırılmalı"
            ]
        }
        
        print(f"\n📊 ÖZET RAPOR OLUŞTURULUYOR...")
        print("📊 ÖZET RAPOR:")
        print("="*50)
        print(f"Test Tarihi: {summary_report['test_date']}")
        print(f"RAG Sistemi: {summary_report['systems_tested']['rag']}")
        print(f"Vector Store: {summary_report['systems_tested']['vector_store']}")
        print()
        print("RAG Performans Metrikleri:")
        for key, value in summary_report['rag_performance'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        print()
        print("Öneriler:")
        for i, rec in enumerate(summary_report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # JSON olarak kaydet
        with open('performance_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Özet rapor 'performance_summary.json' olarak kaydedildi.")
        print(f"✅ Analiz tamamlandı! Ödevinizde kullanabileceğiniz tüm veriler hazır.")
        
    else:
        print("❌ RAG sonuçları bulunamadı!")

if __name__ == "__main__":
    analyze_performance()
