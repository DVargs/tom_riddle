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
    # Eliminar acentos y tildes
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Conservar solo letras, números y espacios
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
    
    # Evaluar todas las reglas y encontrar la de mayor relevancia
    for regla in base_datos.get('reglas', []):
        puntaje_regla = 0
        for kw in regla.get('palabras_clave', []):
            kw_norm = normalizar_texto(kw)
            if kw_norm and kw_norm in consulta_norm:
                # El puntaje equivale a la longitud del término coincidente.
                # Una frase más específica ("cuanto dura la carrera") pesará más que una palabra suelta ("carrera").
                puntos = len(kw_norm)
                if puntos > puntaje_regla:
                    puntaje_regla = puntos
        
        if puntaje_regla > max_puntaje:
            max_puntaje = puntaje_regla
            mejor_regla = regla
            
    # Si encontramos una regla coincidente con puntaje positivo
    if mejor_regla and max_puntaje > 0:
        return jsonify({
            'respuesta': mejor_regla['respuesta'],
            'audio': mejor_regla['audio']
        })
    
    # Si no hubo ninguna coincidencia directa, devolver respuesta genérica
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
    # Agregamos ssl_context='adhoc' para forzar HTTPS local
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')