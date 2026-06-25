# =============================================================================
# interfaz/graficador.py 
# =============================================================================
# Módulo de graficación con Matplotlib (solo para visualización).
# Actúa como puente entre la lógica matemática (Logica/) y la interfaz
# CustomTkinter.
#
# Funciones públicas:
#   graficar_conica(datos, contenedor_ctk)
#       → Dibuja la cónica en el CTkFrame reservado de ventana_conicas.py
#
#   graficar_limites(datos, contenedor_ctk)
#       → Dibuja la función por tramos en el CTkFrame de ventana_limites.py
#
# "datos" es el dict devuelto por analizar_conica() o construir_funcion().
# "contenedor_ctk" es el atributo zona_grafica donde se incrusta el canvas.
# =============================================================================

import customtkinter as ctk

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    # DIFERENCIA: Se importó NavigationToolbar2Tk para agregar una barra de herramientas al gráfico.
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    _MPL_OK = True
except ImportError:
    _MPL_OK = False


# ── Paleta de colores (coherente con la UI dark mode) ────────────────────────
_BG     = "#0F1117"   # Fondo exterior de la figura
_PANEL  = "#1A1D2E"   # Fondo interior del plano cartesiano
_LINE   = "#5E81F4"   # Azul principal — curvas de la cónica
_LINE2  = "#F4A261"   # Naranja cálido — segunda rama / puntos notables
_GRAY   = "#7B83B0"   # Ejes y textos secundarios
_WHITE  = "#E8EAF6"   # Textos principales
_RED    = "#F44336"   # Alertas / asíntota vertical
_GREEN  = "#4CAF50"   # Focos
_LAVAND = "#B39DDB"   # Lavanda — asíntotas de hipérbola


# =============================================================================
# UTILIDADES MATEMÁTICAS MANUALES
# Se implementan sin 'import math' para cumplir la restricción académica.
# DIFERENCIA: Estas funciones matemáticas (_raiz, _sin, _cos, _linspace) se 
# movieron hacia arriba en el archivo. La función _rango() fue eliminada.
# =============================================================================

def _raiz(n):
    """
    Raíz cuadrada por el método de Newton-Raphson (Babilónico).
    Retorna None si n < 0 (raíz imaginaria no válida en este contexto).
    """
    if n < 0:
        return None
    if n == 0:
        return 0.0
    x = n if n >= 1 else 1.0
    for _ in range(200):
        xn = (x + n / x) / 2
        d  = xn - x if xn > x else x - xn
        if d < 1e-10:
            return xn
        x = xn
    return x


def _sin(x):
    """
    Seno por serie de Maclaurin (7 términos).
    Primero normaliza el ángulo a [-π, π] para máxima precisión.
    """
    pi = 3.14159265358979323846
    x  = x % (2 * pi)
    if x > pi:
        x -= 2 * pi
    x2 = x * x
    # sin(x) ≈ x·(1 - x²/6·(1 - x²/20·(1 - x²/42·(1 - x²/72))))
    return x * (1 - x2/6 * (1 - x2/20 * (1 - x2/42 * (1 - x2/72))))


def _cos(x):
    """cos(x) = sin(x + π/2)"""
    return _sin(x + 3.14159265358979323846 / 2)


def _linspace(a, b, n=400):
    """
    Genera n puntos equiespaciados en [a, b].
    Equivalente manual a numpy.linspace.
    """
    # DIFERENCIA: Se agregó validación para evitar división por cero si n <= 1.
    if n <= 1:
        return [a]
    paso = (b - a) / (n - 1)
    return [a + i * paso for i in range(n)]


# =============================================================================
# HELPERS DE MATPLOTLIB
# =============================================================================

def _nueva_figura(contenedor):
    """
    Destruye widgets anteriores del contenedor y crea una Figure con el
    estilo visual de la aplicación.
    Retorna (fig, ax) listos para dibujar.
    """
    for widget in contenedor.winfo_children():
        widget.destroy()

    # DIFERENCIA: Se ajustó el tamaño de la figura (height pasó de 3.5 a 3.8) 
    # para dar espacio a la nueva barra de herramientas inferior.
    fig, ax = plt.subplots(figsize=(5, 3.8), facecolor=_BG)
    ax.set_facecolor(_PANEL)

    for spine in ax.spines.values():
        spine.set_edgecolor(_GRAY)

    ax.tick_params(colors=_GRAY, labelsize=8)
    ax.xaxis.label.set_color(_GRAY)
    ax.yaxis.label.set_color(_GRAY)

    return fig, ax


