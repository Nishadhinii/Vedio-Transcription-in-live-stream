import requests
import speech_recognition as sr
import pyttsx3
from flask import Flask, render_template, jsonify
import threading

app = Flask(__name__, template_folder='test')  # 'test' folder should have your HTML file

HUGGINGFACE_API_KEY = "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"
recognizer = sr.Recognizer()

latest_response = {"response": "Press the mic and speak...", "status": "idle"}

def speak(text):
    print(f"🤖 Assistant: {text}")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {query}")
            return query
        except (sr.UnknownValueError, sr.RequestError):
            return ""

def ask_huggingface(question):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": question,
        "parameters": {"max_new_tokens": 100}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
            return str(result)
        else:
            return f"❌ Hugging Face Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Error: {e}"

@app.route('/voice-command', methods=['POST'])
def voice_command():
    def background_task():
        latest_response["status"] = "listening"
        query = listen()
        if query:
            if "exit" in query.lower() or "stop" in query.lower():
                response = "Goodbye!"
                speak(response)
                latest_response.update({"response": response, "status": "done"})
                return
            response = ask_huggingface(query)
            latest_response.update({"response": response, "status": "speaking"})
            speak(response)
            latest_response.update({"response": "Press the mic and speak...", "status": "idle"})
        else:
            response = "Sorry, I didn't catch that."
            latest_response.update({"response": response, "status": "speaking"})
            speak(response)
            latest_response.update({"response": "Press the mic and speak...", "status": "idle"})

    task_thread = threading.Thread(target=background_task)
    task_thread.start()

    return jsonify({'status': 'Listening started...'})

@app.route('/get-response')
def get_response():
    return jsonify(latest_response)

@app.route('/')
def index():
    return render_template('frontend_voice_assistant.html')

if __name__ == "__main__":
    app.run(debug=True)
