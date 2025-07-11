# 🤖 Monster Notebook RAG Chatbot

Monster Notebook müşteri desteği için geliştirilmiş **LangChain tabanlı RAG (Retrieval-Augmented Generation)** sistemi. Müşteri sorularını otomatik olarak cevaplayabilen yapay zeka chatbot.

## 🎯 Proje Özeti

Bu proje, Monster Notebook'un teknik destek süreçlerini otomatikleştirmek için geliştirilmiştir. **187 adet test sorusu** ile %100 başarı oranı elde edilmiş, production-ready bir RAG sistemidir.

### ✨ Temel Özellikler

- 🔍 **Akıllı Arama**: FAISS vectorstore ile hızlı ve doğru bilgi arama
- 🎯 **Yüksek Doğruluk**: %100 başarı oranı (187/187 test)
- 💰 **Düşük Maliyet**: $0.13/187 soru (~10.6x daha ekonomik)
- 🚀 **Hızlı Yanıt**: Ortalama 6 saniye
- 🇹🇷 **Türkçe Optimizasyonu**: Monster terminolojisi ile uyumlu
- 📊 **Kapsamlı Test**: Otomatik batch testing framework

## 🏗️ Sistem Mimarisi

### 🔧 Teknoloji Stack

| Bileşen | Teknoloji | Versiyon |
|---------|-----------|----------|
| **AI Framework** | LangChain | 0.3.26 |
| **Language Model** | OpenAI GPT-4o-mini | Latest |
| **Vector Database** | FAISS | Latest |
| **Embeddings** | OpenAI text-embedding-ada-002 | Latest |
| **Programming Language** | Python | 3.10.11 |
| **Environment** | Virtual Environment | .venv |

### 📊 Veri Tabanı

- **208 doküman** (chunking yapılmamış, bütünlük korunmuş)
- **13 JSON dosyası** kategorize teknik bilgiler ile
- **187 soru-cevap çifti** test verisi
- **11 kategori**: Donanım, yazılım, ağ, performans vs.

## 🚀 Kurulum

### 1️⃣ Gereksinimler

```bash
Python 3.10+
OpenAI API Key
Git
```

### 2️⃣ Repo'yu Clone Edin

```bash
git clone https://github.com/sezerkarakas/chatgpt-agent-assistant.git
cd chatgpt-agent-assistant
git checkout arda_rag_v2
```

### 3️⃣ Virtual Environment Kurulumu

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 4️⃣ Bağımlılıkları Yükleyin

```bash
pip install langchain==0.3.26
pip install langchain-openai
pip install langchain-community
pip install faiss-cpu
pip install python-dotenv
```

### 5️⃣ Environment Variables

`.env` dosyası oluşturun:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 6️⃣ Vectorstore Oluşturun

```bash
python build_vectorstore.py
```

## 📂 Proje Yapısı

```
chatgpt-agent-assistant/
├── 📁 documents/              # Kaynak dokümanlar
│   └── json/                  # JSON formatında Q&A verileri
│       ├── baglant_ag_sorunlar.json
│       ├── donanim_ekran_panel.json
│       └── ...
├── 📁 vectorstore/            # FAISS vectorstore
│   ├── faiss_index/           # FAISS index dosyaları
│   └── metadata.json          # Vectorstore metadata
├── 📁 static/                 # Web arayüzü dosyaları
├── 🐍 simple_rag_chatbot.py   # Ana chatbot (RECOMMENDED)
├── 🔧 build_vectorstore.py    # Vectorstore oluşturucu
├── 🧪 batch_test_questions.py # Kapsamlı test sistemi
├── 📊 veriler.json            # Test veri seti
├── 📋 requirements.txt        # Python bağımlılıkları
└── 📖 README.md              # Bu dosya
```

## 🎮 Kullanım

### 🤖 Temel Chatbot

```bash
python simple_rag_chatbot.py
```

**Örnek Kullanım:**
```
👤 Siz: Bilgisayarımda Windows kurulum problemi yaşıyorum
🤖 Asistan: FreeDOS olarak satın alınmış cihazınızı kullanabilmek için...
```

### 🧪 Batch Testing

```bash
python batch_test_questions.py
```

**Test Çıktısı:**
- `rag_test_results_YYYYMMDD_HHMMSS.json` - Detaylı sonuçlar
- `test_summary_YYYYMMDD_HHMMSS.txt` - Özet rapor

### 🔧 Vectorstore Yeniden Oluşturma

```bash
python build_vectorstore.py
```

## 📊 Performans Metrikleri

### ✅ Test Sonuçları (Son Test: 11.07.2025)

| Metrik | Değer |
|--------|-------|
| **Toplam Test Sorusu** | 187 |
| **Başarı Oranı** | %100 |
| **Ortalama Yanıt Uzunluğu** | 1.49x daha detaylı |
| **Test Süresi** | 19.8 dakika |
| **Maliyet** | $0.13 (3.5 TL) |

