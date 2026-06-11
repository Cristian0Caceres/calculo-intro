# =============================================================================
# ANALIZADOR DE SECCIONES CÓNICAS
# =============================================================================
# Este módulo identifica y analiza la cónica que representa una ecuación
# cuadrática de la forma general:
#
#       A·x² + C·y² + D·x + E·y + F = 0
#
# Dependiendo de los coeficientes A y C, la cónica puede ser:
#   - Circunferencia  (A = C ≠ 0)
#   - Elipse          (A·C > 0, A ≠ C)
#   - Parábola        (A = 0 ó C = 0, pero no ambos)
#   - Hipérbola       (A·C < 0)
# =============================================================================


# -----------------------------------------------------------------------------
# UTILIDADES MATEMÁTICAS
# Funciones básicas implementadas desde cero (sin usar math ni abs() de Python)
# -----------------------------------------------------------------------------

def Valor_Absoluto(n):
    """
    Devuelve el valor absoluto de n.
    Si n es positivo o cero lo retorna tal cual; si es negativo, lo invierte.
    Equivale a la función abs() de Python.
    """
    return n if n >= 0 else -n


def raiz(n, tolerancia=1e-10):
    """
    Calcula la raíz cuadrada de n usando el método iterativo de Newton-Raphson.

    Idea del método:
        Partiendo de una estimación x, la siguiente aproximación es:
            x_nuevo = (x + n/x) / 2
        Se repite hasta que la diferencia entre iteraciones sea menor que
        la tolerancia (por defecto 1e-10, es decir, muy preciso).

    Casos especiales:
        n < 0  → retorna None  (raíz imaginaria, no válida aquí)
        n = 0  → retorna 0.0

    Estimación inicial:
        Si n >= 1  → x = n   (converge rápido para números grandes)
        Si n < 1   → x = 1.0 (evita divisiones problemáticas con números pequeños)
    """
    if n < 0:
        return None
    if n == 0:
        return 0.0

    x = n if n >= 1 else 1.0  # estimación inicial según la magnitud de n
    for _ in range(200):       # máximo 200 iteraciones (más que suficiente)
        x_nuevo = (x + n / x) / 2
        if Valor_Absoluto(x_nuevo - x) < tolerancia:  # criterio de convergencia
            return x_nuevo
        x = x_nuevo
    return x  # si no converge en 200 pasos, devuelve la mejor aproximación


def redondeo(n, decimales=4):
    """
    Redondea n a la cantidad de decimales indicada (por defecto 4).
    Implementado manualmente para no depender de round() de Python.

    Método:
        1. Multiplica por 10^decimales para "correr" los decimales
        2. Suma 0.5 y trunca → equivale a redondear al entero más cercano
        3. Divide por 10^decimales para volver a la escala original
        4. Respeta el signo original del número
    """
    if n is None:
        return None
    factor = 10 ** decimales
    signo = 1 if n >= 0 else -1
    return signo * int(Valor_Absoluto(n) * factor + 0.5) / factor


def _fmt(n):
    """
    Formatea un número para mostrarlo en los mensajes de pasos intermedios.

    Reglas:
        - None     → muestra "∅" (símbolo de conjunto vacío, indica valor inválido)
        - Entero   → muestra sin decimales  (ej: 4.0 → 4)
        - Decimal  → muestra con decimales  (ej: 2.5 → 2.5)
    """
    if n is None:
        return "∅"
    r = redondeo(n)
    return int(r) if r == int(r) else r


# -----------------------------------------------------------------------------
# COMPLETAR EL CUADRADO
# Núcleo del proceso de transformación a forma canónica
# -----------------------------------------------------------------------------

def completar_cuadrado(A, B):
    """
    Completa el cuadrado para un término de la forma:  A·x² + B·x

    La técnica consiste en escribirlo como:  A·(x - h)² - resta

    Fórmulas:
        h     = -B / (2·A)      → valor que desplaza el vértice/centro
        resta = B² / (4·A)      → término que "sobra" y se pasa al otro lado

    Retorna:
        h     (float) : coordenada del vértice en ese eje
        resta (float) : sobrante que suma al lado derecho de la ecuación
    """
    h = -B / (2 * A)
    resta = (B ** 2) / (4 * A)
    return h, resta


