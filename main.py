### ******* WHATSAPPTAN KULLANMAK İÇİN *******************

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import openai
from dotenv import load_dotenv
import os
import re
from openai import OpenAI
from twilio.rest import Client
app = FastAPI()

tw_client = Client(account_sid, auth_token)
# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant_id = "asst_nElgvNNBkpoTfiLj3ygrnmHF"  # Your assistant ID




def clean_citation(text):
    """Remove citation markers from response"""
    return re.sub(r"【\d+:\d+†.*?】", "", text)

async def get_assistant_response(thread_id, user_input):
    """Get response from OpenAI Assistant"""
    # Add user message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )
    
    # Run assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    # Get latest assistant message
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1
    )
    
    if messages.data and messages.data[0].role == "assistant":
        return clean_citation(messages.data[0].content[0].text.value)
    return "Üzgünüm, bir yanıt oluşturamadım."


async def send_whatsapp_message(message):
    """Send message via Twilio WhatsApp"""
    try:
        tw_client.messages.create(
            to="whatsapp:+905398565492",  # Alıcı numarası
            from_="whatsapp:+14155238886",  # Twilio WhatsApp numarası
            body=message
        )
    except Exception as e:
        print(f"Twilio gönderim hatası: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    TIMEOUT_SEC=60
    await websocket.accept()
    
    # Create a new thread for this connection
    thread = client.beta.threads.create()
    
    try:
        # Send welcome message
        welcome_msg = "Merhaba! Monster Notebook destek asistanına hoş geldiniz. Size nasıl yardımcı olabilirim?"
        await websocket.send_text(f"AI: {welcome_msg}")
        
        while True:
            try:
                # Receive user input with timeout
                user_input = await asyncio.wait_for(websocket.receive_text(), timeout=TIMEOUT_SEC)
                
                if user_input.lower() in ['çıkış', 'exit', 'kapat']:
                    await websocket.send_text("AI: Görüşmek üzere! Monster Notebook yanınızda.")
                    break
                
                # Get assistant response
                response = await get_assistant_response(thread.id, user_input)
                await websocket.send_text(f"AI: {response}")
                tw_client.messages.create(
                    to="whatsapp:+905398565492",
                    from_="whatsapp:+14155238886",
                    body=response
                )
            except asyncio.TimeoutError:
                # Timeout durumunda kullanıcıya bilgi ver ve bağlantıyı kapat
                await websocket.send_text(f"AI: {TIMEOUT_SEC} saniye işlem yapmadığınız için bağlantı sonlandırılıyor.")
                break
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {str(e)}")
        try:
            # Hata mesajını göndermeyi dene, ama bağlantı kapalıysa hata verme
            await websocket.send_text("AI: Bir hata oluştu, lütfen tekrar deneyin.")
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
