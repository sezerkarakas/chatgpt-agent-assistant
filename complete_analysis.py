"""
Monster Notebook Assistant - Complete Performance Analysis
Analyzes both RAG and Vector Store comparison results
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os

def analyze_complete_performance():
    """Complete analysis function that handles both RAG and Vector Store results"""
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
    rag_df = None
    if 'rag' in results and results['rag']:
        rag_df = pd.DataFrame(results['rag'])
        
        print("\n🔍 RAG Test Sonuçları:")
        print(f"   Toplam test sayısı: {len(rag_df)}")
        print(f"   Test edilen sorular: {len(rag_df['question'].unique())}")
        
        # Temel istatistikler
        print("\n📊 RAG Temel İstatistikler:")
        print(f"   Ortalama yanıt süresi: {rag_df['response_time'].mean():.3f} saniye")
        print(f"   En hızlı yanıt: {rag_df['response_time'].min():.3f} saniye")
        print(f"   En yavaş yanıt: {rag_df['response_time'].max():.3f} saniye")
        print(f"   Ortalama token: {rag_df['tokens'].mean():.0f}")
        print(f"   Toplam maliyet: ${rag_df['cost_estimate'].sum():.4f}")
        print(f"   Sorgu başına maliyet: ${rag_df['cost_estimate'].mean():.6f}")
        
    else:
        print("\n❌ RAG sonuçları bulunamadı!")

    # Vector Store sonuçlarını DataFrame'e çevir
    vs_df = None
    if 'vector_store' in results and results['vector_store']:
        vs_df = pd.DataFrame(results['vector_store'])
        
        print("\n🔍 Vector Store Test Sonuçları:")
        print(f"   Toplam test sayısı: {len(vs_df)}")
        print(f"   Test edilen sorular: {len(vs_df['question'].unique())}")
        
        # Temel istatistikler
        print("\n📊 Vector Store Temel İstatistikler:")
        print(f"   Ortalama yanıt süresi: {vs_df['response_time'].mean():.3f} saniye")
        print(f"   En hızlı yanıt: {vs_df['response_time'].min():.3f} saniye")
        print(f"   En yavaş yanıt: {vs_df['response_time'].max():.3f} saniye")
        print(f"   Ortalama token: {vs_df['tokens'].mean():.0f}")
        print(f"   Toplam maliyet: ${vs_df['cost_estimate'].sum():.4f}")
        print(f"   Sorgu başına maliyet: ${vs_df['cost_estimate'].mean():.6f}")
        
    else:
        print("\n❌ Vector Store sonuçları bulunamadı!")

    # Karşılaştırma analizi
    if rag_df is not None and vs_df is not None:
        print("\n🏆 KARŞILAŞTIRMA ANALİZİ:")
        
        # Hız karşılaştırması
        rag_avg_time = rag_df['response_time'].mean()
        vs_avg_time = vs_df['response_time'].mean()
        
        print(f"\n⚡ Hız Karşılaştırması:")
        print(f"   RAG Ortalama: {rag_avg_time:.3f} saniye")
        print(f"   Vector Store Ortalama: {vs_avg_time:.3f} saniye")
        
        if rag_avg_time < vs_avg_time:
            speed_diff = ((vs_avg_time - rag_avg_time) / vs_avg_time) * 100
            print(f"   🏆 RAG {speed_diff:.1f}% daha hızlı!")
        else:
            speed_diff = ((rag_avg_time - vs_avg_time) / rag_avg_time) * 100
            print(f"   🏆 Vector Store {speed_diff:.1f}% daha hızlı!")
        
        # Maliyet karşılaştırması
        rag_avg_cost = rag_df['cost_estimate'].mean()
        vs_avg_cost = vs_df['cost_estimate'].mean()
        
        print(f"\n💰 Maliyet Karşılaştırması:")
        print(f"   RAG Ortalama: ${rag_avg_cost:.6f}/sorgu")
        print(f"   Vector Store Ortalama: ${vs_avg_cost:.6f}/sorgu")
        
        if rag_avg_cost < vs_avg_cost:
            cost_diff = ((vs_avg_cost - rag_avg_cost) / vs_avg_cost) * 100
            print(f"   🏆 RAG {cost_diff:.1f}% daha ekonomik!")
        else:
            cost_diff = ((rag_avg_cost - vs_avg_cost) / rag_avg_cost) * 100
            print(f"   🏆 Vector Store {cost_diff:.1f}% daha ekonomik!")
        
        # Token kullanımı karşılaştırması
        rag_avg_tokens = rag_df['tokens'].mean()
        vs_avg_tokens = vs_df['tokens'].mean()
        
        print(f"\n🔢 Token Kullanımı:")
        print(f"   RAG Ortalama: {rag_avg_tokens:.0f} token/sorgu")
        print(f"   Vector Store Ortalama: {vs_avg_tokens:.0f} token/sorgu")

    # Özet rapor oluştur
    summary_report = {
        "test_date": results['timestamp'],
        "systems_tested": {
            "rag": "SUCCESS" if rag_df is not None else "FAILED",
            "vector_store": "SUCCESS" if vs_df is not None else "FAILED"
        }
    }
    
    if rag_df is not None:
        summary_report["rag_performance"] = {
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
        }
    
    if vs_df is not None:
        summary_report["vector_store_performance"] = {
            "tests_completed": len(vs_df),
            "avg_response_time": f"{vs_df['response_time'].mean():.3f}s",
            "avg_tokens": f"{vs_df['tokens'].mean():.0f}",
            "total_cost": f"${vs_df['cost_estimate'].sum():.4f}",
            "cost_per_query": f"${vs_df['cost_estimate'].mean():.6f}",
            "median_response_time": f"{vs_df['response_time'].median():.3f}s",
            "min_response_time": f"{vs_df['response_time'].min():.3f}s",
            "max_response_time": f"{vs_df['response_time'].max():.3f}s",
            "total_tokens": int(vs_df['tokens'].sum()),
            "min_tokens": int(vs_df['tokens'].min()),
            "max_tokens": int(vs_df['tokens'].max())
        }
    
    # Karşılaştırma metrikleri
    if rag_df is not None and vs_df is not None:
        summary_report["comparison"] = {
            "speed_winner": "RAG" if rag_df['response_time'].mean() < vs_df['response_time'].mean() else "Vector Store",
            "cost_winner": "RAG" if rag_df['cost_estimate'].mean() < vs_df['cost_estimate'].mean() else "Vector Store",
            "speed_difference_percent": abs((rag_df['response_time'].mean() - vs_df['response_time'].mean()) / max(rag_df['response_time'].mean(), vs_df['response_time'].mean()) * 100),
            "cost_difference_percent": abs((rag_df['cost_estimate'].mean() - vs_df['cost_estimate'].mean()) / max(rag_df['cost_estimate'].mean(), vs_df['cost_estimate'].mean()) * 100)
        }
    
    summary_report["recommendations"] = [
        "RAG sistemi üretim için hazır" if rag_df is not None else "RAG sistemi test edilemedi",
        "Vector Store sistemi test edildi" if vs_df is not None else "Vector Store konfigürasyonu gerekli",
        "Düşük hacim için RAG ekonomik" if rag_df is not None else "RAG maliyet analizi yapılamadı",
        "Yüksek hacim için Vector Store araştırılmalı" if vs_df is not None else "Vector Store analizi yapılamadı"
    ]
    
    print(f"\n📊 ÖZET RAPOR:")
    print("="*50)
    print(f"Test Tarihi: {summary_report['test_date']}")
    print(f"RAG Sistemi: {summary_report['systems_tested']['rag']}")
    print(f"Vector Store: {summary_report['systems_tested']['vector_store']}")
    
    if "rag_performance" in summary_report:
        print("\nRAG Performans Metrikleri:")
        for key, value in summary_report['rag_performance'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    if "vector_store_performance" in summary_report:
        print("\nVector Store Performans Metrikleri:")
        for key, value in summary_report['vector_store_performance'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    if "comparison" in summary_report:
        print("\nKarşılaştırma:")
        comp = summary_report['comparison']
        print(f"   Hız Galibi: {comp['speed_winner']}")
        print(f"   Maliyet Galibi: {comp['cost_winner']}")
        print(f"   Hız Farkı: {comp['speed_difference_percent']:.1f}%")
        print(f"   Maliyet Farkı: {comp['cost_difference_percent']:.1f}%")
    
    print("\nÖneriler:")
    for i, rec in enumerate(summary_report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # JSON olarak kaydet
    with open('complete_performance_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Tam özet rapor 'complete_performance_summary.json' olarak kaydedildi.")
    print(f"✅ Tam analiz tamamlandı! Her iki sistem de test edildi.")

if __name__ == "__main__":
    analyze_complete_performance()