# DIFERENCIA: La función _incrustar() se renombró a _incrustar_con_toolbar() 
# y se le agregó la lógica para incluir NavigationToolbar2Tk.
def _incrustar_con_toolbar(fig, contenedor):
    """
    Incrusta la Figure dentro del CTkFrame y añade la NavigationToolbar
    en la parte inferior para permitir zoom, pan y reset.
    """
    canvas = FigureCanvasTkAgg(fig, master=contenedor)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Barra de herramientas nativa de Matplotlib
    toolbar = NavigationToolbar2Tk(canvas, contenedor)
    toolbar.update()
    toolbar.pack(side="bottom", fill="x")

    plt.close(fig)


# DIFERENCIA: Se extrajo la lógica de dibujar los ejes X e Y a una nueva función helper.
def _ejes_cartesianos(ax):
    """Dibuja las líneas de los ejes X e Y pasando por el origen."""
    ax.axhline(0, color=_GRAY, linewidth=0.6, zorder=1)
    ax.axvline(0, color=_GRAY, linewidth=0.6, zorder=1)


# =============================================================================
# ENRUTADOR PRINCIPAL DE CÓNICAS
# =============================================================================

def graficar_conica(datos, contenedor):
    """
    Lee el tipo de cónica del diccionario `datos` y llama a la función
    de graficación correspondiente.
    """
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


# =============================================================================
# CIRCUNFERENCIA
# Ecuación canónica: (x-h)² + (y-k)² = r²
# Parametrización:   x = h + r·cos(t),  y = k + r·sin(t),  t ∈ [0, 2π]
# =============================================================================

def _graf_circunferencia(d, contenedor):
    h, k = d["centro"]
    r    = d["radio"]
    fig, ax = _nueva_figura(contenedor)

    angulos = _linspace(0, 6.28318530718, 500)
    xs = [h + r * _cos(t) for t in angulos]
    ys = [k + r * _sin(t) for t in angulos]

    # DIFERENCIA: Se agregó el parámetro 'zorder' para controlar qué elementos 
    # se dibujan por encima de otros (las curvas están en zorder=3).
    # También se agregó la etiqueta (label) "r = {r}" a la gráfica principal.
    ax.plot(xs, ys, color=_LINE, linewidth=2, label=f"r = {r}", zorder=3)
    ax.plot(h, k, "o", color=_LINE2, markersize=7, zorder=4, label=f"Centro ({h}, {k})")

    # DIFERENCIA: Se reemplazaron las líneas manuales por la llamada al helper _ejes_cartesianos.
    _ejes_cartesianos(ax)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    
    # DIFERENCIA: Se mejoró el título para mostrar la ecuación canónica en vez de solo "r=...".
    ax.set_title(f"Circunferencia  (x−{h})² + (y−{k})² = {r}²",
                 color=_WHITE, fontsize=9)
    # DIFERENCIA: Se llama a la nueva función de incrustado.
    _incrustar_con_toolbar(fig, contenedor)


# =============================================================================
# ELIPSE
# Ecuación canónica: (x-h)²/a² + (y-k)²/b² = 1
# Parametrización:   x = h + a·cos(t),  y = k + b·sin(t)  (eje mayor horizontal)
#                    x = h + b·cos(t),  y = k + a·sin(t)  (eje mayor vertical)
# =============================================================================

def _graf_elipse(d, contenedor):
    h, k   = d["centro"]
    a, b   = d["a"], d["b"]
    eje_m  = d.get("eje_mayor", "horizontal")
    fig, ax = _nueva_figura(contenedor)

    angulos = _linspace(0, 6.28318530718, 500)

    if eje_m == "horizontal":
        xs = [h + a * _cos(t) for t in angulos]
        ys = [k + b * _sin(t) for t in angulos]
    else:
        xs = [h + b * _cos(t) for t in angulos]
        ys = [k + a * _sin(t) for t in angulos]

    # DIFERENCIA: Se agregó zorder=3 a la curva principal.
    ax.plot(xs, ys, color=_LINE, linewidth=2, zorder=3)
    # DIFERENCIA: Se agregó zorder=4 al centro.
    ax.plot(h, k, "o", color=_LINE2, markersize=7, zorder=4,
            label=f"Centro ({h}, {k})")

    for fx, fy in d.get("focos", []):
        # DIFERENCIA: Se agregó el zorder y la etiqueta (label) para los focos.
        ax.plot(fx, fy, "^", color=_GREEN, markersize=7, zorder=4,
                label=f"Foco ({fx}, {fy})")

    # DIFERENCIA: Uso de la función helper para los ejes cartesianos.
    _ejes_cartesianos(ax)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"Elipse  a = {a},  b = {b}", color=_WHITE, fontsize=9)
    # DIFERENCIA: Llamada a la nueva función de incrustado.
    _incrustar_con_toolbar(fig, contenedor)


