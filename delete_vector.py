from openai import OpenAI
import os
# Vector Store'u sil (tüm içeriğiyle birlikte)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


client.vector_stores.delete(vector_store_id="vs_686241d8974881919091836e8f793279")

print("🗑️ 'MONSTER TEKNIK DESTEK v3' adlı Vector Store başarıyla silindi.")
