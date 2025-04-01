from app.config import config

class ContextService:
    
    def __init__(self):
        self.context = []
    
    def update_context(self, user_input, ai_response):
        if len(self.context) >= config.MAX_HISTORY:
            self.context.pop(0)
        self.context.append({"user": user_input, "ai": ai_response})
    
    def get_context_messages(self):
        messages = [
            {"role": "system", "content": "Eres un asistente virtual avanzado con experiencia en programación y análisis de datos."}
        ]
        for entry in self.context:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["ai"]})
        return messages
    
    def reset_context(self):
        self.context = []

    def generate_prompt(self, user_input):
        history_text = "\n".join([f"Usuario: {h['user']}\nAsistente: {h['ai']}" for h in self.context])
        prompt = f"""
Eres un asistente virtual avanzado con experiencia en programación y análisis de datos.
Tu tarea es proporcionar respuestas claras, concisas y precisas a las consultas del usuario.
Evita generar código a menos que el usuario lo solicite explícitamente.
Utiliza un razonamiento lógico estructurado para evaluar opciones y proporciona ejemplos cuando sea necesario.
Mantén el idioma de la consulta.

{history_text if history_text else "(Sin historial previo)"}

Usuario: {user_input}
Asistente:
"""
        return prompt

# Instancia global del servicio de contexto
context_service = ContextService()
