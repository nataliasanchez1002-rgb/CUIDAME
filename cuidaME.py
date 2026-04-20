# ==========================================
# 1. KIVY CORE & CONFIG 
# ==========================================
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)
# ==========================================
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture
# ==========================================
# 2. COMPONENTES DE INTERFAZ 
# ==========================================
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
# ==========================================
# 3. PROPIEDADES Y ANIMACIÓN
# ==========================================
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty
)
from kivy.animation import Animation
# ==========================================
# 4. KIVYMD 
# ==========================================
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import (
    MDRectangleFlatButton, 
    MDFillRoundFlatButton, 
    MDRaisedButton
)
# ==========================================
# 5. LIBRERÍAS DE PROCESAMIENTO
# ==========================================
import cv2
import numpy as np
# ==========================================
# 6. LIBRERÍAS ESTÁNDAR DE PYTHON
# ==========================================
import os
import webbrowser
import math
import random
import json
from datetime import datetime


# ==========================================

def obtener_ruta_archivo(nombre_archivo):
    import os
    return os.path.join(os.path.dirname(__file__), nombre_archivo)

archivo = "usuarios.json"

def cargar_usuarios():
    ruta = obtener_ruta_archivo("usuarios.json")
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(data):
    ruta = obtener_ruta_archivo("usuarios.json")
    with open(ruta, "w") as f:
        json.dump(data, f)



usuarios = cargar_usuarios()

#========================


# ---------- LOGIN ----------
class LoginScreen(Screen):
    mensaje = StringProperty("")

    def login(self, username, password):
        if not username or not password:
            self.mensaje = "Completa todos los campos"
            return

        if username in usuarios and usuarios[username] == password:
            self.manager.current = "home"
        else:
            self.mensaje = "Usuario o contraseña incorrectos"


# ---------- REGISTER ----------
class RegisterScreen(Screen):
    mensaje = StringProperty("")

    def register(self, username, password):
        if not username or not password:
            self.mensaje = "Completa todos los campos"
            return

        if username in usuarios:
            self.mensaje = "Ese usuario ya existe"
        else:
            usuarios[username] = password
            guardar_usuarios(usuarios)
            self.manager.current = "login"


# ---------- HOME ----------
class HomeScreen(Screen):
    pass
class ImageButton(ButtonBehavior,Image):
    pass

# ---------- DRAG ----------
class DraggableSecret(DragBehavior, Label):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

# ---------- GAME ----------

class GameScreen(Screen):

    secretos = [
        ("Me gusta una sorpresa de cumpleaños", "bueno"),
        ("Un adulto me pidió guardar algo incómodo", "malo"),
        ("Planeo un regalo secreto", "bueno"),
        ("Alguien pidió no contar un toque raro", "malo")
    ]

    def on_enter(self):
        self.puntaje = 0
        self.secretos_restantes = self.secretos.copy()

        self.ids.score_label.text = "Puntos: 0"
        self.ids.score_label.opacity = 0  #

        self.ids.resultado.text = ""
        self.nuevo_secreto()

    def nuevo_secreto(self):
        if not self.secretos_restantes:
            self.ids.secret_label.text = ""

            self.ids.resultado.text = f"Juego terminado \n\nPuntaje final: {self.puntaje}"

            self.ids.score_label.text = f"Puntos: {self.puntaje}"
            self.ids.score_label.opacity = 1  

            return

        texto, self.tipo_correcto = random.choice(self.secretos_restantes)
        self.secretos_restantes.remove((texto, self.tipo_correcto))

        self.ids.secret_label.text = texto
        self.ids.secret_label.pos = (Window.width / 2 - 125, Window.height / 2)

        self.ids.resultado.text = ""

    def verificar_colision(self):
        secreto = self.ids.secret_label
        cofre_bueno = self.ids.bueno
        cofre_malo = self.ids.malo

        x, y = secreto.center

        if cofre_bueno.collide_point(x, y):
            elegido = "bueno"
        elif cofre_malo.collide_point(x, y):
            elegido = "malo"
        else:
            return

        if elegido == self.tipo_correcto:
            self.puntaje += 1
            self.ids.resultado.text = "¡Correcto!"
        else:
            self.ids.resultado.text = "Ese no es el cofre correcto"

        
        self.ids.score_label.text = f"Puntos: {self.puntaje}"

        Clock.schedule_once(lambda dt: self.nuevo_secreto(), 2)

