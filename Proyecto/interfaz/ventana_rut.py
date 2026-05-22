import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from Rut import Procesar_Rut
from Clasificador import clasificar, razon_clasificacion, descripcion_completa

from interfaz.ventana_conicas import VentanaConicas
from interfaz.ventana_limites import VentanaLimites
from interfaz.graficador import graficar_conica, graficar_limites

class VentanaRut(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Validador de RUT y Cónicas")
        self.geometry("900x700")  
        self.configure(fg_color="#0F1117") 

        self.tabs = ctk.CTkTabview(
            self,
            fg_color="#0F1117",
            segmented_button_selected_color="#5E81F4",
            segmented_button_unselected_color="#1A1D2E",
            text_color="#E8EAF6"
        )
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_rut = self.tabs.add("Validacion RUT")
        self.tab_conicas = self.tabs.add("Cónicas")
        self.tab_limites = self.tabs.add("Límites")

        # CAMBIO: A partir de aqui, en vez de empaquetar los botones en 'self' (la ventana entera), 
        # los empaquetamos específicamente dentro de 'self.tab_rut' para que solo se vean en la primera pestaña.
        self.label_titulo = ctk.CTkLabel(
            self.tab_rut, text="Ingrese su RUT", font=("Helvetica", 24, "bold")
        )
        self.label_titulo.pack(pady=20)

        self.entry_rut = ctk.CTkEntry(
            self.tab_rut, placeholder_text="Ej: 12345678-5", width=300, font=("Helvetica", 16)
        )
        self.entry_rut.pack(pady=10)

        self.boton_validar = ctk.CTkButton(
            self.tab_rut, text="Validar y Procesar", 
            command=self.procesar_rut, 
            width=250, 
            height=40
        )
        self.boton_validar.pack(pady=15)

        self.frame_resultado = ctk.CTkFrame(self.tab_rut, fg_color="#1A1D2E")
        self.frame_resultado.pack(pady=15, padx=20, fill="both", expand=True)

        self.label_resultado = ctk.CTkLabel(
            self.frame_resultado, text="", font=("Courier", 13), justify="left"
        )
        self.label_resultado.pack(pady=10, padx=10, anchor="w")

        # CAMBIO: Inicializamos las otras dos pantallas y las "metemos" dentro de sus pestañas correspondientes.
        # Al hacer esto, permanecen ocultas hasta que el usuario hace clic arriba.
        self.frame_conicas = VentanaConicas(self.tab_conicas)
        self.frame_conicas.pack(fill="both", expand=True)

        self.frame_limites = VentanaLimites(self.tab_limites)
        self.frame_limites.pack(fill="both", expand=True)

        self.frame_conicas.on_grafica_solicitada = graficar_conica
        self.frame_limites.on_grafica_solicitada = graficar_limites

    def procesar_rut(self):
        rut_ingresado = self.entry_rut.get()
        if not rut_ingresado:
            self.label_resultado.configure(text="Por favor ingrese un RUT", text_color="white")
            return

        resultado = Procesar_Rut(rut_ingresado)
        validacion = resultado["validacion"]

        if not validacion["valido"]:
            self.label_resultado.configure(
                text=f"RUT inválido: {rut_ingresado}\n\n{validacion['mensaje']}",
                text_color="#F44336"
            )
            return

        digitos = resultado["digitos"]
        coef = resultado["coeficientes"]

        # Formateo del texto
        texto = f"RUT válido: {rut_ingresado}\n"
        texto += f"Dígito verificador: {validacion['dv_calculado']}\n\n"
        texto += "=" * 40 + "\n"
        texto += "DÍGITOS EXTRAÍDOS\n"
        texto += "=" * 40 + "\n"
        texto += f"d1={digitos[0]}  d2={digitos[1]}  d3={digitos[2]}  d4={digitos[3]}\n"
        texto += f"d5={digitos[4]}  d6={digitos[5]}  d7={digitos[6]}  d8={digitos[7]}\n\n"
        texto += "=" * 40 + "\n"
        texto += "COEFICIENTES DE LA ECUACIÓN GENERAL\n"
        texto += "=" * 40 + "\n"
        texto += f"A={coef['A']} | C={coef['C']} | D={coef['D']} | E={coef['E']} | F={coef['F']}\n\n"

        tipo = clasificar(coef["A"], coef["C"], coef["D"], coef["E"], coef["F"])
        razon = razon_clasificacion(coef["A"], coef["C"])

        texto += "=" * 40 + "\n"
        texto += "CLASIFICACIÓN DE LA CÓNICA\n"
        texto += "=" * 40 + "\n"
        texto += f"Tipo: {tipo.upper()}\n"

        self.label_resultado.configure(text=texto, text_color="#4CAF50")

        # CAMBIO: COMUNICACIÓN ENTRE MÓDULOS
        # Aquí agarramos los datos que acabamos de calcular en esta función (los coeficientes y los dígitos)
        # y se los 'lanzamos' a los otros dos frames que creamos arriba. 
        # Sin estas dos líneas, las pestañas de Cónicas y Límites estarían siempre en blanco.
        
        self.frame_conicas.cargar_coeficientes(coef["A"], coef["C"], coef["D"], coef["E"], coef["F"])
        self.frame_limites.cargar_digitos(digitos)
