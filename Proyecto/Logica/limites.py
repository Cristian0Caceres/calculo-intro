# =============================================================================
# Logica/limites.py
# =============================================================================
# Módulo encargado de construir y analizar funciones matemáticas por tramos 
# utilizando los dígitos del RUT como parámetros. 
# 
# Su objetivo es calcular límites laterales, determinar la continuidad 
# y clasificar matemáticamente tres tipos de discontinuidades. Todo esto 
# se realiza de forma analítica pura, sin usar librerías externas.
# =============================================================================
# Implementa los tres casos de discontinuidad exigidos por la evaluación:
#   Caso 1 (d8 % 3 == 0) : Discontinuidad removible
#   Caso 2 (d8 % 3 == 1) : Discontinuidad de salto
#   Caso 3 (d8 % 3 == 2) : Discontinuidad infinita
# =============================================================================

# ── Funciones Utilitarias ────────────────────────────────────────────────────

def _redondeo(n, decimales=6):
    """
    Redondea un número flotante a una cantidad específica de decimales.
    
    Concepto: En lugar de usar la función round() nativa que a veces tiene 
    problemas con la representación binaria de los flotantes, este método 
    desplaza la coma (multiplicando por 10^n), trunca el decimal y 
    vuelve a desplazar la coma, garantizando precisión matemática.
    """
    if n is None:
        return None
    factor = 10 ** decimales
    signo  = 1 if n >= 0 else -1
    abs_n  = n if n >= 0 else -n
    return signo * int(abs_n * factor + 0.5) / factor


# =============================================================================
# ORQUESTADOR DEL MÓDULO DE LÍMITES
# =============================================================================

def construir_funcion(digitos):
    """
    Recibe los 8 dígitos del RUT y decide qué tipo de función matemática 
    se va a construir basándose en la regla del residuo (d8 mod 3).
    
    Retorna un diccionario estandarizado con la función lista para ser 
    evaluada y todos sus textos explicativos para la interfaz gráfica.
    """
    # Desempaquetamos los dígitos necesarios
    d1, d2, d3, d4, d5, d6, d7, d8 = digitos[:8]
    
    # El punto crítico de evaluación (a) siempre es el tercer dígito del RUT
    a = d3
    
    # El residuo de dividir el octavo dígito entre 3 determina el caso
    caso = d8 % 3  

    # Derivación al escenario matemático correspondiente
    if caso == 0:
        return _caso_removible(a, d1, d8)
    elif caso == 1:
        return _caso_salto(a, d2, d4, d8)
    else:
        return _caso_infinita(a, d5, d8)


# =============================================================================
# CASO 1: DISCONTINUIDAD REMOVIBLE (Hueco en la gráfica)
# =============================================================================

def _caso_removible(a, d1, d8):
    """
    Construye la función racional: f(x) = (x - a)(x + d1) / (x - a)
    
    Concepto Matemático:
    Al evaluar directamente f(a), obtenemos 0/0 (indeterminación). Sin embargo, 
    como (x - a) está arriba y abajo, se pueden simplificar para todo x distinto 
    de 'a'. Esto significa que el límite existe (es x + d1), pero la función 
    original tiene un "hueco" exacto en x = a.
    """
    limite = a + d1          # Límite analítico tras simplificar la fracción
    f_en_a = None            # f(a) matemáticamente no existe (división por cero)

    def evaluar(x):
        # Programación defensiva: replicamos el hueco matemático
        if x == a:
            return None      
        return x + d1        # Ecuación simplificada para el resto del dominio

    # Textos formateados para la interfaz
    formula_str = (
        f"f(x) = (x − {a})(x + {d1}) / (x − {a})\n"
        f"     = x + {d1}   si x ≠ {a}  (no definida en x = {a})"
    )

    justificacion = (
        f"El sistema generó el Caso 1 porque d8 = {d8} es múltiplo de 3 (d8 % 3 = 0).\n\n"
        f"Punto de análisis crítico: a = {a}\n\n"
        f"Simplificación algebraica:\n"
        f"   El factor (x − {a}) aparece tanto en el numerador como en el denominador.\n"
        f"   Se puede cancelar para todo x ≠ {a}, obteniendo la expresión equivalente:\n"
        f"   f(x) = x + {d1},   x ≠ {a}\n\n"
        f"Cálculo del límite:\n"
        f"   lím(x→{a}) f(x) = lím(x→{a}) (x + {d1}) = {a} + {d1} = {limite}\n\n"
        f"Conclusión de Continuidad:\n"
        f"   Como el límite existe ({limite}) pero f({a}) genera una indeterminación (0/0), "
        f"   estamos ante una DISCONTINUIDAD REMOVIBLE. La gráfica tiene un hueco en ese punto."
    )

    descripcion = f"Se generó una discontinuidad REMOVIBLE (d8={d8} mod 3 = 0). Punto a={a}."

    return _empaquetar(1, a, evaluar, formula_str, limite, limite, True, f_en_a, False, "removible", justificacion, descripcion)