# -----------------------------------------------------------------------------
# TRANSFORMACIÓN A FORMA CANÓNICA
# Convierte la ecuación general  A·x²+C·y²+D·x+E·y+F=0
# en la forma  A·(x-h)² + C·(y-k)² = lado_derecho
# -----------------------------------------------------------------------------

def _transformar(A, C, D, E, F):
    """
    Transforma la ecuación general a forma canónica completando el cuadrado
    en x y en y por separado.

    Proceso:
        1. Pasa F al lado derecho:  lado_derecho = -F
        2. Si A ≠ 0, completa el cuadrado en x → obtiene h y sobrante_x
           El sobrante_x se suma al lado derecho
        3. Si C ≠ 0, completa el cuadrado en y → obtiene k y sobrante_y
           El sobrante_y se suma al lado derecho
        4. Resultado final:
               A·(x-h)² + C·(y-k)² = lado_derecho

    Retorna:
        h            (float) : desplazamiento horizontal del centro/vértice
        k            (float) : desplazamiento vertical del centro/vértice
        lado_derecho (float) : valor del lado derecho tras completar cuadrado
        pasos        (list)  : lista de strings explicando cada paso
    """
    pasos = []
    lado_derecho = -F
    pasos.append(f"Pasamos F al otro lado: -({_fmt(F)})= {_fmt(lado_derecho)}")

    resta_x = resta_y = 0  # sobrantes inicializados en 0

    # --- Completar cuadrado en X (solo si A ≠ 0) ---
    if A != 0:
        h, resta_x = completar_cuadrado(A, D)
        lado_derecho += resta_x
        pasos.append(f"completar cuadrado en x [A={_fmt(A)}, D={_fmt(h)}]\n"
                     f"H = -D/(2A) = -({_fmt(D)})/(2*{_fmt(A)}) = {_fmt(h)}\n"
                     f"sobrante = D ** 2 / (4A) = {_fmt(D)}**2 / (4*{_fmt(A)}) = {_fmt(resta_x)}")
    else:
        h = 0  # sin término en x², el centro está en x = 0

    # --- Completar cuadrado en Y (solo si C ≠ 0) ---
    if C != 0:
        k, resta_y = completar_cuadrado(C, E)
        lado_derecho += resta_y
        pasos.append(f"completar cuadrado en y [A={_fmt(C)}, D={_fmt(E)}]\n"
                     f"H = -E/(2C) = -({_fmt(E)})/(2*{_fmt(C)}) = {_fmt(k)}\n"
                     f"sobrante = E ** 2 / (4C) = {_fmt(E)}**2 / (4*{_fmt(C)}) = {_fmt(resta_y)}")
    else:
        k = 0  # sin término en y², el centro está en y = 0

    pasos.append(
        f"Lado derecho = -F + sobrante_x + sobrante_y \n"
        f"= {_fmt(-F)} + {_fmt(resta_x)} + {_fmt(resta_y)} = {_fmt(lado_derecho)}"
    )
    return h, k, lado_derecho, pasos


# -----------------------------------------------------------------------------
# MANEJO DE ERRORES
# -----------------------------------------------------------------------------

def _error(tipo, msg, pasos=None):
    """
    Crea un diccionario de error uniforme para todas las funciones.

    Parámetros:
        tipo  : nombre de la cónica que se intentaba calcular
        msg   : descripción del problema encontrado
        pasos : pasos realizados antes del error (opcional)

    Retorna un dict con las mismas claves que los resultados normales,
    facilitando el manejo uniforme en el código que llama a estas funciones.
    """
    return {"tipo": tipo, "error": msg, "pasos": pasos or []}


# =============================================================================
# FUNCIONES DE CADA CÓNICA
# Cada función recibe los 5 coeficientes de la forma general:
#   A·x² + C·y² + D·x + E·y + F = 0
# =============================================================================

# -----------------------------------------------------------------------------
# CIRCUNFERENCIA
# Condición: A = C ≠ 0
# Forma canónica: (x-h)² + (y-k)² = r²
# -----------------------------------------------------------------------------