# =============================================================================
# PARÁBOLA
# Ecuación canónica vertical:   (x-h)² = 4p(y-k)  →  y = (x-h)²/(4p) + k
# Ecuación canónica horizontal: (y-k)² = 4p(x-h)  →  x = (y-k)²/(4p) + h
# =============================================================================

def _graf_parabola(d, contenedor):
    vx, vy   = d["vertice"]
    p        = d["p"]
    eje      = d.get("eje", "vertical")
    cuatro_p = d.get("cuatro_p", 4 * p)
    fig, ax  = _nueva_figura(contenedor)

    # DIFERENCIA: Se amplió el rango de evaluación 't' de [-4, 4] a [-5, 5] 
    # y la resolución de 400 a 500 puntos para dibujar ramas más largas.
    t_vals = _linspace(-5, 5, 500)

    if eje.lower() in ("vertical", "eje vertical"):
        if cuatro_p != 0:
            xs = [vx + t for t in t_vals]
            ys = [vy + (t ** 2) / cuatro_p for t in t_vals]
            # DIFERENCIA: Se agregó zorder=3.
            ax.plot(xs, ys, color=_LINE, linewidth=2, zorder=3)
    else:
        if cuatro_p != 0:
            ys = [vy + t for t in t_vals]
            xs = [vx + (t ** 2) / cuatro_p for t in t_vals]
            # DIFERENCIA: Se agregó zorder=3.
            ax.plot(xs, ys, color=_LINE, linewidth=2, zorder=3)

    # DIFERENCIA: Se ajustaron los tamaños de los marcadores (markersize 8 y 7) y zorders.
    ax.plot(vx, vy, "o", color=_LINE2, markersize=8, zorder=4,
            label=f"Vértice ({vx}, {vy})")

    fx, fy = d.get("foco", (vx, vy))
    ax.plot(fx, fy, "^", color=_GREEN, markersize=7, zorder=4,
            label=f"Foco ({fx}, {fy})")

    # DIFERENCIA: Uso de _ejes_cartesianos y la función con toolbar.
    _ejes_cartesianos(ax)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title("Parábola", color=_WHITE, fontsize=9)
    _incrustar_con_toolbar(fig, contenedor)


# =============================================================================
# HIPÉRBOLA — GRAFICACIÓN CORREGIDA CON NUMPY
# =============================================================================
#
# CAUSA DEL BUG ANTERIOR:
#   La función _raiz() manual retorna None cuando el argumento es negativo.
#   Cerca de los vértices (x = h ± a), el argumento (x-h)²/a² - 1 puede dar
#   un valor como -4.4e-16 por error de punto flotante en vez de 0.
#   → _raiz(-4.4e-16) devuelve None
#   → k + b * None lanza TypeError o produce NaN silencioso
#   → Matplotlib une el NaN con los puntos adyacentes → la "V" y diagonal
#     que se ven en la pantalla.
#
# SOLUCIÓN:
#   Usar numpy vectorizado con np.clip(arg, 0, None) antes del sqrt.
#   El clip convierte cualquier epsilon negativo (~-1e-15) a 0 exacto,
#   de modo que sqrt(0) = 0 y el punto del vértice queda en (h±a, k). ✓
#   Nunca se genera NaN ni None: 400 puntos por tramo, todos válidos.
#
# ESTRATEGIA (despeje algebraico directo, sin parametrización sec/tan):
#
#   Hipérbola HORIZONTAL  (x-h)²/a² − (y-k)²/b² = 1
#     Despeje: y = k ± b·√( clip((x-h)²/a² − 1, 0) )
#     Rama derecha:   x ∈ [h+a, h+a+margen]   (|x-h| ≥ a garantizado)
#     Rama izquierda: x ∈ [h-a-margen, h-a]   (|x-h| ≥ a garantizado)
#     → 4 trazos independientes (sup/inf × der/izq). Sin líneas cruzadas.
#
#   Hipérbola VERTICAL    (y-k)²/a² − (x-h)²/b² = 1
#     Despeje: x = h ± b·√( clip((y-k)²/a² − 1, 0) )
#     Rama superior: y ∈ [k+a, k+a+margen]
#     Rama inferior: y ∈ [k-a-margen, k-a]
#     → 4 trazos independientes.
#
#   Asíntotas: y − k = ±m·(x − h),  con m = b/a (horiz.) o a/b (vert.)
# =============================================================================

