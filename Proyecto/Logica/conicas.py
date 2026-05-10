#-----------------------------------------------------------------------------------------------
#esta funcion se encarga de conseguir el valor absoluto de los numeros que le entreguemos 
#-------------------------------------------------------------------------------------------------

def Valor_Absoluto(n):
    return n if n >= 0 else -n


def raiz(n, tolerancia=1e-10):
    #/////////////////////////////////////////////////////////////////////
    #raiz cuadrada por newton-Raphson con criterio de convergencia real
    #/////////////////////////////////////////////////////////////////////
    if n < 0:
        return None
    if n == 0:
        return 0.0
    
    x= n if n>=1 else 1.0 #[estimacion inicial segun magnitud]
    for _ in range(200):
        x_nuevo = ( x + n / x )/2
        if Valor_Absoluto(x_nuevo -x) < tolerancia:
            return x_nuevo
        x = x_nuevo
    return x

def redondeo(n, decimales=4):
    if n is None:
        return None
    factor = 10 ** decimales
    signo = 1 if n >= 0 else -1
    return signo * int(Valor_Absoluto(n)* factor + 0.5) / factor

def _fmt(n):
    #""""""""""""""""""""""""""""""""""""""""""""""""""""
    #formatea un numero para los mensajes de los pasos
    #""""""""""""""""""""""""""""""""""""""""""""""""""""
    
    if n is None:
        return "∅"
    r = redondeo(n)
    return int(r) if r == int(r) else r
#_________________________________________________________________________________________________________

def completar_cuadrado(A,B):
    h = -B / (2 * A)
    resta = (B ** 2) / (4 * A)
    return h, resta

#_____________________________
#Transformar a forma general
#_____________________________

def _transformar(A,C,D,E,F):
    pasos=[]
    lado_derecho=-F
    pasos.append(f"Pasamos F al otro lado: -({_fmt(F)})= {_fmt(lado_derecho)}")
    
    resta_x = resta_y = 0
    
    if A != 0:
        h, resta_x = completar_cuadrado(A,D)
        lado_derecho += resta_x
        pasos.append(f"completar cuadrado en x [A={_fmt(A)}, D={_fmt(h)}]\n"
                     f"H = -D/(2A) = -({_fmt(D)})/(2*{_fmt(A)}) = {_fmt(h)}\n"
                     f"sobrante = D ** 2 / (4A) = {_fmt(D)}**2 / (4*{_fmt(A)}) = {_fmt(resta_x)}")
        
    else:
        h = 0
    if C != 0:
        k, resta_y = completar_cuadrado(C,E)
        lado_derecho += resta_y
        pasos.append(f"completar cuadrado en y [A={_fmt(C)}, D={_fmt(E)}]\n"
                     f"H = -E/(2C) = -({_fmt(E)})/(2*{_fmt(C)}) = {_fmt(k)}\n"
                     f"sobrante = E ** 2 / (4C) = {_fmt(E)}**2 / (4*{_fmt(C)}) = {_fmt(resta_y)}")

    else:
         k = 0
         
    pasos.append(
        f"Lado derecho = -F + sobrante_x + sobrante_y \n"
        f"= {_fmt(-F)} + {_fmt(resta_x)} + {_fmt(resta_y)} = {_fmt(lado_derecho)}"
    )        
    return h, k, lado_derecho, pasos

#/////////////////////////
#diccionario de error
#/////////////////////////

def _error(tipo, msg, pasos=None):
    return{"tipo":tipo,"error":msg,"pasos":pasos or []}


#___________________________________________________
# circunferancia
#___________________________________________________

def circunferencia(A,C,D,E,F):
    if A == 0 or A !=C:
        return _error("circunferencia", "Se requiere A = C =! 0")
    h, k, ld,pasos = _transformar(A,C,D,E,F)
    r2 = ld / A
    pasos.append(f"Normalizamos + A = {_fmt(A)}: r **2 = {_fmt(ld)}/{_fmt(A)} = {_fmt(r2)}")
    
    if r2 <= 0:
        return _error("circunferencia",
                      f"r**2 = {_fmt(r2)}<= 0 -> no existe circunferencia   REAL", pasos)
        
    r = raiz(r2)
    forma= f"(x - {_fmt(h)}) ** 2  + (y - {_fmt(k)}) ** 2 = {_fmt(r2)}"
    pasos.append(f"r = sqr({_fmt(r2)}) = {_fmt(r)} (newthon-raphson)")
    pasos.append(f"Forma conica: {forma}")
    
    return {
        "tipo":"circunferencia",
        "centro":(redondeo(h),redondeo(k)),
        "radio":redondeo(r),
        "r2":redondeo(r2),
        "forma_canonica":forma,
        "pasos":pasos,
        "error":None,
    }
    
    
#________________________
#Elipse
#_______________________