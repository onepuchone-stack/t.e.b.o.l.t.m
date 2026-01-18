from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.json()
    except Exception as e:
        print("Ошибка отправки в Telegram:", str(e))
        return {"error": str(e)}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        # Получаем данные — GET или POST
        if request.method == 'GET':
            data = request.args.to_dict()
        else:
            json_data = request.get_json(silent=True)
            form_data = request.form.to_dict()
            data = json_data if json_data else form_data

        if not data:
            return jsonify({"error": "No data received"}), 400

        print("Получен постбек:", data)

        # Безопасное извлечение параметров
        click_id = data.get('click_id') or '0'
        country = data.get('country') or 'N/A'
        trader_id = data.get('trader_id') or 'N/A'
        sumdep = data.get('sumdep') or '0'
        wdr_sum = data.get('wdr_sum') or '0'
        status = data.get('status') or 'pending'
        ac = data.get('ac') or ''

        # Определяем событие ТОЛЬКО из параметра event
        event = (data.get('event') or '').lower()

        # Если event не задан — НЕ угадываем! Просто игнорируем или логируем
        if not event:
            msg = f"⚠️ Пропущено событие: нет параметра 'event'. Данные: {data}"
            send_telegram_message(msg)
            return jsonify({"status": "ignored", "reason": "missing event"}), 200

        # Формируем сообщение строго по шаблону
        if event == 'reg':
            msg = f"🔱reg👾{click_id}🌍{country}🆔{trader_id}🦈{ac}"
        elif event == 'ftd':
            msg = f"💵ftd👾{click_id}🌍{country}🆔{trader_id}💸{sumdep}🦈{ac}"
        elif event == 'deposit':
            msg = f"💶dep👾{click_id}🌍{country}🆔{trader_id}💸{sumdep}🦈{ac}"
        elif event == 'withdraw':
            if status in ['new', 'pending']:
                msg = f"🟥wd👾{click_id}⏳pending🌍{country}🆔{trader_id}💸{wdr_sum}🦈{ac}"
            elif status in ['processed', 'success', 'approved']:
                msg = f"🟥wd👾{click_id}⏳success🌍{country}🆔{trader_id}💸{wdr_sum}🦈{ac}"
            elif status in ['cancelled', 'cancel', 'rejected']:
                msg = f"🟥wd👾{click_id}⏳cancel🌍{country}🆔{trader_id}💸{wdr_sum}🦈{ac}"
            else:
                msg = f"🟥wd👾{click_id}⏳{status}🌍{country}🆔{trader_id}💸{wdr_sum}🦈{ac}"
        else:
            msg = f"❓Неизвестное событие: '{event}' | Данные: {data}"

        send_telegram_message(msg)

        return jsonify({"status": "ok", "event": event}), 200

    except Exception as e:
        error_msg = f"❌ Ошибка в обработчике: {str(e)}"
        print(error_msg)
        send_telegram_message(error_msg)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
