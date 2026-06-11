_Terminos = [("x**2", "A"), ("y**2", "C"), ("x", "D"), ("y", "E"), ("", "F")]


# --------------------------------------------------------------
# retorna la representacion de in termino individual
# -----------------------------------------------------------------
def _Formatear_Termino(coef, sufijo, primero):
    if coef == 0:
        return None
    abs_c = abs(coef)
    signo = "" if (primero and coef > 0) else ("+ " if coef > 0 else "- ")

    # ________________________________________________________
    # Coeficiente visible= omitimos el 1 en su caso especifico
    # ________________________________________________________

    if sufijo and abs_c == 1:
        cuerpo = sufijo
    elif sufijo:
        cuerpo = f"{abs_c}{sufijo}"
    else:
        cuerpo = str(abs_c)
    return signo + cuerpo


# ------------------------------------------------------------------
# transformamos los coeficientes en un string legible de la ecuacion
# ------------------------------------------------------------------
def _formatear_ecuacion(A, C, D, E, F):
    valores = {"A": A, "C": C, "D": D, "E": E, "F": F}
    partes = []

    for sufijo, clave in _Terminos:
        termino = _Formatear_Termino(valores[clave], sufijo, not partes)
        if termino is not None:
            partes.append(termino)

    return ("".join(partes) if partes else "0") + "= 0"


# ________________________________________________
# Nucleo de la clasificacion toda la logica real vivira aqui
# elresto de funciones seran quienes invoque esto
# _______________________________________________


def _clasificar_iterno(A, C):
    # regresara (tipo, Razon) a partir solo de A y C es el unico punto donde
    # se evaluan las condiciones de clasificacion.
    producto = A * C
    if A == 0 and C == 0:
        return (
            "Invalida",
            f"A = {A} y C = {C}.\n"
            "Como ambos coeficientes cuadraticos son 0, "
            "la ecuacion no representa una conica real valida.\n"
            "-> Ecuacion NO VALIDA",
        )
    if A == 0:
        return (
            "parabola",
            f"A = {A}, C = {C}.\n"
            "Como A = 0, no existe termino en x ** 2 .\n"
            "Solo Hay un termino cuadratico  (en y ** 2). \n"
            "-> la conica es una parabola con eje horizontal.",
        )

    if C == 0:
        return (
            "parabola",
            f"A={A}, C={C}.\n"
            "como C = 0, no existe termino en y ** 2 .\n"
            "solo hay un termino cuadratico (en x ** 2). \n"
            "-> la conica es una parabola con eje vertical.",
        )
    if A == C:
        return (
            "circunferencia",
            f"A={A}, C={C}.\n"
            "como A = C y ambos son distintos de 0,\n"
            "los coeficientes de x ** 2 e y ** 2 son iguales .\n"
            "-> la conica es una circunferencia.",
        )

    if producto > 0:
        return (
            "elipse",
            f"A={A}, C={C}.\n"
            f"como A =/ C pero A * C = {A} * {C} = {producto} > 0,\n"
            "ambos coeficientes tienen el mismo signo pero son distos.\n"
            "-> la conica es una elipse.",
        )

    # producto < 0 (unico caso restante)
    return (
        "hiperbola",
        f"A = {A}, C = {C}.\n"
        f"como A * C = {A} * {C} = {producto} < 0,\n"
        "los coeficientes tiene signos opuestos. \n"
        "-> la conica es una hiperbola.",
    )


# -------------------------------------------
# Api Publica
# --------------------------------------------
def clasificar(A, C, D, E, F):
    tipo, _ = _clasificar_iterno(A, C)
    return tipo


def es_Invalida(A, C):
    return A == 0 and C == 0


def razon_clasificacion(A, C):
    _, razon = _clasificar_iterno(A, C)
    return razon


def descripcion_completa(A, C, D, E, F):
    tipo, razon = _clasificar_iterno(A, C)
    return {
        "tipo": tipo,
        "razon": razon,
        "valida": tipo != "Invalida",
        "ecuacion": _formatear_ecuacion(A, C, D, E, F),
    }


# ====================================================================
# BLOQUE DE PRUEBA
# ====================================================================
if __name__ == "__main__":
    casos = [
        # (A,C,D,E,F tipo esperado)
        (1, 1, -4, 6, 9, "circunferencia"),
        (4, 9, -16, 18, -11, "elipse"),
        (0, 1, -8, 0, 0, "parabola"),
        (1, 0, 0, -4, 0, "parabola"),
        (4, -9, 0, 0, -36, "hiperbola"),
        (0, 0, 1, 1, 0, "Invalida"),
    ]

    print("=" * 55)
    print("Testeo Del clasificador")
    print("=" * 55)

    for A, C, D, E, F, esperado in casos:
        resultado = descripcion_completa(A, C, D, E, F)
        tipo = resultado["tipo"]
        ok = (
            "Correctooooo!!!!!!!!!!"
            if tipo == esperado
            else "neeeeh Esta mal, ¿en que esta mal si puse todo bien?, esta mal en algo"
        )
        print(f"\n{ok} Ecuacion: {resultado['ecuacion']}")
        print(f"    tipo Obtenido : {tipo}     ")
        print(f"    tipo esperado : {esperado} ")
        print(f"    razon         : {resultado}")
        print("-" * 55)