# =============================================================================
# CASO 2: DISCONTINUIDAD DE SALTO (Función por tramos)
# =============================================================================

def _caso_salto(a, d2, d4, d8):
    """
    Construye la función por tramos: 
       f(x) = x + d2  (si x < a)
       f(x) = x + d4  (si x >= a)
       
    Concepto Matemático:
    Para que un límite global exista, los acercamientos por la izquierda y la 
    derecha deben converger al mismo número. Aquí calculamos ambos lados por 
    separado usando su respectiva regla. Si difieren, hay un "salto" abrupto.
    """
    # Evaluamos los límites laterales analíticamente
    lim_izq = a + d2
    lim_der = a + d4
    
    # f(a) se calcula usando el tramo que incluye el signo igual (x >= a)
    f_en_a  = a + d4         
    
    # Comprobación de existencia del límite global
    existe_limite = (lim_izq == lim_der)

    def evaluar(x):
        # Motor lógico que decide qué tramo usar según el valor de x
        return x + d2 if x < a else x + d4

    formula_str = (
        f"f(x) =  x + {d2}   si x < {a}\n"
        f"         x + {d4}   si x ≥ {a}"
    )

    estado_limite = "SÍ" if existe_limite else f"NO  (lím izq = {lim_izq} ≠ lím der = {lim_der})"
    estado_cont = "CONTINUA" if existe_limite else "DISCONTINUA — Discontinuidad de salto"

    justificacion = (
        f"El sistema generó el Caso 2 porque d8 = {d8} deja residuo 1 al dividir por 3.\n\n"
        f"Punto de análisis crítico: a = {a}\n\n"
        f"Límite lateral por la izquierda (usando la primera regla, x < {a}):\n"
        f"   lím(x→{a}⁻) (x + {d2}) = {a} + {d2} = {lim_izq}\n\n"
        f"Límite lateral por la derecha (usando la segunda regla, x ≥ {a}):\n"
        f"   lím(x→{a}⁺) (x + {d4}) = {a} + {d4} = {lim_der}\n\n"
        f"¿Existe el límite global? {estado_limite}\n\n"
        f"Conclusión de Continuidad:\n"
        f"   f({a}) está definida como {f_en_a}. Sin embargo, al ser los límites laterales "
        f"   distintos, la gráfica experimenta un 'salto' abrupto. {estado_cont}."
    )

    descripcion = f"Se generó una discontinuidad de SALTO (d8={d8} mod 3 = 1). Punto a={a}."

    return _empaquetar(2, a, evaluar, formula_str, lim_izq, lim_der, existe_limite, f_en_a, existe_limite, "ninguna" if existe_limite else "salto", justificacion, descripcion)


# =============================================================================
# CASO 3: DISCONTINUIDAD INFINITA (Asíntota Vertical)
# =============================================================================

