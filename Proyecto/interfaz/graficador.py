# =============================================================================
# interfaz/graficador.py
# =============================================================================
# Módulo de graficación con Matplotlib (permitido solo para visualización).
# Este módulo actúa como un puente entre la lógica matemática y la interfaz 
# gráfica (CustomTkinter).
#
# Expone dos funciones públicas principales:
#
#   graficar_conica(datos, contenedor_ctk)
#       → Dibuja la cónica en el CTkFrame reservado de ventana_conicas.py
#
#   graficar_limites(datos, contenedor_ctk)
#       → Dibuja la función por tramos en el CTkFrame de ventana_limites.py
#
# "datos" es el diccionario devuelto por analizar_conica() o construir_funcion().
# "contenedor_ctk" es el atributo `zona_grafica` donde se incrustará el canvas.
# =============================================================================

import customtkinter as ctk

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _MPL_OK = True
except ImportError:
    # Bandera de seguridad por si el usuario no tiene instalada la librería
    _MPL_OK = False


# ── Colores coherentes con la UI ─────────────────────────────────────────────
# Se definen constantes de color para que los gráficos parezcan nativos de la app
_BG    = "#0F1117"  # Fondo exterior de la figura
_PANEL = "#1A1D2E"  # Fondo interno del plano cartesiano
_LINE  = "#5E81F4"  # Color principal de las curvas
_LINE2 = "#F4A261"  # Color secundario (puntos clave, segunda rama)
_GRAY  = "#7B83B0"  # Ejes y textos secundarios
_WHITE = "#E8EAF6"  # Textos principales
_RED   = "#F44336"  # Alertas o asíntotas verticales
_GREEN = "#4CAF50"  # Focos de las cónicas


# =============================================================================
# HELPERS COMUNES
# Funciones auxiliares genéricas para preparar el entorno gráfico y matemático.
# =============================================================================

def _nueva_figura(contenedor):
    """
    Limpia el contenedor de la interfaz y crea una nueva 'Figure' de Matplotlib
    con el estilo visual de la aplicación.
    """
    # 1. Destruimos cualquier gráfica anterior o mensaje de error que esté en el frame
    for widget in contenedor.winfo_children():
        widget.destroy()
        
    # 2. Creamos la figura de Matplotlib estableciendo el color de fondo
    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor=_BG)
    ax.set_facecolor(_PANEL)
    
    # 3. Pintamos los bordes (spines) del plano cartesiano
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRAY)
        
    # 4. Configuramos el color de los números y etiquetas de los ejes
    ax.tick_params(colors=_GRAY, labelsize=8)
    ax.xaxis.label.set_color(_GRAY)
    ax.yaxis.label.set_color(_GRAY)
    
    return fig, ax


def _incrustar(fig, contenedor):
    """
    Toma la 'Figure' de Matplotlib ya dibujada y la incrusta físicamente 
    dentro del widget de CustomTkinter.
    """
    # FigureCanvasTkAgg es el "traductor" entre Matplotlib y Tkinter
    canvas = FigureCanvasTkAgg(fig, master=contenedor)
    canvas.draw()
    # Empaquetamos el canvas para que ocupe todo el espacio disponible del frame
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def _rango(centro, radio, margen=0.3):
    """Genera un rango de valores simétrico alrededor de un centro."""
    paso  = (2 * radio * (1 + margen)) / 400
    start = centro - radio * (1 + margen)
    return [start + i * paso for i in range(401)]


def _linspace(a, b, n=400):
    """
    Equivalente a numpy.linspace. 
    Genera 'n' puntos equiespaciados entre 'a' y 'b'. Útil para crear los valores de X o T.
    """
    paso = (b - a) / (n - 1)
    return [a + i * paso for i in range(n)]


def _raiz(n):
    """
    Calcula la raíz cuadrada usando el Método Babilónico (Newton-Raphson).
    Se implementa manualmente para mantener la restricción de no usar el módulo 'math'.
    """
    if n < 0:
        return None
    if n == 0:
        return 0.0
    x = n if n >= 1 else 1.0
    for _ in range(200):  # Máximo 200 iteraciones para converger
        xn = (x + n / x) / 2
        d  = xn - x if xn > x else x - xn
        if d < 1e-10:  # Tolerancia de error
            return xn
        x = xn
    return x

# =============================================================================
# GRAFICADOR DE CÓNICAS
# =============================================================================

