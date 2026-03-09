import os
import time
import threading
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, HTMLResponse
import edge_tts
import io
from pyngrok import ngrok

app = FastAPI()

# صفحة رئيسية بسيطة
@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1>TTS API is Running on GitHub Actions!</h1><p>Use /tts?text=hello</p>"

# نقطة الـ API
@app.get("/tts")
async def text_to_speech(text: str, voice: str = "ar-EG-SalmaNeural", rate: str = "+0%"):
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_stream.seek(0)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

# دالة لتشغيل Ngrok وطباعة الرابط
def start_ngrok():
    # ننتظر قليلاً حتى يبدأ السيرفر
    time.sleep(5)
    
    # الاتصال بـ Ngrok (يجب إضافة NGROK_AUTH_TOKEN في أسرار الريبو)
    auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if auth_token:
        ngrok.set_auth_token(auth_token)
    
    public_url = ngrok.connect(7860)
    print(f"========================================")
    print(f"YOUR PUBLIC URL: {public_url}")
    print(f"========================================")
    # لحفظ الرابط في ملف لاستخدامه لاحقاً (اختياري)
    with open("public_url.txt", "w") as f:
        f.write(str(public_url))

# نقطة البداية
if __name__ == "__main__":
    # تشغيل Ngrok في خيط (Thread) منفصل
    threading.Thread(target=start_ngrok, daemon=True).start()
    
    # تشغيل السيرفر
    uvicorn.run(app, host="0.0.0.0", port=7860)
