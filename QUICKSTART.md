# 🚀 Quick Start Guide - Monster Notebook RAG Chatbot

Bu rehber, Monster Notebook RAG Chatbot'u **5 dakikada** çalıştırmanızı sağlar.

## ⚡ Hızlı Kurulum

### 1️⃣ Repo'yu İndirin (30 saniye)

```bash
git clone https://github.com/sezerkarakas/chatgpt-agent-assistant.git
cd chatgpt-agent-assistant
git checkout arda_rag_v2
```

### 2️⃣ Virtual Environment (1 dakika)

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Bağımlılıkları Yükleyin (2 dakika)

```bash
pip install -r requirements.txt
```

### 4️⃣ API Key Ayarlayın (30 saniye)

`.env` dosyası oluşturun:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5️⃣ Vectorstore Oluşturun (1 dakika)

```bash
python build_vectorstore.py
```

**Çıktı:**
```
📁 Found 13 JSON files
✅ Total loaded: 208 documents from 13 files
✅ FAISS vectorstore created successfully!
```

### 6️⃣ Chatbot'u Başlatın! (Anında)

```bash
python simple_rag_chatbot.py
```

## 🎯 İlk Test

Chatbot açıldığında şu soruyu deneyin:

```
👤 Siz: Bilgisayarım açılmıyor, ne yapmalıyım?
```

**Beklenen Cevap:**
```
🤖 Asistan: Bilgisayarınızı adaptörden çekin. Güç düğmesine parmağınızı 
yaklaşık 40 saniye basılı tutun. Ardından adaptörü tekrar takarak 
açmayı deneyin...
```

## 🧪 Sistem Testini Çalıştırın

Tüm sistemi test etmek için:

```bash
python batch_test_questions.py
```

**Beklenen Sonuç:**
- ✅ 187/187 soru başarılı
- 📊 %100 başarı oranı
- 💰 ~$0.13 maliyet

## ❗ Sorun Giderme

### Problem: "OPENAI_API_KEY not found"
**Çözüm:** 
```bash
# .env dosyasının doğru konumda olduğundan emin olun
ls -la .env  # Linux/Mac
dir .env     # Windows
```

### Problem: "Vectorstore not found"
**Çözüm:**
```bash
python build_vectorstore.py
```

### Problem: "ModuleNotFoundError"
**Çözüm:**
```bash
pip install -r requirements.txt
```

## 📊 Başarı Metrikleri

Kurulum başarılıysa şu metrikleri görmelisiniz:

| Metrik | Beklenen Değer |
|--------|----------------|
| Documents Loaded | 208 |
| JSON Files | 13 |
| Test Success Rate | %100 |
| Average Response Time | ~6 seconds |

## 🎉 Tebrikler!

Artık Monster Notebook RAG Chatbot'unuz hazır! 

### Sıradaki Adımlar:
1. 📖 [README.md](README.md) dosyasını inceleyin
2. 🧪 Kendi sorularınızla test edin
3. 🔧 Özelleştirmeleri keşfedin

---

**💡 İpucu:** Chatbot'ta `clear` yazarak konuşma geçmişini temizleyebilir, `exit` yazarak çıkabilirsiniz.

**🆘 Yardım:** Sorun yaşarsanız [GitHub Issues](https://github.com/sezerkarakas/chatgpt-agent-assistant/issues) kullanın.