def circunferencia(A, C, D, E, F):
    """
    Analiza la ecuación como una circunferencia.

    Requisito: A = C ≠ 0
        (los coeficientes de x² e y² deben ser iguales y no nulos)

    Proceso:
        1. Completa el cuadrado → obtiene h, k, lado_derecho
        2. Divide por A para normalizar: r² = lado_derecho / A
        3. Calcula r = √(r²) con Newton-Raphson
        4. Si r² ≤ 0, la circunferencia no es real

    Retorna dict con: centro (h,k), radio r, forma canónica y pasos.
    """
    if A == 0 or A != C:
        return _error("circunferencia", "Se requiere A = C =! 0")

    h, k, ld, pasos = _transformar(A, C, D, E, F)

    # Normalizar dividiendo por A para obtener r²
    r2 = ld / A
    pasos.append(f"Normalizamos + A = {_fmt(A)}: r **2 = {_fmt(ld)}/{_fmt(A)} = {_fmt(r2)}")

    # r² debe ser positivo para que exista una circunferencia real
    if r2 <= 0:
        return _error("circunferencia",
                      f"r**2 = {_fmt(r2)}<= 0 -> no existe circunferencia   REAL", pasos)

    r = raiz(r2)
    forma = f"(x - {_fmt(h)}) ** 2  + (y - {_fmt(k)}) ** 2 = {_fmt(r2)}"
    pasos.append(f"r = sqr({_fmt(r2)}) = {_fmt(r)} (newthon-raphson)")
    pasos.append(f"Forma conica: {forma}")

    return {
        "tipo": "circunferencia",
        "centro": (redondeo(h), redondeo(k)),
        "radio": redondeo(r),
        "r2": redondeo(r2),
        "forma_canonica": forma,
        "pasos": pasos,
        "error": None,
    }


# -----------------------------------------------------------------------------
# ELIPSE
# Condición: A·C > 0  y  A ≠ C
# Forma canónica: (x-h)²/a² + (y-k)²/b² = 1
# -----------------------------------------------------------------------------

def elipse(A, C, D, E, F):
    """
    Analiza la ecuación como una elipse.

    Requisito: A·C > 0 y A ≠ C
        (coeficientes del mismo signo pero distintos → figura "achatada")

    Proceso:
        1. Completa el cuadrado → h, k, lado_derecho
        2. Divide por lado_derecho para normalizar:
               a² = lado_derecho / A
               b² = lado_derecho / C
        3. El eje mayor es donde el denominador es mayor:
               a² ≥ b² → eje horizontal
               b² > a² → eje vertical
        4. Calcula c² = |a² - b²|  y  c = √(c²)
           (distancia del centro a cada foco)

    Retorna dict con: centro, a, b, c, focos, vértices, covértices,
                      eje mayor, forma canónica y pasos.
    """
    if A * C <= 0 or A == C:
        return _error("elipse", " se requiere A*C > 0 Y A=/C")

    h, k, ld, pasos = _transformar(A, C, D, E, F)

    if ld <= 0:
        return _error("elipse", f"Lado derecho = {_fmt(ld)} < 0 -> no es elipse real", pasos)

    # Semiejes al cuadrado: se obtienen normalizando por el lado derecho
    a2 = ld / A
    b2 = ld / C
    pasos.append(
        f"Normalizamos / {_fmt(ld)}:\n"
        f"a**2 = {_fmt(ld)}/{_fmt(A)} = {_fmt(a2)}\n"
        f"b**2 = {_fmt(ld)}/{_fmt(C)} = {_fmt(b2)}")
    a = raiz(a2)
    b = raiz(b2)

    # El eje mayor corresponde al semieje de mayor longitud (denominador mayor)
    if a2 >= b2:
        # --- Eje mayor HORIZONTAL: a está en el eje x ---
        eje_mayor = "horizontal"
        c2 = a2 - b2                          # c² = a² - b²  (relación de la elipse)
        c = raiz(c2)
        focos      = [(_fmt(h - c), _fmt(k)), (_fmt(h + c), _fmt(k))]   # focos sobre eje x
        vertices   = [(_fmt(h - a), _fmt(k)), (_fmt(h + a), _fmt(k))]   # extremos del eje mayor
        covertices = [(_fmt(h), _fmt(k - b)), (_fmt(h), _fmt(k + b))]   # extremos del eje menor
        forma      = f"(x-{_fmt(h)})**2/{_fmt(a2)} + (y-{_fmt(k)})**2/{_fmt(b2)} = 1"
    else:
        # --- Eje mayor VERTICAL: a está en el eje y ---
        eje_mayor = "vertical"
        c2 = b2 - a2                          # c² = b² - a²  (b es el semieje mayor)
        c = raiz(c2)
        focos      = [(_fmt(h), _fmt(k - c)), (_fmt(h), _fmt(k + c))]   # focos sobre eje y
        vertices   = [(_fmt(h), _fmt(k - b)), (_fmt(h), _fmt(k + b))]   # extremos del eje mayor
        covertices = [(_fmt(h - a), _fmt(k)), (_fmt(h + a), _fmt(k))]   # extremos del eje menor
        forma      = f"(y-{_fmt(k)})**2/{_fmt(b2)} + (x-{_fmt(h)})**2/{_fmt(a2)} = 1"

    pasos.append(
        f"eje mayor {eje_mayor.upper()}: a**2={_fmt(a2)}, b**2={_fmt(b2)}\n"
        f"a = {_fmt(a)}, b ={_fmt(b)}\n"
        f"c**2 = a**2 - b**2 = {_fmt(a2)} - {_fmt(b2)} = {_fmt(c2)} -> c = {_fmt(c)}"
    )
    pasos.append(f"forma canonica: {forma}")

    return {
        "tipo": "elipse",
        "centro": (redondeo(h), redondeo(k)),
        "a": redondeo(a),
        "b": redondeo(b),
        "c": redondeo(c),
        "a2": redondeo(a2),
        "b2": redondeo(b2),
        "focos": focos,
        "vertices": vertices,
        "covertices": covertices,
        "eje_mayor": eje_mayor,
        "forma_canonica": forma,
        "pasos": pasos,
        "error": None,
    }


