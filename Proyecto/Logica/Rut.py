# ----------------------------------------------------------
# Este módulo se encarga de la validación del RUT
# y la construcción de coeficientes a partir de este mismo
# ----------------------------------------------------------

# Tabla de traducción reutilizable para eliminar puntos y guiones del RUT
_Tabla_Limpieza = str.maketrans("", "", ".-")

# Secuencia de multiplicadores usada en el cálculo del Módulo 11
_secuencia = (2, 3, 4, 5, 6, 7)


#----------------------------------------------------------
# Elimina puntos, guiones y espacios del RUT,
# y convierte todo a mayúsculas para normalizar el formato
#----------------------------------------------------------
def limpiar_rut(rut):
    return rut.strip().translate(_Tabla_Limpieza).upper()


#----------------------------------------------------------
# Calcula el dígito verificador esperado usando el algoritmo
# oficial del Módulo 11, utilizado por el Registro Civil de Chile.
# Recibe el cuerpo numérico del RUT (sin DV) como string.
# Retorna: "K", "0", o un dígito del 1 al 9 como string.
#----------------------------------------------------------
def Modulo11(Cuerpo):
    # Multiplica cada dígito (de derecha a izquierda) por su factor de la secuencia
    suma = sum(
        int(d) * _secuencia[i % 6]
        for i, d in enumerate(reversed(Cuerpo))
    )
    # Calcula el DV restando el residuo de la división por 11
    DV = 11 - (suma % 11)
    # Casos especiales: 11 → "0", 10 → "K", resto → dígito normal
    return "0" if DV == 11 else "K" if DV == 10 else str(DV)


#----------------------------------------------------------
# Valida un RUT completo de forma integral:
# limpia el formato, separa el cuerpo del DV,
# verifica que el cuerpo sea numérico, que el DV sea válido,
# y compara el DV ingresado con el calculado por Módulo 11.
# Retorna un diccionario con el resultado de la validación.
#----------------------------------------------------------
def Valid_Rut(Rut):
    Rut_Limpio = limpiar_rut(Rut)

    # Estructura de resultado con valores por defecto
    Resultado = {
        "valido": False,
        "cuerpo": "",
        "dv_dado": "",
        "dv_calculado": "",
        "mensaje": ""
    }

    # Verificación mínima de longitud (al menos 1 dígito + 1 DV)
    if len(Rut_Limpio) < 2:
        Resultado["mensaje"] = "Rut demasiado corto."
        return Resultado

    # Separar el cuerpo (todos los caracteres menos el último) y el DV (último carácter)
    Cuerpo, DV_Dado = Rut_Limpio[:-1], Rut_Limpio[-1]
    Resultado["cuerpo"] = Cuerpo
    Resultado["dv_dado"] = DV_Dado

    # Verificar que el cuerpo contenga solo dígitos
    if not Cuerpo.isdigit():
        Resultado["mensaje"] = f"El cuerpo '{Cuerpo}' no es válido."
        return Resultado

    # Verificar que el DV sea un dígito del 0 al 9 o la letra K
    if DV_Dado not in "0123456789K":
        Resultado["mensaje"] = f"Dígito verificador '{DV_Dado}' no válido."
        return Resultado

    # Calcular el DV esperado y compararlo con el ingresado
    DV_Calc = Modulo11(Cuerpo)
    Resultado["dv_calculado"] = DV_Calc

    if DV_Dado == DV_Calc:
        Resultado["valido"] = True
        Resultado["mensaje"] = f"RUT válido. DV correcto: {DV_Calc}"
    else:
        Resultado["mensaje"] = (
            f"RUT inválido. DV ingresado: {DV_Dado} — DV esperado: {DV_Calc}"
        )

    return Resultado


#----------------------------------------------------------
# Extrae los primeros 8 dígitos del cuerpo del RUT.
# Si el cuerpo tiene menos de 8 dígitos, rellena con ceros
# a la izquierda para mantener una longitud fija.
# Retorna una lista de enteros.
#----------------------------------------------------------
def Extrae_Digitos(Rut):
    # Eliminar DV, rellenar con ceros y tomar solo los primeros 8 dígitos
    Cuerpo = limpiar_rut(Rut)[:-1].zfill(8)[:8]
    return [int(c) for c in Cuerpo]


#----------------------------------------------------------
# Construye los coeficientes A, C, D, E, F de la ecuación
# general de una cónica a partir de los dígitos del RUT.
# Cada coeficiente se forma con una operación específica
# sobre los dígitos d1 a d7.
# Retorna un diccionario con los coeficientes y su descripción.
#----------------------------------------------------------
def construye_coeficientes(Digitos):
    # Desempaquetar los primeros 7 dígitos (d8 se ignora si sobra)
    d1, d2, d3, d4, d5, d6, d7, *_ = Digitos

    # Cálculo de cada coeficiente según la fórmula de la cónica
    A = d1 + 1
    C = d2 + 1
    D = -(d3 * 2)
    E = -(d4 * 2)
    F = d5 + d6 - d7

    # Texto explicativo del proceso de cálculo de cada coeficiente
    Descripcion = (
        f"A = d1 + 1 = {d1} + 1 = {A}\n"
        f"C = d2 + 1 = {d2} + 1 = {C}\n"
        f"D = -(d3 x 2) = -({d3} x 2) = {D}\n"
        f"E = -(d4 x 2) = -({d4} x 2) = {E}\n"
        f"F = d5 + d6 - d7 = {d5} + {d6} - {d7} = {F}"
    )

    return {"A": A, "C": C, "D": D, "E": E, "F": F, "descripcion": Descripcion}


#----------------------------------------------------------
# Función principal que integra todo el flujo:
# valida el RUT y, si es válido, extrae sus dígitos
# y construye los coeficientes de la cónica.
# Retorna un diccionario con validación, dígitos y coeficientes.
#----------------------------------------------------------
def Procesar_Rut(Rut):
    Validacion = Valid_Rut(Rut)

    # Si el RUT no es válido, retornar solo la validación sin coeficientes
    if not Validacion["valido"]:
        return {"validacion": Validacion, "digitos": [], "coeficientes": {}}

    # Extraer dígitos y construir coeficientes solo si el RUT es válido
    Digitos = Extrae_Digitos(Rut)
    return {
        "validacion": Validacion,
        "digitos": Digitos,
        "coeficientes": construye_coeficientes(Digitos)
    }


# ------------------------------------------------------------------
# Testeo
# ------------------------------------------------------------------

if __name__ == "__main__":
    ruts_prueba = [
        "12.345.678-9",
        "17.654.321-K",
        "11111111-1",
        "99999999-9",
    ]

    for rut in ruts_prueba:
        print("=" * 50)
        print(f"RUT ingresado : {rut}")

        resultado = Procesar_Rut(rut)
        v = resultado["validacion"]

        print(f"Limpio        : {limpiar_rut(rut)}")
        print(f"Válido        : {v['valido']}")
        print(f"Mensaje       : {v['mensaje']}")

        if resultado["digitos"]:
            print(f"Dígitos       : {resultado['digitos']}")
            print("Coeficientes  :")
            print(resultado["coeficientes"]["descripcion"])