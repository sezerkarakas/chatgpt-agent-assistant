from openai import OpenAI
import re
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI()  # API key .env dosyasından otomatik yüklenir

assistant = client.beta.assistants.retrieve("asst_XuKA9OFej4LHjuqZGlskT6o6")

def temizle_citation(cevap):
    return re.sub(r"【\d+:\d+†.*?】", "", cevap)

def chat():
    print("\n🤖 Monster Terminal Asistanı (Vector Store Versiyonu) - Başlatılıyor...")
    
    # Yeni bir thread oluştur
    thread = client.beta.threads.create()
    last_message_id = None
    
    # Stats tracking
    total_queries = 0
    total_time = 0
    
    print("✓ Vector Store sistemi hazır!")
    print("Çıkmak için 'exit' yazın, istatistikleri görmek için 'stats' yazın\n")
    
    # ASİSTANIN OTOMATİK KARŞILAMA MESAJI GÖNDERMESİ
    # Önce kullanıcı mesajı olmadan asistanı tetiklemek için boş bir mesaj oluştur
    start_time = time.time()
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
    welcome_time = time.time() - start_time
    
    # Asistanın karşılama mesajını al
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc"
    )
    
    # Karşılama mesajını göster
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print(f"\nAsistan: {msg.content[0].text.value}")
            print(f"⚡ Karşılama süresi: {welcome_time:.2f}s\n")
            last_message_id = msg.id
            break
    
    # Normal sohbet döngüsü
    while True:
        try:
            # Kullanıcı girişi al
            user_input = input("Siz: ")
            
            if user_input.lower() == 'exit':
                print(f"\n📊 Oturum İstatistikleri:")
                print(f"Toplam sorgu: {total_queries}")
                print(f"Ortalama yanıt süresi: {total_time/max(total_queries,1):.2f} saniye")
                print("\nAsistan: Görüşmek üzere! Monster Terminal Asistanı her zaman yanınızda.\n")
                break
                
            if user_input.lower() == 'stats':
                print(f"\n📊 Anlık İstatistikler:")
                print(f"Toplam sorgu: {total_queries}")
                print(f"Ortalama yanıt süresi: {total_time/max(total_queries,1):.2f} saniye")
                continue
                
            if not user_input.strip():
                continue
            
            # Measure response time
            start_time = time.time()
            
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
            
            response_time = time.time() - start_time
            
            # Asistanın cevabını al
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                order="asc",
                after=last_message_id
            )
            
            # Update stats
            total_queries += 1
            total_time += response_time
            
            # Sadece yeni asistan mesajlarını göster
            for msg in messages.data:
                if msg.role == "assistant":
                    cleaned_message = temizle_citation(msg.content[0].text.value)
                    print(f"\nAsistan: {cleaned_message}")
                    print(f"⚡ Yanıt süresi: {response_time:.2f}s | Vector Store\n")
                    last_message_id = msg.id
                    break
                    
        except KeyboardInterrupt:
            print("\nAsistan: Görüşmek üzere!\n")
            break
        except Exception as e:
            print(f"\nHata oluştu: {str(e)}\n")

if __name__ == "__main__":
    chat()