# -----------------------------------------------------------------------------
# PARÁBOLA
# Condición: exactamente uno de A o C es 0
# Formas canónicas:
#   Eje vertical:   (x-h)² = 4p·(y-k)
#   Eje horizontal: (y-k)² = 4p·(x-h)
# -----------------------------------------------------------------------------

def parabola(A, C, D, E, F):
    """
    Analiza la ecuación como una parábola.

    Requisito: exactamente uno de A o C es 0
        C = 0, A ≠ 0 → parábola con eje VERTICAL   (abre hacia arriba o abajo)
        A = 0, C ≠ 0 → parábola con eje HORIZONTAL (abre hacia derecha o izquierda)

    Parámetro p:
        4p = coeficiente lineal / coeficiente cuadrático (con signo)
        p > 0 → abre hacia arriba/derecha
        p < 0 → abre hacia abajo/izquierda
        |4p| = longitud del lado recto (cuerda focal perpendicular al eje)

    Proceso (eje vertical, C=0):
        1. Completa cuadrado en x → obtiene h y sobrante
        2. Despeja k: k = (sobrante - F) / E
        3. Calcula 4p = -E/A  y  p = 4p/4
        4. Foco en (h, k+p), directriz y = k-p

    Proceso (eje horizontal, A=0):
        1. Completa cuadrado en y → obtiene k y sobrante
        2. Despeja h: h = (sobrante - F) / D
        3. Calcula 4p = -D/C  y  p = 4p/4
        4. Foco en (h+p, k), directriz x = h-p

    Retorna dict con: vértice, foco, p, 4p, directriz, eje,
                      lado recto, forma canónica y pasos.
    """
    if A != 0 and C != 0:
        return _error("parabola", "A y C =/ 0 -> no es parabola")
    if A == 0 and C == 0:
        return _error("parabola", "A = C = 0 -> ecuacion degenerada")

    pasos = []

    if C == 0:
        # =====================================================================
        # CASO 1: Eje VERTICAL  →  (x-h)² = 4p·(y-k)
        # El término cuadrático es en x; y aparece de forma lineal
        # =====================================================================
        if E == 0:
            return _error("parabola", "E = 0 con C = 0 -> parabola degenerada")

        pasos.append("C = 0, A =/ 0 -> eje VERTICAL: (x-h)**2 = 4p*(y-k)")
        h, sobrante = completar_cuadrado(A, D)

        pasos.append(
            f"completar cuadrado en x:\n"
            f"h = {_fmt(h)}, sobrante = {_fmt(sobrante)}"
        )
        # Despejamos k de la ecuación reordenada
        k = (sobrante - F) / E
        # 4p relaciona el coeficiente lineal en y con el cuadrático en x
        cuatro_p = -E / A
        p = cuatro_p / 4

        pasos.append(
            f"despejamos k y p:\n"
            f"k = (sobrante - F)/E = {_fmt(sobrante)} - {_fmt(F)} / {_fmt(E)} = {_fmt(k)}\n"
            f"4p = -E/A = {_fmt(cuatro_p)} -> p = {_fmt(p)}"
        )

        vertices  = (_fmt(h), _fmt(k))
        foco      = (_fmt(h), _fmt(k + p))       # el foco está p unidades sobre el vértice
        directriz = f"y = {_fmt(k - p)}"          # la directriz está p unidades bajo el vértice
        eje       = "vertical"
        forma     = f"(x-{_fmt(h)})**2 = {_fmt(cuatro_p)} * (y-{_fmt(k)})"

    else:
        # =====================================================================
        # CASO 2: Eje HORIZONTAL  →  (y-k)² = 4p·(x-h)
        # El término cuadrático es en y; x aparece de forma lineal
        # =====================================================================
        if D == 0:
            return _error("parabola", "D = 0 con A = 0 -> parabola degenerada")

        pasos.append("A = 0, C =/ 0 -> eje HORIZONTAL: (y-h)**2 = 4p*(x-k)")
        k, sobrante = completar_cuadrado(C, E)   # completa cuadrado en y (variable cuadrática)

        pasos.append(
            f"completar cuadrado en y:\n"
            f"k = {_fmt(k)}, sobrante = {_fmt(sobrante)}"
        )
        # Despejamos h de la ecuación reordenada
        h = (sobrante - F) / D
        # 4p relaciona el coeficiente lineal en x con el cuadrático en y
        cuatro_p = -D / C
        p = cuatro_p / 4

        pasos.append(
            f"despejamos h y p:\n"
            f"h = (sobrante - F)/D = {_fmt(sobrante)} - {_fmt(F)} / {_fmt(D)} = {_fmt(h)}\n"
            f"4p = -D/C = {_fmt(cuatro_p)} -> p = {_fmt(p)}"
        )

        vertices  = (_fmt(h), _fmt(k))
        foco      = (_fmt(h + p), _fmt(k))       # el foco está p unidades a la derecha del vértice
        directriz = f"x = {_fmt(h - p)}"          # la directriz está p unidades a la izquierda
        eje       = "Horizontal"
        forma     = f"(y-{_fmt(k)})**2 = {_fmt(cuatro_p)} * (x-{_fmt(h)})"

    # El lado recto es el valor absoluto de 4p (longitud de la cuerda focal)
    lado_recto = Valor_Absoluto(cuatro_p)
    pasos.append(
        f"vertice = {vertices}, foco = {foco}\n"
        f"directriz: {directriz}, lado recto = |4p| = {_fmt(lado_recto)}"
    )
    pasos.append(f"forma canonica: {forma}")

    return {
        "tipo": "parabola",
        "vertice": vertices,
        "foco": foco,
        "p": redondeo(p),
        "cuatro_p": redondeo(cuatro_p),
        "directriz": directriz,
        "eje": eje,
        "lado_recto": redondeo(lado_recto),
        "forma_canonica": forma,
        "pasos": pasos,
        "error": None
    }