def graficar_conica(datos, contenedor):
    """
    Enrutador principal. Identifica el tipo de cónica desde el diccionario `datos`
    y llama a la función de dibujo correspondiente.
    """
    # Si la librería no está instalada, mostramos un aviso en la UI y detenemos la ejecución
    if not _MPL_OK:
        _aviso_no_matplotlib(contenedor)
        return

    tipo = datos.get("tipo", "")

    if tipo == "circunferencia":
        _graf_circunferencia(datos, contenedor)
    elif tipo == "elipse":
        _graf_elipse(datos, contenedor)
    elif tipo == "parabola":
        _graf_parabola(datos, contenedor)
    elif tipo == "hiperbola":
        _graf_hiperbola(datos, contenedor)
    else:
        _aviso_error(contenedor, "No se puede graficar este tipo de cónica.")

# ── Circunferencia ────────────────────────────────────────────────────────────

def _graf_circunferencia(d, contenedor):
    h, k = d["centro"]
    r    = d["radio"]
    fig, ax = _nueva_figura(contenedor)

    # Parametrización: x = h + r*cos(t), y = k + r*sin(t) para t entre 0 y 2π
    angulos = _linspace(0, 6.28318530718, 500)
    xs = [h + r * _cos(t) for t in angulos]
    ys = [k + r * _sin(t) for t in angulos]

    ax.plot(xs, ys, color=_LINE, linewidth=2)
    # Dibujamos el centro como un punto
    ax.plot(h, k, "o", color=_LINE2, markersize=6, label=f"Centro ({h},{k})")
    
    # Líneas guía de los ejes X e Y cruzando por el origen (0,0)
    ax.axhline(0, color=_GRAY, linewidth=0.6)
    ax.axvline(0, color=_GRAY, linewidth=0.6)
    
    # Asegura que la cuadrícula sea cuadrada para que el círculo no se vea ovalado
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"Circunferencia  r = {r}", color=_WHITE, fontsize=9)
    _incrustar(fig, contenedor)

# ── Elipse ────────────────────────────────────────────────────────────────────

def _graf_elipse(d, contenedor):
    h, k = d["centro"]
    a, b = d["a"], d["b"]
    fig, ax = _nueva_figura(contenedor)

    angulos = _linspace(0, 6.28318530718, 500)
    eje_m   = d.get("eje_mayor", "horizontal")

    # La parametrización depende de qué eje (x o y) es el mayor ('a' siempre acompaña al mayor)
    if eje_m == "horizontal":
        xs = [h + a * _cos(t) for t in angulos]
        ys = [k + b * _sin(t) for t in angulos]
    else:
        xs = [h + b * _cos(t) for t in angulos]
        ys = [k + a * _sin(t) for t in angulos]

    ax.plot(xs, ys, color=_LINE, linewidth=2)
    ax.plot(h, k, "o", color=_LINE2, markersize=6, label=f"Centro ({h},{k})")

    # Dibujamos los focos si existen en los datos
    for fx, fy in d.get("focos", []):
        ax.plot(fx, fy, "^", color=_GREEN, markersize=6)

    ax.axhline(0, color=_GRAY, linewidth=0.6)
    ax.axvline(0, color=_GRAY, linewidth=0.6)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"Elipse  a={d['a']}  b={d['b']}", color=_WHITE, fontsize=9)
    _incrustar(fig, contenedor)

# ── Parábola ──────────────────────────────────────────────────────────────────

def _graf_parabola(d, contenedor):
    vx, vy = d["vertice"]
    p      = d["p"]
    eje    = d.get("eje", "vertical")
    fig, ax = _nueva_figura(contenedor)

    t_vals = _linspace(-4, 4, 400)
    cuatro_p = d.get("cuatro_p", 4 * p)

    if eje.lower() == "vertical" or eje.lower() == "eje vertical":
        # Despejamos 'y' en función de un desplazamiento 't' desde el vértice
        # Ecuación: (x-h)^2 = 4p(y-k)  →  y = (x-h)^2/(4p) + k
        if cuatro_p != 0:
            xs = [vx + t for t in t_vals]
            ys = [vy + (t ** 2) / cuatro_p for t in t_vals]
            ax.plot(xs, ys, color=_LINE, linewidth=2)
    else:
        # Despejamos 'x' en función de 't'
        # Ecuación: (y-k)^2 = 4p(x-h)  →  x = (y-k)^2/(4p) + h
        if cuatro_p != 0:
            ys = [vy + t for t in t_vals]
            xs = [vx + (t ** 2) / cuatro_p for t in t_vals]
            ax.plot(xs, ys, color=_LINE, linewidth=2)

    ax.plot(vx, vy, "o", color=_LINE2, markersize=6, label=f"Vértice ({vx},{vy})")
    fx, fy = d.get("foco", (vx, vy))
    ax.plot(fx, fy, "^", color=_GREEN, markersize=6, label=f"Foco ({fx},{fy})")
    
    ax.axhline(0, color=_GRAY, linewidth=0.6)
    ax.axvline(0, color=_GRAY, linewidth=0.6)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title("Parábola", color=_WHITE, fontsize=9)
    _incrustar(fig, contenedor)