# DIFERENCIA: Se importó numpy exclusivamente para resolver el bug de punto flotante 
# de la hipérbola y vectorizar las operaciones.
import numpy as np


# DIFERENCIA MAYOR: La graficación de la hipérbola se refactorizó por completo.
# Se abandonó la parametrización trigonométrica manual (_sin, _cos con secantes y tangentes) 
# y se separó la lógica en funciones modulares (_dibujar_hiperbola_horizontal, vertical y asintotas).
def _graf_hiperbola(d, contenedor):
    """
    Función principal de la hipérbola.
    Lee el diccionario de datos, crea la figura y delega en las
    funciones de dibujo según la orientación del eje real.
    """
    h, k    = d["centro"]
    a, b    = d["a"], d["b"]
    eje     = d.get("eje_real", "horizontal")
    m       = d.get("asintota_pendiente", b / a if a else 1)
    fig, ax = _nueva_figura(contenedor)

    # Margen visual: las ramas se dibujan 3a más allá de los vértices
    margen = 3 * a

    if eje == "horizontal":
        _dibujar_hiperbola_horizontal(ax, h, k, a, b, margen)
    else:
        _dibujar_hiperbola_vertical(ax, h, k, a, b, margen)

    _dibujar_asintotas(ax, h, k, m, a, margen, eje)

    # ── Puntos notables ───────────────────────────────────────────────────────
    ax.plot(h, k, "o", color=_LINE2, markersize=8, zorder=5,
            label=f"Centro ({h}, {k})")

    # DIFERENCIA: Se agregó el gráfico explícito de los Vértices de la hipérbola.
    for vx, vy in d.get("vertices", []):
        ax.plot(float(vx), float(vy), "s", color=_LINE2, markersize=6, zorder=5,
                label=f"Vértice ({vx}, {vy})")

    for fx, fy in d.get("focos", []):
        ax.plot(float(fx), float(fy), "^", color=_GREEN, markersize=7, zorder=5,
                label=f"Foco ({fx}, {fy})")

    _ejes_cartesianos(ax)
    ax.set_aspect("equal")
    # DIFERENCIA: Se movió la leyenda a la esquina superior derecha (loc="upper right").
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY,
              loc="upper right")
    ax.set_title(f"Hipérbola  a = {a},  b = {b}  (eje {eje})",
                 color=_WHITE, fontsize=9)
    _incrustar_con_toolbar(fig, contenedor)


# DIFERENCIA: Nueva función dedicada a la rama horizontal usando numpy.
def _dibujar_hiperbola_horizontal(ax, h, k, a, b, margen):
    """
    Traza las cuatro curvas que forman la hipérbola horizontal:
        (x-h)²/a² − (y-k)²/b² = 1

    Despeje: y = k ± b · √( (x-h)²/a² − 1 )

    Para cada rama (derecha e izquierda) se calculan simultáneamente
    los dos semitrazos (y superior e inferior) con operaciones numpy
    sobre arrays completos. El clip(0) elimina los epsilons negativos
    de punto flotante que aparecen exactamente en los vértices.
    """
    # ── Rama DERECHA: x desde el vértice derecho hacia la derecha ────────────
    xs_der = np.linspace(h + a, h + a + margen, 500)

    # Argumento de la raíz: debe ser ≥ 0. clip evita NaN por epsilon flotante
    arg_der = np.clip((xs_der - h)**2 / a**2 - 1, 0, None)
    raiz_der = np.sqrt(arg_der)

    ax.plot(xs_der, k + b * raiz_der, color=_LINE, linewidth=2, zorder=3)
    ax.plot(xs_der, k - b * raiz_der, color=_LINE, linewidth=2, zorder=3)

    # ── Rama IZQUIERDA: x desde la izquierda hasta el vértice izquierdo ──────
    xs_izq = np.linspace(h - a - margen, h - a, 500)

    arg_izq = np.clip((xs_izq - h)**2 / a**2 - 1, 0, None)
    raiz_izq = np.sqrt(arg_izq)

    ax.plot(xs_izq, k + b * raiz_izq, color=_LINE, linewidth=2, zorder=3)
    ax.plot(xs_izq, k - b * raiz_izq, color=_LINE, linewidth=2, zorder=3)


