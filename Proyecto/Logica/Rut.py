# =============================================================================
# Rut.py — Validación de RUT y construcción de coeficientes de cónica
# =============================================================================
# La construcción de coeficientes sigue EXACTAMENTE la fórmula del enunciado:
#
#   A = (d1+d2)/v    B = (d3+d4)/v    C = -(d5+d6)
#   D = -(d7+d8)     E =  d1+d3+d5+d7
#
# donde v se obtiene del dígito verificador (DV).
#
# La nomenclatura interna del proyecto (usada en conicas.py y Clasificador.py)
# mapea así respecto al PDF:
#
#   PDF → interno
#   A   → A   (coeficiente de x²)
#   B   → C   (coeficiente de y²)
#   C   → D   (coeficiente de x)
#   D   → E   (coeficiente de y)
#   E   → F   (término constante)
# =============================================================================

_Tabla_Limpieza = str.maketrans("", "", ".-")
_secuencia      = (2, 3, 4, 5, 6, 7)


def limpiar_rut(rut):
    return rut.strip().translate(_Tabla_Limpieza).upper()


def Modulo11(cuerpo):
    """
    Algoritmo oficial del Módulo 11 para calcular el DV esperado.
    Multiplica cada dígito (de derecha a izquierda) por la secuencia 2-7
    de forma cíclica, suma los productos y calcula: DV = 11 − (suma % 11).
    Casos especiales: resultado 11 → '0', resultado 10 → 'K'.
    """
    suma = sum(
        int(d) * _secuencia[i % 6]
        for i, d in enumerate(reversed(cuerpo))
    )
    dv = 11 - (suma % 11)
    return "0" if dv == 11 else "K" if dv == 10 else str(dv)


def Valid_Rut(rut):
    rut_limpio = limpiar_rut(rut)
    resultado  = {"valido": False, "cuerpo": "", "dv_dado": "",
                  "dv_calculado": "", "mensaje": ""}

    if len(rut_limpio) < 2:
        resultado["mensaje"] = "RUT demasiado corto."
        return resultado

    cuerpo, dv_dado = rut_limpio[:-1], rut_limpio[-1]
    resultado["cuerpo"]   = cuerpo
    resultado["dv_dado"]  = dv_dado

    if not cuerpo.isdigit():
        resultado["mensaje"] = f"El cuerpo '{cuerpo}' contiene caracteres no numéricos."
        return resultado

    if dv_dado not in "0123456789K":
        resultado["mensaje"] = f"Dígito verificador '{dv_dado}' no es válido."
        return resultado

    dv_calc = Modulo11(cuerpo)
    resultado["dv_calculado"] = dv_calc

    if dv_dado == dv_calc:
        resultado["valido"]  = True
        resultado["mensaje"] = f"RUT válido. DV correcto: {dv_calc}"
    else:
        resultado["mensaje"] = (
            f"RUT inválido. DV ingresado: {dv_dado} — DV esperado: {dv_calc}"
        )
    return resultado


def Extrae_Digitos(rut):
    """
    Devuelve lista de 8 enteros con los dígitos del cuerpo del RUT.
    Si el cuerpo tiene menos de 8 cifras se rellena con ceros a la izquierda.
    """
    cuerpo = limpiar_rut(rut)[:-1].zfill(8)[:8]
    return [int(c) for c in cuerpo]


def _calcular_v(dv_str):
    """
    Convierte el dígito verificador en la variable auxiliar v:
        DV = 'K' → v = 10
        DV = '0' → v = 11
        DV = '1'..'9' → v = int(DV)
    """
    if dv_str == "K":
        return 10
    if dv_str == "0":
        return 11
    return int(dv_str)