### 💰 Maliyet Analizi

| Yaklaşım | Maliyet (187 soru) | Ölçeklenebilirlik |
|----------|-------------------|-------------------|
| **RAG Sistemi** | $0.13 | ✅ Çok iyi |
| **Sadece OpenAI API** | $1.38 | ❌ Pahalı (10.6x) |

## 🔍 Dosya Açıklamaları

### 🎯 Ana Dosyalar

#### `simple_rag_chatbot.py` ⭐ **[RECOMMENDED]**
- **Amaç**: Production-ready RAG chatbot
- **Özellikler**: 
  - Optimized chunking (disabled for Q&A integrity)
  - Conversation memory
  - Turkish language optimization
  - Error handling

#### `build_vectorstore.py`
- **Amaç**: FAISS vectorstore oluşturma
- **Özellikler**:
  - JSON document processing
  - Batch processing (50 documents)
  - Metadata extraction
  - Category mapping

#### `batch_test_questions.py`
- **Amaç**: Kapsamlı sistem testi
- **Özellikler**:
  - 187 sorunun otomatik testi
  - Accuracy calculation
  - Cost tracking
  - JSON reporting

### 🗂️ Veri Kategorileri

```
documents/json/ klasöründe:
├── 🌐 baglant_ag_sorunlar.json      # Ağ ve bağlantı sorunları
├── 📺 donanim_ekran_panel.json     # Ekran ve panel problemleri
├── 🔋 donanim_guc_batarya.json     # Güç ve batarya sorunları
├── ⌨️ donanim_klavye_touchpad.json # Klavye ve touchpad
├── 🔩 donanim_mentese_kasa.json    # Menteşe ve kasa problemleri
├── 🔌 donanim_usb_portlar.json     # USB port sorunları
├── 💻 kurulum_ve_yazlm_sorunlar.json # Yazılım kurulum
├── ⚡ performans_sorunlar.json     # Performans optimizasyonu
├── 🔊 ses_hoparlor_problemleri.json # Ses sistemleri
├── 📋 Monster Model List.json       # Model listesi
├── 🛠️ Technical Service Information.json # Servis bilgileri
└── 🏢 Technical Service Office.json # Servis lokasyonları
```

## 🎯 Kullanım Senaryoları

### 👥 Müşteri Desteği
- Windows kurulum sorunları
- Donanım arızaları (ekran, klavye, batarya)
- Performans optimizasyonu
- Sürücü kurulumları

### 🔧 Teknik Destek
- BIOS ayarları
- Ekran kartı problemleri
- Isınma sorunları
- Garanti kapsamı

### 📞 Çağrı Merkezi
- İlk seviye destek otomasyonu
- Sık sorulan soruların yanıtlanması
- Teknik personel için referans

## 🚀 Gelecek Geliştirmeler

### 🌟 Planlanmış Özellikler
- [ ] Web arayüzü entegrasyonu (FastAPI)
- [ ] Real-time learning capability
- [ ] Multi-language support
- [ ] Voice interaction
- [ ] Image/video content support

### 📈 Ölçeklenebilirlik
- [ ] Kubernetes deployment
- [ ] Database integration
- [ ] A/B testing framework
- [ ] Analytics dashboard
- [ ] Customer satisfaction tracking

## 🔧 Geliştirici Notları

### 🎯 Optimizasyonlar Yapıldı

1. **Chunking Devre Dışı**: Q&A çiftlerinin bütünlüğü korundu
2. **Türkçe Prompting**: Monster terminolojisi entegrasyonu
3. **Memory Management**: 5 etkileşim hafızası
4. **Error Handling**: Kapsamlı hata yönetimi
5. **Batch Processing**: Büyük dataset'ler için optimize

### ⚠️ Bilinen Limitasyonlar

- OpenAI API rate limits
- FAISS memory usage (büyük dataset'lerde)
- Turkish language context window limitations

## 📞 Destek

### 🐛 Bug Reports
GitHub Issues kullanarak bug raporu oluşturun.

### 💡 Feature Requests
Yeni özellik önerileri için GitHub Discussions kullanın.

### 📧 İletişim
- **Email**: destek@monsternotebook.com
- **Phone**: 0850 255 11 11

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

## 🎉 Katkıda Bulunanlar

- **Arda Özkan** - RAG Implementation & Testing
- **Sezer Karakaş** - Project Lead & Repository Management
- **Monster Notebook Team** - Domain Expertise & Data

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

```bash
# Son güncelleme
git log --oneline -5
```

**Monster Notebook RAG Chatbot - Müşteri Desteğinde Yapay Zeka Devrimi** 🚀