# -----------------------------------------------------------------------------
# HIPÉRBOLA
# Condición: A·C < 0 (coeficientes de signos opuestos)
# Formas canónicas:
#   Eje real horizontal: (x-h)²/a² - (y-k)²/b² = 1
#   Eje real vertical:   (y-k)²/a² - (x-h)²/b² = 1
# -----------------------------------------------------------------------------

def hiperbola(A, C, D, E, F):
    """
    Analiza la ecuación como una hipérbola.

    Requisito: A·C < 0
        (un coeficiente positivo y el otro negativo → figura "abierta en dos ramas")

    Proceso:
        1. Completa el cuadrado → h, k, lado_derecho
        2. Normaliza dividiendo por lado_derecho:
               coef_x = A / lado_derecho
               coef_y = C / lado_derecho
        3. Determina la orientación por el signo de coef_x:
               coef_x > 0 → eje real HORIZONTAL (la x va primero con signo +)
               coef_x < 0 → eje real VERTICAL   (la y va primero con signo +)
        4. Calcula a², b², c² = a² + b²  (relación de la hipérbola)
           y la pendiente de las asíntotas (±b/a o ±a/b)

    Retorna dict con: centro, a, b, c, focos, vértices, eje real,
                      pendiente de asíntotas, forma canónica y pasos.
    """
    if A * C >= 0:
        return _error("hiperbola", "se requiere A * C < 0 (signos opuestos)")

    h, k, ld, pasos = _transformar(A, C, D, E, F)

    # lado_derecho = 0 → hipérbola degenerada (se reduce a dos rectas que se cruzan)
    if ld == 0:
        return _error("hiperbola",
                      "lado derecho= 0 -> hiperbola degenerada (2 rectas)", pasos)

    # Normalizar para llevar la ecuación a la forma estándar = 1
    coef_x = A / ld
    coef_y = C / ld
    pasos.append(
        f"normalizamos + {_fmt(ld)}:\n"
        f"coef_x = {_fmt(A)}/{_fmt(ld)} = {_fmt(coef_x)}\n"
        f"coef_y = {_fmt(C)}/{_fmt(ld)} = {_fmt(coef_y)}"
    )

    if coef_x > 0:
        # =====================================================================
        # CASO 1: Eje real HORIZONTAL
        # La parte positiva de la ecuación corresponde a x
        # Forma: (x-h)²/a² - (y-k)²/b² = 1
        # =====================================================================
        a2       = 1 / coef_x                      # a² = denominador de x
        b2       = 1 / Valor_Absoluto(coef_y)       # b² = denominador de y
        eje_real = "horizontal"
        a        = raiz(a2)
        b        = raiz(b2)
        c        = raiz(a2 + b2)                    # c² = a² + b² (hipérbola, diferente a elipse)
        focos    = [(_fmt(h - c), _fmt(k)), (_fmt(h + c), _fmt(k))]  # focos sobre eje x
        vertices = [(_fmt(h - a), _fmt(k)), (_fmt(h + a), _fmt(k))]  # vértices sobre eje real
        pendiente = b / a                            # pendiente de asíntotas y = ±(b/a)(x-h)+k
        forma    = f"(x - {_fmt(h)})**2 / {_fmt(a2)} - (y-{_fmt(k)})**2 / {_fmt(b2)} = 1"

    else:
        # =====================================================================
        # CASO 2: Eje real VERTICAL
        # La parte positiva de la ecuación corresponde a y
        # Forma: (y-k)²/a² - (x-h)²/b² = 1
        # =====================================================================
        a2       = 1 / coef_y                       # a² = denominador de y (positivo)
        b2       = 1 / Valor_Absoluto(coef_x)        # b² = denominador de x
        eje_real = "vertical"
        a        = raiz(a2)
        b        = raiz(b2)
        c        = raiz(a2 + b2)
        focos    = [(_fmt(h), _fmt(k - c)), (_fmt(h), _fmt(k + c))]  # focos sobre eje y
        vertices = [(_fmt(h), _fmt(k - a)), (_fmt(h), _fmt(k + a))]  # vértices sobre eje real
        pendiente = a / b                            # pendiente de asíntotas y = ±(a/b)(x-h)+k
        forma    = f"(y - {_fmt(k)})**2 / {_fmt(a2)} - (x-{_fmt(h)})**2 / {_fmt(b2)} = 1"

    pasos.append(
        f"eje real {eje_real.upper()}:\n"
        f"a**2 = {_fmt(a2)}, b**2 = {_fmt(b2)}\n"
        f"a = {_fmt(a)}, b={_fmt(b)}\n"
        f"c**2 = a**2 + b**2 = {_fmt(a2 + b2)} -> c={_fmt(c)}\n"
        f"asintotas: y-{_fmt(k)} = +-{_fmt(pendiente)} * (x-{_fmt(h)})"
    )
    pasos.append(f"forma canonica: {forma}")

    return {
        "tipo": "hiperbola",
        "centro": (redondeo(h), redondeo(k)),
        "a": redondeo(a),
        "b": redondeo(b),
        "c": redondeo(c),
        "a2": redondeo(a2),
        "b2": redondeo(b2),
        "focos": focos,
        "vertices": vertices,
        "eje_real": eje_real,
        "asintota_pendiente": redondeo(pendiente),
        "forma_canonica": forma,
        "pasos": pasos,
        "error": None,
    }


