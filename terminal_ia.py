import speech_recognition as sr
import pyttsx3
from core_ia import TarsVision

# Inicializa el motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de habla
engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Voz por defecto

# Inicializa el reconocedor de voz
recognizer = sr.Recognizer()

# Inicializa TARS con personalidad y memoria
tars = TarsVision()

# Función para hablar

def speak(text):
    print(f"TARS: {text}")
    engine.say(text)
    engine.runAndWait()

# Función para escuchar

def listen():
    with sr.Microphone() as source:
        print("Escuchando...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='es-ES')
        print(f"Tú: {text}")
        return text
    except sr.UnknownValueError:
        speak("No entendí lo que dijiste. ¿Puedes repetir?")
        return None
    except sr.RequestError:
        speak("Error con el servicio de reconocimiento de voz.")
        return None

# Aquí puedes importar tu lógica principal de IA
def ia_response(user_input):
    # Usar el sistema avanzado de TARS para generar respuesta personalizada
    respuesta = tars.generar_respuesta_texto(user_input, user_id="Ndrz")
    # Personalizar aún más la respuesta con el modo amigable
    respuesta_final = tars.personalidad_amigable(respuesta, modo="amigable")
    return respuesta_final

if __name__ == "__main__":
    speak("Hola, soy TARS. ¿En qué puedo ayudarte?")
    while True:
        user_input = listen()
        if user_input:
            if user_input.lower() in ["salir", "terminar", "adiós"]:
                speak("Hasta luego.")
                break
            response = ia_response(user_input)
            speak(response)