# ---------- BODY DETECTOR ----------

class BodyScreen(Screen):

    def on_enter(self):
        import os
        import numpy as np
        import cv2
        from tensorflow.lite.python.interpreter import Interpreter
        from kivy.graphics.texture import Texture
        from kivy.clock import Clock

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        folder_name = "movenet-tflite-singlepose-lightning-v1"
        self.model_path = os.path.join(BASE_DIR, folder_name, "3.tflite")

        self.prev_points = None  

        try:
            self.interpreter = Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()

            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            self.cap = cv2.VideoCapture(0)
            self.event = Clock.schedule_interval(self.update, 1.0 / 25.0)

        except Exception as e:
            print("Error:", e)

    def on_leave(self):
        if hasattr(self, 'event'):
            self.event.cancel()
        if hasattr(self, 'cap'):
            self.cap.release()

    # ================= DETECCIÓN =================
    def detectar_pose(self, frame):
        img = cv2.resize(frame, (192, 192))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        input_image = np.expand_dims(img, axis=0).astype(np.float32)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_image)
        self.interpreter.invoke()

        return self.interpreter.get_tensor(self.output_details[0]['index'])

    # ================= SMOOTHING =================
    def smooth(self, new_points, alpha=0.6):
        if self.prev_points is None:
            self.prev_points = new_points
            return new_points

        smoothed = []
        for p_old, p_new in zip(self.prev_points, new_points):
            x = int(p_old[0] * alpha + p_new[0] * (1 - alpha))
            y = int(p_old[1] * alpha + p_new[1] * (1 - alpha))
            c = p_new[2]
            smoothed.append((x, y, c))

        self.prev_points = smoothed
        return smoothed

    # ================= LOOP =================
    def update(self, dt):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        try:
            keypoints = self.detectar_pose(frame)[0][0]

            puntos = []
            for kp in keypoints:
                y, x, conf = kp
                puntos.append((int(x * w), int(y * h), conf))

            puntos = self.smooth(puntos)

            overlay = frame.copy()
            th = 0.25

            verde = (0, 255, 0)
            naranja = (0, 165, 255)
            rojo = (0, 0, 255)

            # ================= CARA =================
            if puntos[0][2] > th:
                nx, ny = puntos[0][0], puntos[0][1]

                cv2.circle(overlay, (nx, ny - 35), 35, verde, -1)
                cv2.circle(overlay, (nx - 20, ny - 10), 8, verde, -1)
                cv2.circle(overlay, (nx + 20, ny - 10), 8, verde, -1)
                cv2.circle(overlay, (nx, ny + 30), 18, rojo, -1)

            # ================= MANOS =================
            for i in [9, 10]:
                if puntos[i][2] > th:
                    cv2.circle(overlay, (puntos[i][0], puntos[i][1]), 25, verde, -1)

            # ================= PECHO =================
            if puntos[5][2] > th and puntos[6][2] > th and puntos[11][2] > th:
                hombros_y = (puntos[5][1] + puntos[6][1]) // 2
                cadera_y = puntos[11][1]
                pecho_y = int(hombros_y + (cadera_y - hombros_y) * 0.4)

                pecho_x = (puntos[5][0] + puntos[6][0]) // 2
                cv2.circle(overlay, (pecho_x, pecho_y), 50, rojo, -1)

            # ================= MUSLOS =================
            for i1, i2 in [(11, 13), (12, 14)]:
                if puntos[i1][2] > th and puntos[i2][2] > th:
                    x = (puntos[i1][0] + puntos[i2][0]) // 2
                    y = (puntos[i1][1] + puntos[i2][1]) // 2 + 40
                    cv2.circle(overlay, (x, y), 40, naranja, -1)

            # ================= ENTREPIERNA =================
            if puntos[11][2] > th and puntos[12][2] > th:
                x = (puntos[11][0] + puntos[12][0]) // 2
                y = (puntos[11][1] + puntos[12][1]) // 2 + 50
                cv2.circle(overlay, (x, y), 45, rojo, -1)

            # ================= ESQUELETO =================
            conexiones = [
                (5, 6), (5, 11), (6, 12),
                (11, 12), (11, 13), (13, 15),
                (12, 14), (14, 16),
                (5, 7), (7, 9),
                (6, 8), (8, 10)
            ]

            for a, b in conexiones:
                if puntos[a][2] > th and puntos[b][2] > th:
                    cv2.line(overlay,
                             (puntos[a][0], puntos[a][1]),
                             (puntos[b][0], puntos[b][1]),
                             (255, 255, 255), 2)

            # ================= MEZCLA =================
            frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

            # ================= TEXTO =================
            cv2.putText(frame, "VERDE: Esta bien", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, verde, 2)

            cv2.putText(frame, "NARANJA: Con permiso o cuidado", (20, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, naranja, 2)

            cv2.putText(frame, "ROJO: No tocar", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, rojo, 2)

        except Exception as e:
            print("Error:", e)

        # ================= TEXTURA =================
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(w, h), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.ids.camera_view.texture = texture


# ---------- CHAT ----------
class ChatScreen(Screen):

    modo_texto = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.etapa = 0
        self.respuestas = []

        self.frases = {
            "feliz": ["¡Qué bonito!", "Eso alegra mucho"],
            "triste": ["Lo siento", "Gracias por decirlo"],
            "enojado": ["Es válido sentirse enojado"],
            "asustado": ["Estoy contigo", "Puedes contarme qué pasó"]
        }

        self.btn_enviar = MDFillRoundFlatButton(
            text="Enviar",
            md_bg_color=(0.2, 0.7, 0.3, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height="50dp",
            on_release=lambda x: self.enviar_texto()
        )

    def on_enter(self):
        self.ids.chat_box.clear_widgets()
        self.respuestas = []
        self.agregar_mensaje("¿Cómo te sientes hoy?", principal=True)
        self.mostrar_botones("emociones")
        self.etapa = 1

    def agregar_mensaje(self, texto, es_usuario=False, principal=False):

        mensaje = Label(
            text=texto,
            size_hint_y=None,
            halign="left",
            valign="middle",
            color=(0, 0, 0, 1)
        )

        mensaje.text_size = (260, None)

        def ajustar(_, value):
            mensaje.height = value[1] + 20

        mensaje.bind(texture_size=ajustar)

        with mensaje.canvas.before:
            if es_usuario:
                Color(0.7, 0.85, 1, 1)
            elif principal:
                Color(1, 0.8, 0.9, 1)
            else:
                Color(0.9, 0.9, 0.9, 1)

            mensaje.bg = RoundedRectangle(pos=mensaje.pos, size=mensaje.size, radius=[15])

        def actualizar(_, __):
            mensaje.bg.pos = mensaje.pos
            mensaje.bg.size = mensaje.size

        mensaje.bind(pos=actualizar, size=actualizar)

        self.ids.chat_box.add_widget(mensaje)

    def mostrar_botones(self, tipo):

        self.ids.botones_box.clear_widgets()

        color_feliz = (1, 0.9, 0.2, 1)
        color_triste = (0.2, 0.6, 1, 1)
        color_enojado = (0.9, 0.2, 0.2, 1)
        color_asustado = (0.6, 0.3, 0.8, 1)
        color_default = (0.6, 0.7, 0.8, 1)

        opciones_dict = {
            "emociones": [
                ("Feliz", color_feliz),
                ("Triste", color_triste),
                ("Enojado", color_enojado),
                ("Asustado", color_asustado)
            ],
            "bonito": [("Si", color_feliz), ("No", color_triste), ("Mas o menos", color_default)],
            "incomodo": [("Si", color_enojado), ("No", color_feliz)],
            "tipo_incomodo": [
                ("Toque malo", color_enojado),
                ("Beso malo", color_enojado),
                ("Secreto malo", color_asustado),
                ("Me hizo sentir incómodo", color_asustado),
                ("Quiero escribirlo", color_default)
            ],
            "final": [("Regresar", color_default)]
        }

        opciones = opciones_dict.get(tipo, [])

        self.ids.botones_box.cols = 1 if len(opciones) > 4 else 2

        for texto, color_btn in opciones:
            btn = MDFillRoundFlatButton(
                text=texto,
                md_bg_color=color_btn,
                text_color=(0, 0, 0, 1) if tipo == "emociones" else (1, 1, 1, 1),
                size_hint=(1, None),
                height="50dp",
                on_release=lambda x, t=texto: self.manejar_respuesta(t)
            )
            self.ids.botones_box.add_widget(btn)

    def detectar_riesgo(self, texto):
        texto = texto.lower()

        riesgo_alto = [
            "me toco", "me obligo", "abuso", "me lastimo",
            "secreto", "parte privada", "no le digas a nadie"
        ]

        riesgo_medio = [
            "incomodo", "miedo", "no quiero", "raro", "no me gusta"
        ]

        if any(p in texto for p in riesgo_alto):
            return "alto"
        elif any(p in texto for p in riesgo_medio):
            return "medio"
        return "bajo"

    def evaluar_conversacion(self):
        niveles = [r["riesgo"] for r in self.respuestas]

        if "alto" in niveles:
            return "alto"
        elif "medio" in niveles:
            return "medio"
        return "bajo"

    def guardar_respuestas(self):

        try:
            usuario = getattr(self.manager, "current_user", "anonimo")

            data = {
                "usuario": usuario,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M"),
                "respuestas": self.respuestas,
                "riesgo_total": self.evaluar_conversacion()
            }

            ruta_archivo = obtener_ruta_archivo("usuario_deteccion_riesgo.json")

            historial = []

            if os.path.exists(ruta_archivo):
                try:
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        historial = json.load(f)
                except:
                    historial = []

            historial.append(data)

            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)

        except:
            pass

    def enviar_texto(self):

        texto = self.ids.input_usuario.text.strip()

        if not texto:
            return

        self.ids.input_usuario.text = ""
        self.agregar_mensaje(texto, es_usuario=True)

        nivel_riesgo = self.detectar_riesgo(texto)

        self.respuestas.append({
            "respuesta": texto,
            "riesgo": nivel_riesgo
        })

        if nivel_riesgo == "alto":
            self.agregar_mensaje("Eso no está bien")
            self.agregar_mensaje("Habla con un adulto de confianza")

        elif nivel_riesgo == "medio":
            self.agregar_mensaje("Gracias por confiar en mí")
            self.agregar_mensaje("Es importante hablarlo con un adulto")

        self.ids.botones_box.clear_widgets()
        self.mostrar_botones("final")

        self.guardar_respuestas()
        self.modo_texto = False

    def manejar_respuesta(self, respuesta):

        if respuesta.lower() == "regresar":
            self.manager.current = "home"
            return

        self.agregar_mensaje(respuesta, True)

        self.respuestas.append({
            "respuesta": respuesta,
            "riesgo": self.detectar_riesgo(respuesta)
        })

        r = respuesta.lower()

        if self.etapa == 1:
            self.agregar_mensaje(random.choice(self.frases.get(r, ["Increible"])))
            self.agregar_mensaje("¿Te pasó algo bonito hoy?")
            self.mostrar_botones("bonito")
            self.etapa = 2

        elif self.etapa == 2:
            self.agregar_mensaje("Gracias por contarme")
            self.agregar_mensaje("¿Te pasó algo incómodo?")
            self.mostrar_botones("incomodo")
            self.etapa = 3

        elif self.etapa == 3:
            if "no" in r:
                self.agregar_mensaje("Me alegra")
                self.mostrar_botones("final")
                self.guardar_respuestas()
                self.etapa = 0
            else:
                self.agregar_mensaje("Gracias por confiar en mí")
                self.agregar_mensaje("¿Qué tipo de situación fue?")
                self.mostrar_botones("tipo_incomodo")
                self.etapa = 4

        elif self.etapa == 4:

            if respuesta == "Quiero escribirlo":
                self.agregar_mensaje("Puedes contarme lo que pasó")
                self.agregar_mensaje("Solo escribe lo que quieras")

                self.modo_texto = True

                self.ids.botones_box.clear_widgets()
                self.ids.botones_box.add_widget(self.btn_enviar)

                Clock.schedule_once(
                    lambda dt: setattr(self.ids.input_usuario, 'focus', True), 0.1
                )
                return

            self.agregar_mensaje("Eso no está bien")
            self.agregar_mensaje("Habla con un adulto de confianza")

            self.mostrar_botones("final")
            self.guardar_respuestas()
            self.etapa = 0

#-----MEMORY--------

class MemoryScreen(Screen):
    valores = ListProperty([])
    descubiertas = ListProperty([])
    seleccion = ListProperty([])
    mensaje = StringProperty("¡Encuentra las parejas!")
    puntos = NumericProperty(0)
    tiempo = NumericProperty(30)
    bloqueo_clic = False 
    
    
    IMAGEN_REVERSO = 'Imagenes/reverso.png' 

    def on_enter(self):
        self.iniciar_juego()

    def iniciar_juego(self):
        
        self.pares = {
            "Imagenes/situacion1.png": "Imagenes/respuesta1.png",
            "Imagenes/situacion2.png": "Imagenes/respuesta2.png",
            "Imagenes/situacion3.png": "Imagenes/respuesta3.png"
        }

        self.valores = list(self.pares.keys()) + list(self.pares.values())
        random.shuffle(self.valores)

        self.descubiertas = [False] * len(self.valores)
        self.seleccion = []
        self.puntos = 0
        self.tiempo = 30
        self.mensaje = "¡Encuentra las parejas!"
        self.bloqueo_clic = False

        Clock.unschedule(self.contar_tiempo)
        Clock.schedule_interval(self.contar_tiempo, 1)

        self.crear_tablero()

    def crear_tablero(self):
        grid = self.ids.grid
        grid.clear_widgets()

        for i in range(len(self.valores)):
            btn = Button(
                background_normal=self.IMAGEN_REVERSO, 
                size_hint=(1, 1), 
                on_press=lambda x, idx=i: self.voltear(idx)
            )
            grid.add_widget(btn)
        self.actualizar_ui()

    def actualizar_ui(self):
        for i, btn in enumerate(self.ids.grid.children[::-1]):
            if self.descubiertas[i] or i in self.seleccion:
                btn.background_normal = self.valores[i]
            else:
                btn.background_normal = self.IMAGEN_REVERSO
            
            btn.text = ""
            btn.background_down = btn.background_normal 

    def contar_tiempo(self, dt):
        if self.tiempo > 0:
            self.tiempo -= 1
        else:
            Clock.unschedule(self.contar_tiempo)
            self.mensaje = "Tiempo terminado"
            self.descubiertas = [True] * len(self.valores)
            self.actualizar_ui()

    def voltear(self, i):
        if self.bloqueo_clic or i in self.seleccion or self.descubiertas[i] or self.tiempo <= 0:
            return

        self.seleccion.append(i)
        self.actualizar_ui()

        if len(self.seleccion) == 2:
            self.verificar_pareja()

    def verificar_pareja(self):
        i1, i2 = self.seleccion
        v1, v2 = self.valores[i1], self.valores[i2]

        es_pareja = (v1 in self.pares and self.pares[v1] == v2) or \
                    (v2 in self.pares and self.pares[v2] == v1)

        if es_pareja:
            self.descubiertas[i1] = True
            self.descubiertas[i2] = True
            self.puntos += 1
            self.mensaje = "¡Muy bien!"
            self.seleccion = []
            if all(self.descubiertas):
                Clock.unschedule(self.contar_tiempo)
                self.mensaje = f"¡Ganaste! {self.puntos} pts"
        else:
            self.mensaje = "Casi... ¡intenta otra vez!"
            self.bloqueo_clic = True
            Clock.schedule_once(self.ocultar, 1)
        self.actualizar_ui()

    def ocultar(self, dt):
        self.seleccion = []
        self.bloqueo_clic = False
        self.actualizar_ui()



# ---------- APP ----------
class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.primary_hue = "500"

        return Builder.load_file("cuidaME.kv")


if __name__ == "__main__":
    MyApp().run()