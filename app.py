import threading
import telebot
import requests
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# ==========================================
# إعدادات تليجرام وبينانس (ضع بياناتك هنا)
# ==========================================
TELEGRAM_TOKEN = "9189606611:AAF5XWpG2jBDAv1h3avwt0v_gHl6wxVLTVQ"      # ضع توكن البوت الخاص بك بين علامتي التنصيص
CHAT_ID = "5662351431"            # ضع الـ Chat ID الخاص بك بين علامتي التنصيص

# أضفنا عملة الدوجكوين (DOGEUSDT) للقائمة
TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]

# تهيئة بوت تليجرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_crypto_prices_text():
    """جلب أسعار العملات من بينانس وتجهيز الرسالة"""
    message = "دعبس جابلك أسعار العملات الحالية 📈:\n"
    for symbol in TARGET_SYMBOLS:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url).json()
            if "price" in response:
                price = round(float(response['price']), 4) # عدلنا الرقم العشري لدقة أفضل مع الدوجكوين
                clean_name = symbol.replace('USDT', '')
                message += f"- {clean_name}: {price} $\n"
        except Exception as e:
            print(f"خطأ في السعر {symbol}: {e}")
    return message

# 1. الرد الفوري عند إرسال /prices للبوت
@bot.message_handler(commands=['prices'])
def send_prices_command(message):
    prices_text = get_crypto_prices_text()
    bot.reply_to(message, prices_text)

# 2. الإرسال التلقائي المجدول كل 3 دقائق
def scheduled_crypto_job():
    try:
        prices_text = get_crypto_prices_text()
        bot.send_message(CHAT_ID, prices_text)
        print("تم إرسال التحديث التلقائي بنجاح على تليجرام!")
    except Exception as e:
        print(f"خطأ في الإرسال التلقائي (تأكد من Chat ID أو أنك باعت رسالة للبوت): {e}")

scheduler = BackgroundScheduler()
# ضبط الجدول الزمني ليكون كل 3 دقائق
scheduler.add_job(func=scheduled_crypto_job, trigger="interval", minutes=3)
scheduler.start()

def run_telegram_bot():
    bot.infinity_polling()

@app.route('/')
def index():
    return "دعبس متصل بتليجرام وبينانس ويعمل الآن!"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    return jsonify({'response': f"أهلاً بك يا مصطفى، دعبس استلم رسالتك: {user_message}"})

if __name__ == '__main__':
    # تشغيل بوت تليجرام في الخلفية
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # تشغيل سيرفر فلاسك
    app.run(debug=True, use_reloader=False)