def construye_coeficientes(digitos, dv_str):
    """
    Construye los coeficientes de la ecuación general de la cónica
    siguiendo el enunciado (Fase 1):

        A·x² + B·y² + C·x + D·y + E = 0   (nomenclatura del PDF)

    Fórmulas base:
        A = (d1+d2) / v
        B = (d3+d4) / v
        C = -(d5+d6)
        D = -(d7+d8)
        E =  d1+d3+d5+d7

    Ajustes (mutuamente excluyentes entre sí en el orden indicado):
        1. Si d1 == d2          → B = A              (circunferencia forzada)
        2. Si (d5+d6) % 3 == 0 → parábola forzada:
               d7 par   → B = 0
               d7 impar → A = 0
        Si NO se aplicó ninguno de los ajustes anteriores:
        3. Si d8 es impar       → B = −B             (permite hipérbola)

    Los coeficientes se devuelven con la NOMENCLATURA INTERNA del proyecto
    para ser compatibles con conicas.py y Clasificador.py:
        A_int = A del PDF  (coef x²)
        C_int = B del PDF  (coef y²)   ← nombre interno 'C'
        D_int = C del PDF  (coef x)    ← nombre interno 'D'
        E_int = D del PDF  (coef y)    ← nombre interno 'E'
        F_int = E del PDF  (constante) ← nombre interno 'F'
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digitos[:8]
    v = _calcular_v(dv_str)

    # ── Valores base según fórmulas del enunciado ─────────────────────────────
    A = (d1 + d2) / v
    B = (d3 + d4) / v
    C = -(d5 + d6)
    D = -(d7 + d8)
    E =  d1 + d3 + d5 + d7

    pasos_ajuste   = []
    ajuste_aplicado = False   # bandera para el ajuste 3

    # ── Ajuste 1: circunferencia forzada ──────────────────────────────────────
    if d1 == d2:
        B = A
        ajuste_aplicado = True
        pasos_ajuste.append(
            f"Ajuste 1: d1 = d2 = {d1}  →  B = A = {A:.4f}  (circunferencia forzada)"
        )

    # ── Ajuste 2: parábola forzada ────────────────────────────────────────────
    elif (d5 + d6) % 3 == 0:
        ajuste_aplicado = True
        if d7 % 2 == 0:
            B = 0
            pasos_ajuste.append(
                f"Ajuste 2: (d5+d6) = {d5+d6} es múltiplo de 3 y d7 = {d7} es par  "
                f"→  B = 0  (parábola de eje vertical)"
            )
        else:
            A = 0
            pasos_ajuste.append(
                f"Ajuste 2: (d5+d6) = {d5+d6} es múltiplo de 3 y d7 = {d7} es impar  "
                f"→  A = 0  (parábola de eje horizontal)"
            )

    # ── Ajuste 3: hipérbola (solo si no hubo ajuste 1 ni 2) ──────────────────
    if not ajuste_aplicado and d8 % 2 != 0:
        B = -B
        pasos_ajuste.append(
            f"Ajuste 3: d8 = {d8} es impar  →  B = −B = {B:.4f}  (permite hipérbola)"
        )

    if not pasos_ajuste:
        pasos_ajuste.append("Sin ajustes: se mantienen los valores base.")

    # ── Descripción paso a paso para la interfaz ──────────────────────────────
    descripcion = (
        f"Variable auxiliar:\n"
        f"  DV = '{dv_str}'  →  v = {v}\n\n"
        f"Fórmulas base (nomenclatura del enunciado):\n"
        f"  A = (d1+d2)/v = ({d1}+{d2})/{v} = {(d1+d2)/v:.4f}\n"
        f"  B = (d3+d4)/v = ({d3}+{d4})/{v} = {(d3+d4)/v:.4f}\n"
        f"  C = -(d5+d6)  = -({d5}+{d6})    = {-(d5+d6)}\n"
        f"  D = -(d7+d8)  = -({d7}+{d8})    = {-(d7+d8)}\n"
        f"  E =  d1+d3+d5+d7 = {d1}+{d3}+{d5}+{d7} = {d1+d3+d5+d7}\n\n"
        f"Ajustes aplicados:\n"
        + "\n".join(f"  • {p}" for p in pasos_ajuste) +
        f"\n\nCoeficientes finales (nomenclatura interna del proyecto):\n"
        f"  A (coef x²) = {A:.4f}\n"
        f"  C (coef y²) = {B:.4f}\n"
        f"  D (coef x)  = {C}\n"
        f"  E (coef y)  = {D}\n"
        f"  F (cte)     = {E}\n"
    )

    return {
        "A": A,   # coef x²  (A del PDF)
        "C": B,   # coef y²  (B del PDF) — nombre interno 'C'
        "D": C,   # coef x   (C del PDF) — nombre interno 'D'
        "E": D,   # coef y   (D del PDF) — nombre interno 'E'
        "F": E,   # cte      (E del PDF) — nombre interno 'F'
        "v": v,
        "descripcion": descripcion,
    }


def Procesar_Rut(rut):
    """
    Flujo completo: valida el RUT y, si es válido, extrae dígitos
    y construye los coeficientes de la cónica.
    """
    validacion = Valid_Rut(rut)
    if not validacion["valido"]:
        return {"validacion": validacion, "digitos": [], "coeficientes": {}}

    digitos = Extrae_Digitos(rut)
    dv_str  = limpiar_rut(rut)[-1]

    return {
        "validacion":   validacion,
        "digitos":      digitos,
        "coeficientes": construye_coeficientes(digitos, dv_str),
    }


# =============================================================================
# BLOQUE DE PRUEBA
# =============================================================================
if __name__ == "__main__":
    ruts_prueba = [
        ("11.111.111-1", "d1==d2 → circunferencia forzada"),
        ("22.222.222-2", "d1==d2 → circunferencia forzada"),
        ("14.765.432-6", "caso normal, verificar ajuste 3"),
        ("12.678.941-4", "(d5+d6) múltiplo de 3 → parábola"),
    ]

    for rut, caso in ruts_prueba:
        print("=" * 60)
        print(f"RUT: {rut}  [{caso}]")
        res = Procesar_Rut(rut)
        v   = res["validacion"]
        print(f"  Válido: {v['valido']}  |  {v['mensaje']}")
        if res["digitos"]:
            print(f"  Dígitos: {res['digitos']}")
            print(res["coeficientes"]["descripcion"])