# =============================================================================
# CLASIFICADOR PRINCIPAL
# Decide qué cónica es según las relaciones entre A y C
# =============================================================================

def analizar_conica(A, C, D, E, F):
    """
    Punto de entrada principal. Clasifica y analiza la cónica dada por:

        A·x² + C·y² + D·x + E·y + F = 0

    Árbol de decisión basado en los coeficientes A y C:

        A=0, C=0         → ERROR (no es cónica)
        A = C ≠ 0        → Circunferencia
        A=0 ó C=0        → Parábola        (exactamente uno es 0)
        A·C > 0, A≠C     → Elipse
        A·C < 0          → Hipérbola

    Retorna el dict generado por la función correspondiente,
    siempre con las claves "tipo", "error" y "pasos".
    """
    # Caso degenerado: sin términos cuadráticos no es una cónica
    if A == 0 and A == C:
        return _error("INVALIDA", "A=0 y C=0 -> no es una conica!!!!!")

    # Circunferencia: ambos coeficientes iguales
    if A != 0 and A == C:
        return circunferencia(A, C, D, E, F)

    # Parábola: exactamente uno de los coeficientes cuadráticos es 0
    if A == 0 or C == 0:
        return parabola(A, C, D, E, F)

    # Elipse: mismo signo, distintos valores
    if A * C > 0:
        return elipse(A, C, D, E, F)

    # Hipérbola: signos opuestos (A*C < 0 es el único caso restante)
    return hiperbola(A, C, D, E, F)