# ── Hipérbola ─────────────────────────────────────────────────────────────────

def _graf_hiperbola(d, contenedor):
    h, k   = d["centro"]
    a, b   = d["a"], d["b"]
    eje    = d.get("eje_real", "horizontal")
    fig, ax = _nueva_figura(contenedor)

    t_vals = _linspace(0, 6.28318530718, 800)
    ramas_x, ramas_y = [], []
    
    # Parametrización hipérbola: x = h + a*sec(t), y = k + b*tan(t)
    for t in t_vals:
        ct = _cos(t)
        if ct == 0: # Evitar división por cero en secante y tangente
            continue
        sec = 1 / ct
        tan = _sin(t) / ct
        if eje == "horizontal":
            ramas_x.append(h + a * sec)
            ramas_y.append(k + b * tan)
        else:
            ramas_x.append(h + b * tan)
            ramas_y.append(k + a * sec)

    # Lógica crucial: Separar las coordenadas en dos "ramas" distintas.
    # Si graficamos todo junto, Matplotlib dibujará una línea uniendo ambas ramas
    # que cruzará por el centro de la gráfica de forma errónea.
    xs1, ys1, xs2, ys2 = [], [], [], []
    for i in range(len(ramas_x)):
        if eje == "horizontal":
            if ramas_x[i] >= h: # Rama derecha
                xs1.append(ramas_x[i]); ys1.append(ramas_y[i])
            else:               # Rama izquierda
                xs2.append(ramas_x[i]); ys2.append(ramas_y[i])
        else:
            if ramas_y[i] >= k: # Rama superior
                xs1.append(ramas_x[i]); ys1.append(ramas_y[i])
            else:               # Rama inferior
                xs2.append(ramas_x[i]); ys2.append(ramas_y[i])

    ax.plot(xs1, ys1, color=_LINE,  linewidth=2)
    ax.plot(xs2, ys2, color=_LINE,  linewidth=2)
    ax.plot(h, k, "o", color=_LINE2, markersize=6, label=f"Centro ({h},{k})")

    for fx, fy in d.get("focos", []):
        ax.plot(fx, fy, "^", color=_GREEN, markersize=6)

    # Cálculo y dibujo de las Asíntotas
    pend = d.get("asintota_pendiente", b / a if a else 1)
    xs_a = _linspace(h - a * 2, h + a * 2, 100) # Rango de X para las asíntotas
    ax.plot(xs_a, [k + pend * (x - h) for x in xs_a],  "--", color=_GRAY, linewidth=0.8)
    ax.plot(xs_a, [k - pend * (x - h) for x in xs_a],  "--", color=_GRAY, linewidth=0.8)

    ax.axhline(0, color=_GRAY, linewidth=0.6)
    ax.axvline(0, color=_GRAY, linewidth=0.6)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"Hipérbola  a={d['a']}  b={d['b']}", color=_WHITE, fontsize=9)
    _incrustar(fig, contenedor)

# =============================================================================
# GRAFICADOR DE FUNCIONES POR TRAMOS (límites)
# =============================================================================

