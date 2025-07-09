# build_faiss_index.py

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
import json
from textwrap import wrap

from huggingface_hub import login

login(token= os.getenv("HUGGINGFACE_TOKEN"))  # Hugging Face token ile giriş yap

# Embedding modelini yükle
#model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

docs = []
filepaths = []

base_path = "documents/json"

for filename in os.listdir(base_path):
    if filename.endswith(".json"):
        full_path = os.path.join(base_path, filename)
        with open(full_path, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                text = json.dumps(content, ensure_ascii=False, indent=2)  # JSON'ı düz yazıya çevir
            except json.JSONDecodeError:
                print(f"Hatalı JSON: {filename}")
                continue

            # 🔹 Her belgeyi 300 karakterlik chunk'lara böl
            chunks = wrap(text, width=300)
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                filepaths.append(f"{filename} [chunk {i+1}]")

# 🔹 Embedding üret
embeddings = model.encode(docs, convert_to_numpy=True)

# 🔹 FAISS index oluştur
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 🔹 Kaydet
faiss.write_index(index, "faiss_index.idx")
with open("doc_store.pkl", "wb") as f:
    pickle.dump(filepaths, f)
with open("doc_texts.pkl", "wb") as f:
    pickle.dump(docs, f)

print("✅ FAISS index chunk'larla birlikte oluşturuldu.")
print(f"🔢 Toplam chunk sayısı: {len(docs)}")
