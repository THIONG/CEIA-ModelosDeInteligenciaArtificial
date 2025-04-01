from flask import Flask, request, jsonify, render_template
from langchain_ollama import ChatOllama
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import threading
import signal

# Configuración general
MAX_HISTORY = 10

app = Flask(__name__)
CORS(app)

model = ChatOllama(model="mistral")

context = []

# Función para generar un prompt optimizado que incluya el historial de la conversación.
def generate_prompt(user_input):
    # Concatenamos el historial con formato estructurado
    history_text = "\n".join([f"Usuario: {h['user']}\nAsistente: {h['ai']}" for h in context])
    prompt = f"""
Eres un asistente virtual avanzado con experiencia en programación y análisis de datos.
Tu tarea es proporcionar respuestas claras, concisas y precisas a las consultas del usuario.
Evita generar código a menos que el usuario lo solicite explícitamente.
Utiliza un razonamiento lógico estructurado para evaluar opciones y proporciona ejemplos cuando sea necesario.
Mantén el idioma de la consulta.

### Historial de conversación:
{history_text if history_text else "(Sin historial previo)"}

### Nueva consulta:
Usuario: {user_input}
Asistente:
"""
    return prompt

def update_context(user_input, ai_response):
    global context
    if len(context) >= MAX_HISTORY:
        context.pop(0)
    context.append({"user": user_input, "ai": ai_response})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-response", methods=["POST"])
def get_response():
    global context
    try:
        data = request.get_json()
        user_input = data["message"]

        # Construir el historial de mensajes para el modelo
        messages = [
            {"role": "system", "content": "Eres un asistente virtual avanzado con experiencia en programación y análisis de datos."}
        ]
        for entry in context:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["ai"]})
        messages.append({"role": "user", "content": user_input})

        # Invoca el modelo con los mensajes estructurados
        result = model.invoke(messages).content

        # Actualiza el contexto con la nueva interacción
        update_context(user_input, result)

        return jsonify({"reply": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_context():
    global context
    context = []
    return jsonify({"status": "contexto reiniciado"})

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            file_ext = os.path.splitext(event.src_path)[1].lower()
            if file_ext in ['.py', '.html', '.css', '.js']:
                print(f"\n🔄 Cambio detectado en: {os.path.basename(event.src_path)}")
                print("⚡ Reiniciando servidor...")
                os.kill(os.getpid(), signal.SIGTERM)

def start_watchdog():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    threading.Thread(target=start_watchdog, daemon=True).start()
    app.run(debug=True, use_reloader=False, port=5000)
