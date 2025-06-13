from openai import OpenAI
import re

client =OpenAI()  # API keyinizi buraya girin


assistant = client.beta.assistants.retrieve("asst_XuKA9OFej4LHjuqZGlskT6o6")
def temizle_citation(cevap):
    return re.sub(r"【\d+:\d+†.*?】", "", cevap)

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