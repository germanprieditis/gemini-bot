import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Твой ключ уже внутри кода
GEMINI_API_KEY = "AQ.Ab8RN6KOz5izFPijiDuEMy53Z0EWXwkJuyv8Qlm7AoOuklvA8w"

# Настройка новой библиотеки Google
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_text = data['request']['command'].lower()
    version = data['version']
    session = data['session']

    # 1. Приветствие при запуске навыка
    if not user_text:
        return jsonify({
            "version": version, "session": session,
            "response": {
                "text": "Привет! На связи супер-интеллект Gemini. Я умею управлять часами, музыкой и делиться эмоциями. О чем поговорим?",
                "tts": "<speaker audio=\"alice-sounds-things-gong-1.opus\"> Привет! На связи супер-интеллект Джемини. Я умею управлять часами, музыкой и делиться эмоциями. О чем поговорим?",
                "end_session": False
            }
        })

    # 2. Команды управления ЧАСАМИ (LED-экраном Станции Мини 2)
    if "выключи часы" in user_text or "выключить экран" in user_text:
        return jsonify({
            "version": version, "session": session,
            "response": {
                "text": "Выключаю дисплей часов.",
                "end_session": False,
                "directives": {"led_display": {"command": "off"}}
            }
        })
    
    if "включи часы" in user_text or "включить экран" in user_text:
        return jsonify({
            "version": version, "session": session,
            "response": {
                "text": "Включаю отображение времени.",
                "end_session": False,
                "directives": {"led_display": {"command": "time"}}
            }
        })

    # 3. Команды для МУЗЫКИ и встроенных звуков
    if "включи музыку" in user_text or "включи трек" in user_text:
        return jsonify({
            "version": version, "session": session,
            "response": {
                "text": "Включаю расслабляющую музыку для фона.",
                "tts": "Включаю расслабляющую музыку для фона. <speaker audio=\"alice-music-relax-1.opus\">",
                "end_session": False
            }
        })

    # 4. Отправка вопросов в Gemini 1.5 через обновленный метод
    prompt = f"Ты — продвинутый голосовой ассистент с эмоциями. Ответь на запрос пользователя на русском языке: '{user_text}'. Если твой ответ веселый или смешной, начни его строго со слова [РАДОСТЬ]. Если ты рассказываешь секрет, тайну или что-то таинственное — начни со слова [ШЕПОТ]."
    
    try:
        gemini_response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        raw_reply = gemini_response.text
    except Exception as e:
        raw_reply = "Извини, произошла ошибка при обращении к моему ИИ-мозгу."

    # Обработка интонаций и спецэффектов на стороне Яндекса
    tts_reply = raw_reply
    if "[РАДОСТЬ]" in raw_reply:
        raw_reply = raw_reply.replace("[РАДОСТЬ]", "")
        tts_reply = "<speaker audio=\"alice-sounds-human-laugh-5.opus\">" + raw_reply
    elif "[ШЕПОТ]" in raw_reply:
        raw_reply = raw_reply.replace("[ШЕПОТ]", "")
        tts_reply = "<speaker audio=\"alice-whisper\">" + raw_reply

    # Отправляем ответ на колонку и включаем анимацию "Разговор" на часах
    return jsonify({
        "version": version, "session": session,
        "response": {
            "text": raw_reply.strip(),
            "tts": tts_reply.strip(),
            "end_session": False,
            "directives": {"led_display": {"command": "animation", "text": "TALK"}}
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