# DIFERENCIA: Nueva función dedicada a la rama vertical usando numpy.
def _dibujar_hiperbola_vertical(ax, h, k, a, b, margen):
    """
    Traza las cuatro curvas que forman la hipérbola vertical:
        (y-k)²/a² − (x-h)²/b² = 1

    Despeje: x = h ± b · √( (y-k)²/a² − 1 )

    Misma estrategia que la horizontal pero intercambiando roles de x e y.
    """
    # ── Rama SUPERIOR: y desde el vértice superior hacia arriba ──────────────
    ys_sup = np.linspace(k + a, k + a + margen, 500)

    arg_sup = np.clip((ys_sup - k)**2 / a**2 - 1, 0, None)
    raiz_sup = np.sqrt(arg_sup)

    ax.plot(h + b * raiz_sup, ys_sup, color=_LINE, linewidth=2, zorder=3)
    ax.plot(h - b * raiz_sup, ys_sup, color=_LINE, linewidth=2, zorder=3)

    # ── Rama INFERIOR: y desde abajo hasta el vértice inferior ───────────────
    ys_inf = np.linspace(k - a - margen, k - a, 500)

    arg_inf = np.clip((ys_inf - k)**2 / a**2 - 1, 0, None)
    raiz_inf = np.sqrt(arg_inf)

    ax.plot(h + b * raiz_inf, ys_inf, color=_LINE, linewidth=2, zorder=3)
    ax.plot(h - b * raiz_inf, ys_inf, color=_LINE, linewidth=2, zorder=3)


# DIFERENCIA: La lógica de dibujar asíntotas se movió a su propia función y se 
# le agregaron anotaciones de texto en la gráfica mostrando las ecuaciones.
def _dibujar_asintotas(ax, h, k, m, a, margen, eje):
    """
    Dibuja las dos asíntotas de la hipérbola como líneas discontinuas
    que pasan exactamente por el centro (h, k) con pendientes ±m.

    Las ecuaciones se etiquetan sobre las propias líneas para facilitar
    la lectura durante la defensa oral:
        y − k = +(b/a)(x − h)
        y − k = −(b/a)(x − h)

    Parámetros
    ----------
    ax    : eje de Matplotlib donde se dibujan
    h, k  : coordenadas del centro de la hipérbola
    m     : pendiente positiva (b/a para eje horizontal, a/b para vertical)
    a     : semieje real (define el margen de visualización)
    margen: extensión horizontal/vertical del rango graficado
    eje   : "horizontal" o "vertical"
    """
    # Rango de x para las asíntotas: cubre toda la extensión visible de las ramas
    extension = a + margen
    xs_a = _linspace(h - extension, h + extension, 300)

    # Asíntota con pendiente +m:  y = k + m·(x - h)
    ys_pos = [k + m * (x - h) for x in xs_a]
    # Asíntota con pendiente -m:  y = k - m·(x - h)
    ys_neg = [k - m * (x - h) for x in xs_a]

    # DIFERENCIA: Se utilizan alphas (transparencia) y zorders para las asíntotas.
    ax.plot(xs_a, ys_pos, "--", color=_LAVAND, linewidth=1.0, zorder=2, alpha=0.85)
    ax.plot(xs_a, ys_neg, "--", color=_LAVAND, linewidth=1.0, zorder=2, alpha=0.85)

    # ── Etiquetas de las asíntotas sobre las líneas ───────────────────────────
    # Formato: y − k = ±(m)(x − h)
    _fmt_num = lambda n: int(n) if n == int(n) else round(n, 3)
    hf = _fmt_num(h)
    kf = _fmt_num(k)
    mf = _fmt_num(round(m, 3))

    # Posición de la etiqueta: cerca del extremo derecho de cada asíntota
    x_lbl  = h + extension * 0.78
    y_lbl1 = k + m * (x_lbl - h)
    y_lbl2 = k - m * (x_lbl - h)

    # El signo en la ecuación depende del tipo de eje
    lbl_pos = f"y−{kf}= +({mf})(x−{hf})"
    lbl_neg = f"y−{kf}= −({mf})(x−{hf})"

    # DIFERENCIA: Se dibuja el texto de las ecuaciones de las asíntotas usando ax.text().
    ax.text(x_lbl, y_lbl1, lbl_pos, fontsize=6.5, color=_LAVAND,
            va="bottom", ha="right", zorder=6)
    ax.text(x_lbl, y_lbl2, lbl_neg, fontsize=6.5, color=_LAVAND,
            va="top",    ha="right", zorder=6)


