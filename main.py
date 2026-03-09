import os
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io

app = FastAPI()

# السماح للمواقع الخارجية بالاتصال (مهم جداً لعمل InfinityFree)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>Server is Running!</h1><p>Use /tts endpoint.</p>"

@app.get("/tts")
async def tts(text: str, voice: str = "ar-EG-SalmaNeural", rate: str = "+0%"):
    try:
        # معالجة قيمة السرعة لتكون نسبة مئوية دائماً
        if not rate.endswith('%'):
            rate = rate + '%'
        if not rate.startswith('+') and not rate.startswith('-'):
            rate = '+' + rate

        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_stream = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        
        audio_stream.seek(0)
        
        return StreamingResponse(
            audio_stream, 
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=output.mp3"}
        )
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import asyncio
    from pyngrok import ngrok

    token = os.getenv("NGROK_AUTH_TOKEN")
    if token:
        ngrok.set_auth_token(token)
        # استخدم اسم النطاق الثابت الخاص بك هنا
        public_url = ngrok.connect(7860, domain="mitzi-rhizomorphous-noncomprehensiblely.ngrok-free.dev")
        print(f"\nURL: {public_url}\n")

    # مهمة للحفاظ على نشاط السيرفر
    async def keep_alive():
        while True:
            await asyncio.sleep(60)

    @app.on_event("startup")
    async def startup():
        asyncio.create_task(keep_alive())

    uvicorn.run(app, host="0.0.0.0", port=7860)