def graficar_limites(datos, contenedor):
    """
    Dibuja la función por tramos evaluando valores a la izquierda y derecha
    del punto crítico 'a'.
    """
    if not _MPL_OK:
        _aviso_no_matplotlib(contenedor)
        return

    fig, ax = _nueva_figura(contenedor)
    a      = datos["a"]
    caso   = datos["caso"]
    eval_f = datos["evaluar"]

    # Generamos valores de X evitando evaluar exactamente en 'a' para no generar errores (división por cero)
    margen = 3
    xs_izq = _linspace(a - margen, a - 0.005, 300)
    xs_der = _linspace(a + 0.005, a + margen, 300)

    ys_izq = [eval_f(x) for x in xs_izq]
    ys_der = [eval_f(x) for x in xs_der]

    def _limpia(xs, ys):
        """
        Limpia los resultados de la evaluación. 
        Ignora valores 'None' o infinitos (muy grandes) que arruinarían la escala gráfica.
        """
        px, py = [], []
        for x, y in zip(xs, ys):
            if y is not None and y == y and abs(y) < 1e6: # 'y == y' filtra NaN
                px.append(x); py.append(y)
        return px, py

    px_izq, py_izq = _limpia(xs_izq, ys_izq)
    px_der, py_der = _limpia(xs_der, ys_der)

    # Dibujamos ambos lados por separado
    ax.plot(px_izq, py_izq, color=_LINE,  linewidth=2, label="x < a")
    ax.plot(px_der, py_der, color=_LINE2, linewidth=2, label="x ≥ a")

    # Marcador visual de donde se encuentra el punto crítico
    ax.axvline(a, color=_RED, linewidth=0.8, linestyle="--", label=f"x = {a}")

    # Lógica para los círculos que indican si un límite está incluido o no
    lim_i = datos["limite_izq"]
    lim_d = datos["limite_der"]

    if isinstance(lim_i, (int, float)):
        # Círculo vacío (fillstyle="none") para el límite izquierdo (suele ser estricto <)
        ax.plot(a, lim_i, "o", color=_LINE,  markersize=7, fillstyle="none", linewidth=2)
    
    if isinstance(lim_d, (int, float)):
        # Círculo relleno si la función existe en 'a', vacío si es una discontinuidad hueca
        ax.plot(a, lim_d, "o", color=_LINE2, markersize=7,
                fillstyle="full" if datos["f_en_a"] is not None else "none")

    # Si el caso es 3 (Límites infinitos), trazamos una asíntota vertical sólida
    if caso == 3:
        ax.axvline(a, color=_RED, linewidth=1.5, linestyle="-")

    ax.axhline(0, color=_GRAY, linewidth=0.5)
    ax.axvline(0, color=_GRAY, linewidth=0.5)
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"f(x)  —  punto crítico: x = {a}", color=_WHITE, fontsize=9)
    _incrustar(fig, contenedor)

# =============================================================================
# TRIGONOMETRÍA MANUAL (sin usar math)
# Se necesitan estas funciones ya que hay restricciones para no importar 'math'.
# =============================================================================

def _sin(x):
    """
    Calcula el Seno utilizando el polinomio de Maclaurin (Serie de Taylor centrada en 0).
    """
    pi  = 3.14159265358979323846
    
    # 1. Normalizamos el ángulo para que esté dentro del rango de una vuelta [-π, π]
    # Esto asegura que la aproximación de Taylor sea precisa sin necesitar muchos términos
    x   = x % (2 * pi)
    if x > pi:
        x -= 2 * pi
        
    # 2. Serie de Taylor truncada a 7 términos (suficiente precisión visual)
    # sin(x) ≈ x - x^3/3! + x^5/5! - x^7/7! ... (factorizado para eficiencia de cálculo)
    x2  = x * x
    return x * (1 - x2/6 * (1 - x2/20 * (1 - x2/42 * (1 - x2/72))))


def _cos(x):
    """
    Calcula el Coseno basándose en la identidad trigonométrica:
    cos(x) = sin(x + π/2)
    """
    pi = 3.14159265358979323846
    return _sin(x + pi / 2)

# =============================================================================
# AVISOS DE ERROR
# Manejan de forma elegante los fallos incrustando mensajes en la UI
# en lugar de romper el programa por consola.
# =============================================================================

def _aviso_no_matplotlib(contenedor):
    """Muestra un texto amigable indicando que falta instalar la dependencia."""
    for widget in contenedor.winfo_children():
        widget.destroy()
    ctk.CTkLabel(contenedor,
                 text="matplotlib no está instalado.\nEjecuta: pip install matplotlib",
                 font=("Segoe UI", 11), text_color="#F4A261"
                 ).place(relx=0.5, rely=0.5, anchor="center")


def _aviso_error(contenedor, msg):
    """Muestra un error genérico (ej. cónica degenerada)."""
    for widget in contenedor.winfo_children():
        widget.destroy()
    ctk.CTkLabel(contenedor, text=f"⚠  {msg}",
                 font=("Segoe UI", 11), text_color="#F44336"
                 ).place(relx=0.5, rely=0.5, anchor="center")
