import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from agent import KanaOmniAgent # Mengambil logika scraper yang sudah ada
from analyzer import KanaAnalyzer
from dotenv import load_dotenv

load_dotenv()

# Inisialisasi Agent & Analyzer
kana_agent = KanaOmniAgent()
kana_analyzer = KanaAnalyzer()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    chat_id = str(update.message.chat_id)
    
    # Keamanan: Hanya respon jika ID sesuai dengan .env
    if chat_id != os.getenv("TELEGRAM_CHAT_ID"):
        await update.message.reply_text("⛔ Akses Ditolak. Unauthorized ID.")
        return

    if user_msg.startswith("http"):
        await update.message.reply_text(f"🚀 Perintah diterima! Men-scrap niche:\n{user_msg}")
        
        # Eksekusi Scraper & Sync GitHub
        try:
            kana_agent.scrap_and_learn(user_msg)
            await update.message.reply_text("✔ Scrapping & GitHub Push Selesai!")
            
            # Otomatis Jalankan Analyzer setelah scrap
            await update.message.reply_text("🔍 Menjalankan Analisis Celah...")
            kana_analyzer.scan_knowledge()
            await update.message.reply_text("✅ Analisis Selesai. Cek GitHub Kingkana22 untuk detailnya.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("🤖 KANA OMNI Ready. Kirim URL Niche untuk memulai perburuan.")

if __name__ == '__main__':
    print("[*] KANA TELEGRAM CONTROLLER AKTIF...")
    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()