def _caso_infinita(a, d5, d8):
    """
    Construye la función racional: f(x) = (d5 + 1) / (x - a)
    
    Concepto Matemático:
    El denominador se hace cero exactamente en 'a', pero el numerador es una 
    constante positiva. Al dividir una constante por un número infinitamente 
    pequeño (tendiendo a cero), el resultado explota hacia el infinito, 
    creando una asíntota vertical.
    """
    numerador = d5 + 1 

    def evaluar(x):
        if x == a:
            return None      # Representa la asíntota vertical
        return numerador / (x - a)

    # Lógica de signos para el límite infinito
    if numerador > 0:
        lim_izq, lim_der = "-∞", "+∞"
    elif numerador < 0:
        lim_izq, lim_der = "+∞", "-∞"
    else:
        lim_izq, lim_der = "0", "0"

    formula_str = f"f(x) = {numerador} / (x − {a})"

    justificacion = (
        f"El sistema generó el Caso 3 porque d8 = {d8} deja residuo 2 al dividir por 3.\n\n"
        f"Punto de análisis crítico: a = {a}\n\n"
        f"Análisis del comportamiento cerca de la asíntota:\n"
        f"   El denominador se hace cero en x = {a}, generando una restricción de dominio.\n"
        f"   Al acercarnos por la izquierda (x → {a}⁻), el denominador es negativo, "
        f"   llevando la fracción a {lim_izq}.\n"
        f"   Al acercarnos por la derecha (x → {a}⁺), el denominador es positivo, "
        f"   llevando la fracción a {lim_der}.\n\n"
        f"Conclusión de Continuidad:\n"
        f"   Como la función crece/decrece sin tope numérico al acercarse a x = {a}, "
        f"   estamos ante una DISCONTINUIDAD INFINITA (Asíntota vertical)."
    )

    descripcion = f"Se generó una discontinuidad INFINITA (d8={d8} mod 3 = 2). Punto a={a}."

    return _empaquetar(3, a, evaluar, formula_str, lim_izq, lim_der, False, None, False, "infinita", justificacion, descripcion)


# =============================================================================
# GENERACIÓN DE TABLA DE VALORES NUMÉRICOS
# =============================================================================

def generar_tabla(evaluar, a):
    """
    Calcula la evidencia empírica acercándose infinitesimalmente al punto 'a'.
    
    Concepto Matemático:
    Para demostrar un límite numéricamente, evaluamos la función sumando y 
    restando "deltas" (diferenciales) cada vez más pequeños, simulando 
    el comportamiento de x tendiendo a 'a'.
    """
    deltas = [1, 0.1, 0.01, 0.001]
    filas  = []

    # Acercamiento por la izquierda (x tiende a 'a' desde números menores)
    for delta in reversed(deltas):
        x = a - delta
        val = evaluar(x)
        filas.append({
            "x":      _redondeo(x, 4),
            "fx_str": "No definida" if val is None else str(_redondeo(val, 6)),
            "lado":   "←",
        })

    # Acercamiento por la derecha (x tiende a 'a' desde números mayores)
    for delta in deltas:
        x = a + delta
        val = evaluar(x)
        filas.append({
            "x":      _redondeo(x, 4),
            "fx_str": "No definida" if val is None else str(_redondeo(val, 6)),
            "lado":   "→",
        })

    return filas

# =============================================================================
# EMPAQUETADOR DE RESPUESTAS (USO INTERNO)
# =============================================================================

def _empaquetar(caso, a, evaluar, formula_str, limite_izq, limite_der, 
                limite_existe, f_en_a, continua, tipo_disc, justificacion, descripcion):
    """
    Recopila todas las variables sueltas generadas por los casos matemáticos 
    y las estructura en un diccionario ordenado para que la ventana de la 
    interfaz gráfica pueda leerlas fácilmente sin tener que recalcular nada.
    """
    tabla = generar_tabla(evaluar, a)
    
    return {
        "caso":          caso,
        "a":             a,
        "formula_str":   formula_str,
        "evaluar":       evaluar,
        "limite_izq":    limite_izq,
        "limite_der":    limite_der,
        "limite_existe": limite_existe,
        "f_en_a":        f_en_a,
        "continua":      continua,
        "tipo_disc":     tipo_disc,
        "justificacion": justificacion,
        "descripcion":   descripcion,
        "tabla":         tabla,
    }
