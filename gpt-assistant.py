from openai import OpenAI
import os
import time
import re

def temizle_citation(cevap):
    return re.sub(r"【\d+:\d+†.*?】", "", cevap)

# Sistem promptunu yükle
try:
    with open('gpt_prompt_v4.md', 'r', encoding='utf-8') as file:
        system_instructions = file.read()
except FileNotFoundError:
    print("Hata: gpt_prompt.md dosyası bulunamadı!")
    exit()

# OpenAI istemcisini oluştur
client = OpenAI()  # API keyinizi buraya girin

# Asistanı oluştur
assistant = client.beta.assistants.create(
    name="Monster Terminal Asistanı",
    instructions=system_instructions,
    model="gpt-4o",  # gpt-4o-mini yerine geçerli model
    tools=[{"type": "file_search"}],
)

# Vector Store ve dosyaları yükle
try:
    vector_store = client.vector_stores.create(name="Monster Dokümanları")
    
    file_paths = [
        "documents/json/Monster Model List.json",
        "documents/json/Problems and Solutions.json",
        "documents/json/Technical Service Information.json",
        "documents/json/Technical Service Office.json"
    ]
    
    file_streams = [open(path, "rb") for path in file_paths]
    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, 
        files=file_streams
    )
    
    print("Dosya yükleme durumu:", file_batch.status)
    print("Yüklenen dosyalar:", file_batch.file_counts)
    
    # Asistanı güncelle
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
except Exception as e:
    print(f"Dosya yükleme hatası: {str(e)}")
    exit()

def chat():
    # print("\nMonster Terminal Asistanına Hoş Geldiniz! (Çıkmak için 'exit' yazın)\n")
    
    # Yeni bir thread oluştur
    thread = client.beta.threads.create()
    last_message_id = None
    
    # ASİSTANIN OTOMATİK KARŞILAMA MESAJI GÖNDERMESİ
    # Önce kullanıcı mesajı olmadan asistanı tetiklemek için boş bir mesaj oluştur
    initial_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Merhaba"
    )
    
    # Asistanı çalıştır
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Asistanın karşılama mesajını al
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc"
    )
    
    # Karşılama mesajını göster
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print("\nAsistan:", msg.content[0].text.value, "\n")
            last_message_id = msg.id
            break
    
    # Normal sohbet döngüsü
    while True:
        try:
            # Kullanıcı girişi al
            user_input = input("Siz: ")
            
            if user_input.lower() == 'exit':
                print("\nAsistan: Görüşmek üzere! Monster Terminal Asistanı her zaman yanınızda.\n")
                break
            
            # Mesajı thread'e ekle
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )
            last_message_id = message.id
            
            # Asistanı çalıştır
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            # Asistanın cevabını al
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                order="asc",
                after=last_message_id
            )
            
            # Sadece yeni asistan mesajlarını göster
            for msg in messages.data:
                if msg.role == "assistant":
                    cleaned_message = temizle_citation(msg.content[0].text.value)
                    print("\nAsistan:", cleaned_message, "\n")
                    last_message_id = msg.id
                    break
                    
        except KeyboardInterrupt:
            print("\nAsistan: Görüşmek üzere!\n")
            break
        except Exception as e:
            print(f"\nHata oluştu: {str(e)}\n")

if __name__ == "__main__":
    chat()