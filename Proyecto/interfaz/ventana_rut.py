import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from Rut import Procesar_Rut
from Clasificador import clasificar, razon_clasificacion, descripcion_completa


class VentanaRut(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Validador de RUT y Cónicas")
        self.geometry("700x600")

        self.label_titulo = ctk.CTkLabel(
            self, text="Ingrese su RUT", font=("Helvetica", 24, "bold")
        )
        self.label_titulo.pack(pady=30)

        self.entry_rut = ctk.CTkEntry(
            self, placeholder_text="Ej: 12345678-5", width=300, font=("Helvetica", 16)
        )
        self.entry_rut.pack(pady=10)

        self.boton_validar = ctk.CTkButton(
            self,
            text="Validar y Procesar",
            command=self.procesar_rut,
            width=250,
            height=40,
        )
        self.boton_validar.pack(pady=15)

        self.frame_resultado = ctk.CTkFrame(self)
        self.frame_resultado.pack(pady=15, padx=20, fill="both", expand=True)

        self.label_resultado = ctk.CTkLabel(
            self.frame_resultado, text="", font=("Courier", 12), justify="left"
        )
        self.label_resultado.pack(pady=10, padx=10, anchor="w")

    def procesar_rut(self):
        rut_ingresado = self.entry_rut.get()
        if not rut_ingresado:
            self.label_resultado.configure(text="Por favor ingrese un RUT")
            return

        resultado = Procesar_Rut(rut_ingresado)
        validacion = resultado["validacion"]

        if not validacion["valido"]:
            self.label_resultado.configure(
                text=f"RUT inválido: {rut_ingresado}\n\n{validacion['mensaje']}",
                text_color="red",
            )
            return

        digitos = resultado["digitos"]
        coef = resultado["coeficientes"]

        texto = f"RUT válido: {rut_ingresado}\n"
        texto += f"Dígito verificador: {validacion['dv_calculado']}\n\n"
        texto += "=" * 40 + "\n"
        texto += "DÍGITOS EXTRAÍDOS\n"
        texto += "=" * 40 + "\n"
        texto += f"d1={digitos[0]}  d2={digitos[1]}  d3={digitos[2]}  d4={digitos[3]}\n"
        texto += (
            f"d5={digitos[4]}  d6={digitos[5]}  d7={digitos[6]}  d8={digitos[7]}\n\n"
        )
        texto += "=" * 40 + "\n"
        texto += "COEFICIENTES DE LA ECUACIÓN GENERAL\n"
        texto += "=" * 40 + "\n"
        texto += f"Ax² + Cy² + Dx + Ey + F = 0\n\n"
        texto += f"A = {coef['A']}\n"
        texto += f"C = {coef['C']}\n"
        texto += f"D = {coef['D']}\n"
        texto += f"E = {coef['E']}\n"
        texto += f"F = {coef['F']}\n\n"
        texto += "=" * 40 + "\n"
        texto += "ECUACIÓN GENERAL\n"
        texto += "=" * 40 + "\n"
        texto += f"{coef['A']}x² + {coef['C']}y² + {coef['D']}x + {coef['E']}y + {coef['F']} = 0\n\n"

        tipo = clasificar(coef["A"], coef["C"], coef["D"], coef["E"], coef["F"])
        razon = razon_clasificacion(coef["A"], coef["C"])

        texto += "=" * 40 + "\n"
        texto += "CLASIFICACIÓN DE LA CÓNICA\n"
        texto += "=" * 40 + "\n"
        texto += f"Tipo: {tipo.upper()}\n\n"
        texto += "Razón:\n"
        texto += razon

        self.label_resultado.configure(text=texto, text_color="green")
