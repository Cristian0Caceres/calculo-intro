def calcular_modulo11(lista_digitos):
    suma = 0
    factor = 2

    # Recorrer dígitos de derecha a izquierda
    for digito in reversed(lista_digitos):
        suma += digito * factor
        factor += 1
        if factor > 7:  # Reiniciar factor cuando llega a 7
            factor = 2

    resto = suma % 11
    resultado = 11 - resto

    # Determinar dígito verificador
    if resultado == 11:
        dv = "0"
    elif resultado == 10:
        dv = "K"
    else:
        dv = str(resultado)

    return dv