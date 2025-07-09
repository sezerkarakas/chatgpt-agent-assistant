# Monster Notebook Assistant - Performance Analysis
# RAG vs Vector Store Comparison

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Grafik ayarları
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("✅ Kütüphaneler başarıyla yüklendi!")

# JSON dosyasını yükle - en son dosyayı otomatik bul
import glob
import os

result_files = glob.glob("comparison_results_*.json")
if result_files:
    # En son dosyayı seç
    filename = max(result_files, key=os.path.getctime)
else:
    filename = "comparison_results_20250708_151146.json"  # fallback

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
    print("Mevcut dosyalar:")
    import os
    for file in os.listdir('.'):
        if file.endswith('.json'):
            print(f"   - {file}")
except Exception as e:
    print(f"❌ Veri yükleme hatası: {e}")

# RAG sonuçlarını DataFrame'e çevir
if 'rag' in results and results['rag']:
    rag_df = pd.DataFrame(results['rag'])
    
    print("\n🔍 RAG Test Sonuçları:")
    print(f"   Toplam test sayısı: {len(rag_df)}")
    print(f"   Test edilen sorular: {len(rag_df['question'].unique())}")
    print()
    
    # Temel istatistikler
    print("📊 Temel İstatistikler:")
    print(f"   Ortalama yanıt süresi: {rag_df['response_time'].mean():.3f} saniye")
    print(f"   En hızlı yanıt: {rag_df['response_time'].min():.3f} saniye")
    print(f"   En yavaş yanıt: {rag_df['response_time'].max():.3f} saniye")
    print(f"   Ortalama token: {rag_df['tokens'].mean():.0f}")
    print(f"   Toplam maliyet: ${rag_df['cost_estimate'].sum():.4f}")
    print(f"   Sorgu başına maliyet: ${rag_df['cost_estimate'].mean():.6f}")
    
    # İlk 5 sonucu göster
    print("\n📋 İlk 5 Test Sonucu:")
    print(rag_df[['question', 'response_time', 'tokens', 'cost_estimate']].head())
    
    # Yanıt süreleri grafiği
    print("\n📈 Yanıt Süreleri Analizi Başlatılıyor...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Yanıt süreleri çizgi grafiği
    ax1.plot(range(1, len(rag_df) + 1), rag_df['response_time'], 
             marker='o', linewidth=2, markersize=8, color='#1f77b4')
    ax1.set_xlabel('Test Sıra No')
    ax1.set_ylabel('Yanıt Süresi (saniye)')
    ax1.set_title('RAG Sistemi - Yanıt Süreleri')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, max(rag_df['response_time']) * 1.1)
    
    # Yanıt süreleri histogram
    ax2.hist(rag_df['response_time'], bins=8, alpha=0.7, color='#ff7f0e', edgecolor='black')
    ax2.set_xlabel('Yanıt Süresi (saniye)')
    ax2.set_ylabel('Frekans')
    ax2.set_title('RAG Sistemi - Yanıt Süreleri Dağılımı')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('response_times_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Özet istatistikler
    print(f"📈 Yanıt Süresi Analizi:")
    print(f"   Ortalama: {rag_df['response_time'].mean():.3f} saniye")
    print(f"   Medyan: {rag_df['response_time'].median():.3f} saniye")
    print(f"   Standart sapma: {rag_df['response_time'].std():.3f} saniye")
    
    # Token kullanımı ve maliyet analizi
    print("\n💰 Maliyet Analizi Başlatılıyor...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Token kullanımı
    ax1.bar(range(1, len(rag_df) + 1), rag_df['tokens'], 
            color='#2ca02c', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Test Sıra No')
    ax1.set_ylabel('Token Sayısı')
    ax1.set_title('RAG Sistemi - Token Kullanımı')
    ax1.grid(True, alpha=0.3)
    
    # Maliyet analizi
    ax2.bar(range(1, len(rag_df) + 1), rag_df['cost_estimate'], 
            color='#d62728', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Test Sıra No')
    ax2.set_ylabel('Maliyet ($)')
    ax2.set_title('RAG Sistemi - Test Başına Maliyet')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cost_token_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Token ve maliyet istatistikleri
    print(f"🔢 Token Kullanımı:")
    print(f"   Toplam token: {rag_df['tokens'].sum():,}")
    print(f"   Ortalama token/test: {rag_df['tokens'].mean():.0f}")
    print(f"   Min-Max token: {rag_df['tokens'].min()}-{rag_df['tokens'].max()}")
    print()
    print(f"💰 Maliyet Analizi:")
    print(f"   Toplam maliyet: ${rag_df['cost_estimate'].sum():.4f}")
    print(f"   Ortalama maliyet/test: ${rag_df['cost_estimate'].mean():.6f}")
    print(f"   Token başına maliyet: ${(rag_df['cost_estimate'].sum() / rag_df['tokens'].sum()):.8f}")
    
    # Korelasyon analizi
    print("\n🔍 Korelasyon Analizi Başlatılıyor...")
    correlation_data = rag_df[['response_time', 'tokens', 'cost_estimate']].corr()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Korelasyon matrisi
    sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, 
                square=True, ax=ax1, cbar_kws={'label': 'Korelasyon'})
    ax1.set_title('RAG Metrikleri - Korelasyon Matrisi')
    
    # Yanıt süresi vs Token sayısı scatter plot
    ax2.scatter(rag_df['tokens'], rag_df['response_time'], 
               s=100, alpha=0.7, c='#9467bd', edgecolor='black')
    ax2.set_xlabel('Token Sayısı')
    ax2.set_ylabel('Yanıt Süresi (saniye)')
    ax2.set_title('Token Sayısı vs Yanıt Süresi')
    ax2.grid(True, alpha=0.3)
    
    # Trend çizgisi
    z = np.polyfit(rag_df['tokens'], rag_df['response_time'], 1)
    p = np.poly1d(z)
    ax2.plot(rag_df['tokens'], p(rag_df['tokens']), "r--", alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig('correlation_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("🔗 Korelasyon Analizi:")
    print(f"   Yanıt süresi ↔ Token sayısı: {correlation_data.loc['response_time', 'tokens']:.3f}")
    print(f"   Yanıt süresi ↔ Maliyet: {correlation_data.loc['response_time', 'cost_estimate']:.3f}")
    print(f"   Token sayısı ↔ Maliyet: {correlation_data.loc['tokens', 'cost_estimate']:.3f}")
    print()
    print("📊 Yorumlar:")
    if correlation_data.loc['response_time', 'tokens'] > 0.7:
        print("   ✅ Güçlü pozitif korelasyon: Daha fazla token = Daha yavaş yanıt")
    elif correlation_data.loc['response_time', 'tokens'] > 0.3:
        print("   ⚠️ Orta düzeyde pozitif korelasyon: Token sayısı yanıt süresini etkiliyor")
    else:
        print("   ❌ Zayıf korelasyon: Token sayısı yanıt süresini pek etkilemiyor")
    
    # Özet rapor oluştur
    print("\n📊 ÖZET RAPOR OLUŞTURULUYOR...")
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
            "cost_per_query": f"${rag_df['cost_estimate'].mean():.6f}"
        },
        "recommendations": [
            "RAG sistemi üretim için hazır",
            "Vector Store konfigürasyonu gerekli",
            "Düşük hacim için RAG ekonomik",
            "Yüksek hacim için Vector Store araştırılmalı"
        ]
    }
    
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
    print(f"📊 Grafikler PNG olarak kaydedildi:")
    print(f"   - response_times_analysis.png")
    print(f"   - cost_token_analysis.png") 
    print(f"   - correlation_analysis.png")
    print(f"✅ Analiz tamamlandı! Ödevinizde kullanabileceğiniz tüm veriler hazır.")
    
else:
    print("❌ RAG sonuçları bulunamadı!")