# =============================================================================
# BLOQUE DE PRUEBA
# Se ejecuta solo cuando se corre este archivo directamente (no al importarlo)
# =============================================================================

if __name__ == "__main__":

    # Cada caso es una tupla: (descripción, (A, C, D, E, F))
    casos = [
        ("CIRCUNFERENCIA   x²+y²−4x+6y+9=0",    (1,  1,  -4,  6,   9)),
        ("ELIPSE           4x²+9y²−16x+18y−11=0",(4,  9, -16, 18, -11)),
        ("PARÁBOLA VERT.   x²−8y=0",             (1,  0,   0, -8,   0)),
        ("PARÁBOLA HORIZ.  y²+4x=0",             (0,  1,   4,  0,   0)),
        ("HIPÉRBOLA        4x²−9y²−36=0",        (4, -9,   0,  0, -36)),
    ]

    for titulo, coefs in casos:
        print("\n" + "=" * 62)
        print(titulo)
        res = analizar_conica(*coefs)          # desempaqueta la tupla de coeficientes

        if res.get("error"):
            print(f"  ERROR: {res['error']}")
            continue

        # Imprime cada paso del desarrollo
        for p in res["pasos"]:
            print(f"  • {p}")

        # Imprime el resumen según el tipo de cónica identificada
        t = res["tipo"]
        if t == "circunferencia":
            print(f"  → centro={res['centro']}  r={res['radio']}")
        elif t == "elipse":
            print(f"  → centro={res['centro']}  a={res['a']}  b={res['b']}  c={res['c']}")
            print(f"     focos={res['focos']}")
        elif t == "parabola":
            print(f"  → vértice={res['vertice']}  foco={res['foco']}  {res['directriz']}")
        elif t == "hiperbola":
            print(f"  → centro={res['centro']}  a={res['a']}  b={res['b']}  c={res['c']}")
            print(f"     asíntotas pendiente ±{res['asintota_pendiente']}")