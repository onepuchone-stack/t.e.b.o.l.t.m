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
    response = requests.post(url, data=payload)
    return response.json()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        # Получаем данные из запроса — и из GET, и из POST
        if request.method == 'GET':
            data = request.args.to_dict()  # Параметры из URL
        else:  # POST
            data = request.get_json() or request.form.to_dict()  # JSON или form-data

        if not data:
            return jsonify({"error": "No data"}), 400

        print("Получен постбек:", data)

        # Определяем событие
        event = data.get('event', '').lower()
        # Если event не передан — попробуем определить по другим параметрам
        if not event:
            if 'trader_id' in data and 'click_id' in data:
                event = 'reg'  # По умолчанию регистрация, если нет события

        # Извлекаем нужные параметры
        click_id = data.get('click_id', 'N/A')
        country = data.get('country', 'N/A')
        trader_id = data.get('trader_id', 'N/A')
        sumdep = data.get('sumdep', '0')      # сумма депозита
        wdr_sum = data.get('wdr_sum', '0')    # сумма вывода
        status = data.get('status', 'pending') # статус вывода

        # Формируем сообщение в нужном формате
        if event == 'reg':
            msg = f"🔱reg👾{click_id}🌍{country}🆔{trader_id}🏴‍☠️"
        elif event == 'ftd':
            msg = f"💵ftd👾{click_id}🌍{country}🆔{trader_id}💸{sumdep}🏴‍☠️"
        elif event == 'deposit':
            msg = f"💶dep👾{click_id}🌍{country}🆔{trader_id}💸{sumdep}🏴‍☠️"
        elif event == 'withdraw':
            if status in ['new', 'pending']:
                msg = f"🟥wd👾{click_id}⏳pending🌍{country}🆔{trader_id}💸{wdr_sum}🏴‍☠️"
            elif status in ['processed', 'success']:
                msg = f"🟥wd👾{click_id}⏳success🌍{country}🆔{trader_id}💸{wdr_sum}🏴‍☠️"
            elif status in ['cancelled', 'cancel']:
                msg = f"🟥wd👾{click_id}⏳cancel🌍{country}🆔{trader_id}💸{wdr_sum}🏴‍☠️"
            else:
                msg = f"🟥wd👾{click_id}⏳{status}🌍{country}🆔{trader_id}💸{wdr_sum}🏴‍☠️"
        else:
            msg = f"❓Неизвестное событие: {event} | Данные: {data}"

        # Отправляем в Telegram
        send_telegram_message(msg)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Ошибка:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
