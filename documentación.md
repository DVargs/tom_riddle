* Aclaración inicial. Faltan hacer las voces para que hable cuando escribe. Esto se puede hacer desde herramientas como ElevenLabs o TTSMaker, entre otras. Los archivos de audio que se encuentran en la carpeta static/audios/ no tienen nada, solo están ahí para la estructura del proyecto por lo que hay que reemplazarlos una vez que se tengan esas grabaciones y más!
- Hay que poner más respuestas y por ende más audios de respuesta y, las respuestas que están son genéricas, por lo que tienen que ser acorde a la carrera completamente.
------------------------------------------------------------------------------------------------------

📖 Documentación Técnica: El Diario de Tom RiddleProyecto interactivo desarrollado para la Expo Tech (temática Harry Potter) que simula el cuaderno de Tom Riddle en una Netbook (G5/G7). Permite a los visitantes interactuar por voz, teclado o botones temáticos ("Runas"), absorbiendo la tinta en el pergamino y devolviendo respuestas narradas y escritas en tiempo real sobre la carrera.🛠️ Requisitos y Dependencias

Requisitos de Hardware
- Equipo destino: Netbook del Gobierno (G5/G7 o equivalente) con micrófono y parlantes operativos.
- Pantalla: Configuración recomendada en resolución nativa a pantalla completa (F11).

Requisitos de Software
- Python 3.8 o superior.
- Navegador Web moderno (Google Chrome, Chromium, Brave o Edge).

Dependencias de Python
Instalación vía pip:
- pip install flask pyopenssl


Librería      Función 
flask         Servidor web ligero para procesar la lógica, buscar coincidencias y servir la interfaz.
pyopenssl     (Opcional) Permite levantar el servidor local bajo protocolo seguro HTTPS para autorizar el micrófono.



📂 Estructura del ProyectoPlaintextdiario_riddle/
├── app.py                  # Servidor Flask y algoritmo de puntuación por palabras clave
├── respuestas.json         # Base de conocimientos con reglas, palabras clave y mapeo de audio
├── static/
│   └── audios/             # Audios MP3 sintetizados previamente con IA
│       ├── tom_quien_sos.mp3
│       ├── tom_carrera.mp3
│       ├── tom_materias.mp3
│       ├── tom_duracion.mp3
│       ├── tom_laboral.mp3
│       └── tom_generico.mp3
└── templates/
    └── index.html          # Interfaz gráfica (CSS Pergamino, Web Speech API, Audio Sync)


💻 Código Fuente1. app.py (Servidor y Algoritmo de Coincidencias)
Implementa la normalización de texto (eliminación de tildes, signos de puntuación y mayúsculas) y la ponderación por mayor especificidad para evitar conflictos de orden en el JSON (por ejemplo, prioriza "¿Cuánto dura la carrera?" sobre "carrera").

1 - app.py:

