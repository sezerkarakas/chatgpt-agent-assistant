
from openai import OpenAI
import contextlib
import os

# OpenAI API anahtarını gir (gizli tut!)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Dosya yolları
file_paths = [
    "documents/json/baglant_ag_sorunlar.json",
    "documents/json/donanim_ekran_panel.json",
    "documents/json/donanim_guc_batarya.json",
    "documents/json/donanim_klavye_touchpad.json",
    "documents/json/donanim_mentese_kasa.json",
    "documents/json/donanim_usb_portlar.json",
    "documents/json/genel_bilgilendirmeler_diger.json",
    "documents/json/kurulum_ve_yazlm_sorunlar.json",
    "documents/json/Monster Model List.json",
    "documents/json/performans_sorunlar.json",
    "documents/json/ses_hoparlor_problemleri.json",
    "documents/json/Technical Service Information.json",
    "documents/json/Technical Service Office.json",
]

try:
    # Vector Store oluştur
    vector_store = client.vector_stores.create(name="Monster Doküman V4",)
    
    # Dosyaları güvenli şekilde aç ve yükle
    with contextlib.ExitStack() as stack:
        file_streams = [stack.enter_context(open(path, "rb")) for path in file_paths]
        
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )
    
    # Durumu yazdır
    print("✅ Dosya yükleme durumu:", file_batch.status)
    print("📄 Yüklenen dosya sayısı:", file_batch.file_counts)

except Exception as e:
    print(f"❌ Dosya yükleme hatası: {str(e)}")