# =============================================================================
# GRAFICADOR DE FUNCIONES POR TRAMOS (límites / continuidad)
# =============================================================================

def graficar_limites(datos, contenedor):
    """
    Dibuja la función por tramos evaluando valores a izquierda y derecha
    del punto crítico 'a'. Muestra círculos abiertos/cerrados para indicar
    si el límite está incluido.
    """
    if not _MPL_OK:
        _aviso_no_matplotlib(contenedor)
        return

    fig, ax = _nueva_figura(contenedor)
    a       = datos["a"]
    caso    = datos["caso"]
    eval_f  = datos["evaluar"]

    margen  = 3
    xs_izq  = _linspace(a - margen, a - 0.005, 300)
    xs_der  = _linspace(a + 0.005,  a + margen, 300)

    ys_izq  = [eval_f(x) for x in xs_izq]
    ys_der  = [eval_f(x) for x in xs_der]

    def _limpia(xs, ys):
        """Descarta valores None, NaN e infinitos grandes."""
        px, py = [], []
        for x, y in zip(xs, ys):
            if y is not None and y == y and abs(y) < 1e6:
                px.append(x)
                py.append(y)
        return px, py

    px_izq, py_izq = _limpia(xs_izq, ys_izq)
    px_der, py_der = _limpia(xs_der, ys_der)

    ax.plot(px_izq, py_izq, color=_LINE,  linewidth=2, label="x < a")
    ax.plot(px_der, py_der, color=_LINE2, linewidth=2, label="x ≥ a")

    ax.axvline(a, color=_RED, linewidth=0.8, linestyle="--", label=f"x = {a}")

    lim_i = datos["limite_izq"]
    lim_d = datos["limite_der"]

    if isinstance(lim_i, (int, float)):
        ax.plot(a, lim_i, "o", color=_LINE,  markersize=7,
                fillstyle="none", linewidth=2)

    if isinstance(lim_d, (int, float)):
        ax.plot(a, lim_d, "o", color=_LINE2, markersize=7,
                fillstyle="full" if datos["f_en_a"] is not None else "none")

    if caso == 3:
        ax.axvline(a, color=_RED, linewidth=1.5, linestyle="-")

    # DIFERENCIA: Uso de la función _ejes_cartesianos y la función incrustar con toolbar.
    _ejes_cartesianos(ax)
    ax.legend(fontsize=7, labelcolor=_WHITE, facecolor=_PANEL, edgecolor=_GRAY)
    ax.set_title(f"f(x)  —  punto crítico: x = {a}", color=_WHITE, fontsize=9)
    _incrustar_con_toolbar(fig, contenedor)


# =============================================================================
# AVISOS DE ERROR (incrustados en la UI, no en consola)
# =============================================================================

def _aviso_no_matplotlib(contenedor):
    """Informa al usuario que falta instalar matplotlib."""
    for widget in contenedor.winfo_children():
        widget.destroy()
    # DIFERENCIA: Pequeño cambio de formateo en cómo se pasan los parámetros a CTkLabel.
    ctk.CTkLabel(
        contenedor,
        text="matplotlib no está instalado.\nEjecuta: pip install matplotlib",
        font=("Segoe UI", 11), text_color="#F4A261"
    ).place(relx=0.5, rely=0.5, anchor="center")


def _aviso_error(contenedor, msg):
    """Muestra un error genérico (cónica degenerada u otro caso inválido)."""
    for widget in contenedor.winfo_children():
        widget.destroy()
    # DIFERENCIA: Pequeño cambio de formateo de parámetros en CTkLabel.
    ctk.CTkLabel(
        contenedor, text=f"⚠  {msg}",
        font=("Segoe UI", 11), text_color="#F44336"
    ).place(relx=0.5, rely=0.5, anchor="center")