import json
import random
import re
import unicodedata
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def cargar_respuestas():
    try:
        with open('respuestas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar respuestas.json: {e}")
        return {"reglas": [], "genericas": []}

def normalizar_texto(texto):
    """Convierte a minúsculas, remueve tildes, signos de puntuación y espacios extras."""
    if not texto:
        return ""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    return texto.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/preguntar', methods=['POST'])
def preguntar():
    data = request.get_json() or {}
    consulta_bruta = data.get('pregunta', '')
    consulta_norm = normalizar_texto(consulta_bruta)
    
    base_datos = cargar_respuestas()
    
    mejor_regla = None
    max_puntaje = 0
    
    # Evaluación de relevancia por coincidencia de mayor longitud
    for regla in base_datos.get('reglas', []):
        puntaje_regla = 0
        for kw in regla.get('palabras_clave', []):
            kw_norm = normalizar_texto(kw)
            if kw_norm and kw_norm in consulta_norm:
                puntos = len(kw_norm)
                if puntos > puntaje_regla:
                    puntaje_regla = puntos
        
        if puntaje_regla > max_puntaje:
            max_puntaje = puntaje_regla
            mejor_regla = regla
            
    if mejor_regla and max_puntaje > 0:
        return jsonify({
            'respuesta': mejor_regla['respuesta'],
            'audio': mejor_regla['audio']
        })
    
    genericas = base_datos.get('genericas', [])
    if genericas:
        elegida = random.choice(genericas)
        return jsonify({
            'respuesta': elegida['respuesta'],
            'audio': elegida['audio']
        })
    
    return jsonify({
        'respuesta': "La tinta se desvanece sin entender tu mensaje...",
        'audio': "tom_generico.mp3"
    })

if __name__ == '__main__':
    # Habilitar ssl_context='adhoc' si se requiere HTTPS nativo
    app.run(host='0.0.0.0', port=5000, debug=True)



2 - respuestas.json (Base de Conocimiento)

{
  "reglas": [
    {
      "palabras_clave": ["quien sos", "quién eres", "tu nombre", "tom", "riddle"],
      "respuesta": "Soy Tom Marvolo Riddle. Conservo mis recuerdos guardados en este pergamino para quienes buscan conocimiento verdadero...",
      "audio": "tom_quien_sos.mp3"
    },
    {
      "palabras_clave": ["carrera", "profesorado", "informatica", "estudiar"],
      "respuesta": "Estás en el Profesorado de Educación Superior en Informática. Aquí enseñamos a dominar la tecnología, desde la programación hasta la creación de sistemas interactivos...",
      "audio": "tom_carrera.mp3"
    },
    {
      "palabras_clave": ["materia", "que se enseña", "programacion", "materias"],
      "respuesta": "Aprenderás Programación, Robótica, Sistemas Operativos, Redes y Didáctica de la Informática para formar a los futuros profesionales...",
      "audio": "tom_materias.mp3"
    },
    {
      "palabras_clave": ["¿Cuánto dura la carrera?", "duración", "duracion", "años", "cuanto dura", "cuánto dura", "tiempo"],
      "respuesta": "La carrera tiene una duración de 4 años de formación intensa en software, hardware y desarrollo tecnológico...",
      "audio": "tom_duracion.mp3"
    },
    {
      "palabras_clave": ["salida laboral", "trabajo", "trabajar", "laburo"],
      "respuesta": "Podrás ejercer como Docente en escuelas secundarias y terciarias, Asesor Tecnológico, Desarrollador o Diseñador de proyectos educativos...",
      "audio": "tom_laboral.mp3"
    }
  ],
  "genericas": [
    {
      "respuesta": "Veo la curiosidad en tus palabras... Pregúntame sobre el Profesorado de Informática y te daré las respuestas.",
      "audio": "tom_generico.mp3"
    }
  ]
}



3 - templates/index.html (Frontend Kiosk & Audio Sync)

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>El Diario de Tom Riddle</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Italianno&display=swap');

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #080402;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            font-family: 'Italianno', cursive;
            overflow: hidden;
        }

        .diario-container {
            width: 100vw;
            height: 100vh;
            background: #dca86b;
            background-image: 
                linear-gradient(to right, rgba(15, 8, 3, 0.85) 0%, rgba(15, 8, 3, 0.35) 4%, rgba(15, 8, 3, 0.05) 10%, transparent 18%),
                radial-gradient(ellipse at 55% 40%, #e8ba7d 0%, #ca9052 65%, #8c5828 100%);
            padding: 35px 60px 25px 80px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .titulo-diario {
            font-family: 'Cinzel Decorative', serif;
            text-align: center;
            color: #331e0f;
            font-size: 1.4rem;
            letter-spacing: 4px;
            opacity: 0.45;
            border-bottom: 1px solid rgba(51, 30, 15, 0.2);
            padding-bottom: 6px;
        }

        .hoja-texto {
            flex-grow: 1;
            margin-top: 15px;
            margin-bottom: 10px;
            overflow-y: auto;
            font-size: 3.4rem;
            line-height: 1.3;
            letter-spacing: 1px;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }

        .hoja-texto::-webkit-scrollbar {
            display: none;
        }

        .texto-usuario {
            color: #2b180d;
            text-shadow: 0.5px 0.5px 1px rgba(43, 24, 13, 0.5);
            opacity: 1;
            filter: blur(0px);
            transition: opacity 2.5s ease-in-out, filter 2.5s ease-in-out, transform 2.5s ease-in-out;
            margin-bottom: 10px;
        }

        .absorbido {
            opacity: 0;
            filter: blur(7px);
            transform: scale(0.99);
        }

        .respuesta-tom {
            color: #1c1008;
            font-weight: normal;
            text-shadow: 0.5px 0.5px 1px rgba(28, 16, 8, 0.6);
            margin-top: 15px;
            margin-bottom: 10px;
            display: block;
        }

        .letra-suave {
            opacity: 0;
            filter: blur(2px);
            animation: aparecerTinta 0.35s forwards ease-out;
        }

        @keyframes aparecerTinta {
            to {
                opacity: 1;
                filter: blur(0px);
            }
        }

        .panel-interactivo {
            display: flex;
            flex-direction: column;
            gap: 10px;
            border-top: 1px dashed rgba(51, 30, 15, 0.25);
            padding-top: 10px;
        }

        .runas-container {
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .btn-runa {
            background: rgba(51, 30, 15, 0.07);
            border: 1px solid rgba(51, 30, 15, 0.3);
            border-radius: 20px;
            padding: 4px 16px;
            font-family: 'Italianno', cursive;
            font-size: 1.8rem;
            color: #2b180d;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-runa:hover {
            background: rgba(43, 24, 13, 0.18);
            border-color: #1c1008;
            color: #1c1008;
            transform: translateY(-2px);
        }

        .input-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="text"] {
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            font-family: 'Italianno', cursive;
            font-size: 2.8rem;
            color: #1c1008;
        }

        ::placeholder {
            color: rgba(51, 30, 15, 0.45);
            font-style: italic;
        }

        .btn-mic {
            background: none;
            border: none;
            font-size: 2.2rem;
            cursor: pointer;
            transition: transform 0.2s ease;
            opacity: 0.65;
            filter: sepia(1) hue-rotate(-20deg);
        }

        .btn-mic:hover {
            transform: scale(1.2);
            opacity: 1;
        }

        .escuchando {
            animation: pulsoMic 1s infinite alternate;
        }

        @keyframes pulsoMic {
            from { transform: scale(1); opacity: 0.6; }
            to { transform: scale(1.3); opacity: 1; filter: drop-shadow(0 0 6px #331e0f); }
        }
    </style>
</head>
<body>

<div class="diario-container">
    <div class="titulo-diario">T. M. RIDDLE</div>
    
    <div class="hoja-texto" id="hoja">
        <p class="respuesta-tom">Hello... My name is Tom Riddle.</p>
    </div>

    <div class="panel-interactivo">
        <div class="runas-container">
            <button class="btn-runa" onclick="enviarPregunta('¿Qué es esta carrera?')">📜 La Carrera</button>
            <button class="btn-runa" onclick="enviarPregunta('¿Qué materias se cursan?')">🔮 Materias</button>
            <button class="btn-runa" onclick="enviarPregunta('¿Cuánto dura la carrera?')">⏳ Duración</button>
            <button class="btn-runa" onclick="enviarPregunta('¿Qué salida laboral tiene?')">💼 Salida Laboral</button>
        </div>

        <div class="input-row">
            <button class="btn-mic" id="btnMic" title="Toca para hablar por el micrófono">🎙️</button>
            <input type="text" id="inputUsuario" placeholder="Escribe aquí o toca el micrófono..." autocomplete="off">
        </div>
    </div>
</div>

<script>
    const hoja = document.getElementById('hoja');
    const inputUsuario = document.getElementById('inputUsuario');
    const btnMic = document.getElementById('btnMic');

    let audioActual = null;

    function escribirRespuestaConVoz(texto, nombreAudio) {
        if (audioActual) audioActual.pause();
        audioActual = new Audio(`/static/audios/${nombreAudio}`);
        audioActual.play().catch(e => console.log("Audio aguarda interacción previa"));

        const pRespuesta = document.createElement('p');
        pRespuesta.className = 'respuesta-tom';
        hoja.appendChild(pRespuesta);

        let i = 0;
        const intervalo = setInterval(() => {
            if (i < texto.length) {
                const spanLetra = document.createElement('span');
                spanLetra.className = 'letra-suave';
                spanLetra.textContent = texto.charAt(i);
                pRespuesta.appendChild(spanLetra);
                
                hoja.scrollTop = hoja.scrollHeight;
                i++;
            } else {
                clearInterval(intervalo);
            }
        }, 50);
    }

    async function enviarPregunta(textoPregunta) {
        if (!textoPregunta.trim()) return;

        inputUsuario.value = '';

        const pUsuario = document.createElement('p');
        pUsuario.className = 'texto-usuario';
        pUsuario.textContent = '✒️ ' + textoPregunta;
        hoja.appendChild(pUsuario);
        hoja.scrollTop = hoja.scrollHeight;

        setTimeout(() => {
            pUsuario.classList.add('absorbido');
        }, 1200);

        try {
            const response = await fetch('/api/preguntar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta: textoPregunta })
            });
            const data = await response.json();

            setTimeout(() => {
                escribirRespuestaConVoz(data.respuesta, data.audio);
            }, 2600);
        } catch (err) {
            console.error(err);
        }
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-AR';
        recognition.continuous = false;

        btnMic.addEventListener('click', () => {
            recognition.start();
            btnMic.classList.add('escuchando');
        });

        recognition.onresult = (event) => {
            btnMic.classList.remove('escuchando');
            const mensajeVoz = event.results[0][0].transcript;
            enviarPregunta(mensajeVoz);
        };

        recognition.onerror = () => btnMic.classList.remove('escuchando');
        recognition.onend = () => btnMic.classList.remove('escuchando');
    } else {
        btnMic.style.display = 'none';
    }

    inputUsuario.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') enviarPregunta(inputUsuario.value);
    });
</script>

</body>
</html>


⚠️ Troubleshooting: Permisos de Micrófono y Redes Locales

El Problema

Los navegadores modernos bloquean la API del Micrófono (Web Speech API / getUserMedia) en entornos que no utilicen el protocolo HTTPS o localhost. Si se intenta acceder a la aplicación mediante la IP local de la netbook (por ejemplo: [http://192.168.1.15:5000](http://192.168.1.15:5000)), el botón del micrófono se desactiva o no solicita permisos.

- Solución A: Habilitar el origen inseguro en Chromium/Chrome 
Abrir el navegador en la Netbook e ingresar a la URL:chrome://flags/#unsafely-treat-insecure-origin-as-secure
Cambiar la opción de Disabled a Enabled.
En la casilla de texto, agregar las direcciones del servidor separadas por coma:http://localhost:5000, [http://127.0.0.1:5000](http://127.0.0.1:5000), http://<IP_DE_LA_NETBOOK>:5000
Hacer clic en Relaunch para reiniciar el navegador.

- Solución B: Forzar HTTPS en FlaskInstalar la librería SSL: pip install pyopenssl
En app.py, modificar la línea de arranque:app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
Abrir la dirección con https:// y aceptar la excepción de seguridad de certificado autofirmado en el navegador.

-----------------------
🤖 Prompt Máster para Replicar este Proyecto con otra IA
Para volver a generar este proyecto en cualquier otro modelo de Lenguaje / IA, utilizar el siguiente prompt estructurado:

"""
Actúa como un Desarrollador Full-Stack Senior y diseñador de UX/UI. Crea una aplicación web standalone en Python con Flask para simular "El Diario de Tom Riddle" (temática Harry Potter) orientada a un stand interactivo en un evento escolar.

Requisitos técnicos y funcionales:
1. Backend (Flask + Python):
   - Archivo app.py que sirva una interfaz en la ruta raíz '/' y una API en '/api/preguntar' (POST).
   - Base de conocimientos guardada en 'respuestas.json' con un listado de reglas que contienen 'palabras_clave', 'respuesta' y 'audio'.
   - Algoritmo de coincidencias inteligente: Normalizar el texto de la consulta (eliminar tildes, mayúsculas y caracteres especiales) y evaluar todas las reglas asignando un puntaje basado en la LONGITUD de la palabra clave que coincide. La regla con el mayor puntaje gana (para evitar que palabras cortas como "carrera" opaquen frases específicas como "¿Cuánto dura la carrera?"). Si no hay coincidencias, devolver una respuesta genérica aleatoria.

2. Frontend (HTML5 / CSS3 / JavaScript):
   - Diseño estilo Kiosk a pantalla completa (100vw, 100vh) sin barras de desplazamiento visibles (scrollbar invisible) ni bordes negros.
   - Textura visual de pergamino ámbar/miel con sombra de lomo de libro encuadernado en cuero en el margen izquierdo.
   - Fuentes tipográficas caligráficas desde Google Fonts (Italianno y Cinzel Decorative) simulando la letra original de la película Harry Potter y la Cámara Secreta.
   - Tinta sepia/negra con efecto de sangrado sutil en el papel.
   - Interacción triple:
     a) Botón de micrófono usando la Web Speech API nativa (es-AR).
     b) Botones estilo "Runas" de acceso rápido con preguntas frecuentes.
     c) Input de texto para escritura manual.
   - Animación de tinta: Al ingresar una pregunta, el texto aparece en la hoja y a los 1.2 segundos se absorbe mediante desvanecimiento y desenfoque gradual (CSS blur/opacity). Luego, la respuesta de Tom Riddle aparece letra por letra de forma suave mientras se reproduce en paralelo un archivo de audio MP3 alojado en '/static/audios/'.

Entrega el código modularizado listo para ejecutar en carpetas 'templates/' y 'static/'. 
"""