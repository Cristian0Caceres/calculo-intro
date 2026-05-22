# =============================================================================
# interfaz/ventana_limites.py
# =============================================================================
# Frame del módulo de análisis de funciones por tramos.
# Se conecta con Logica/limites.py y recibe la lista de dígitos del RUT.
#
# Muestra:
#   1. Encabezado: función generada + regla de selección del caso
#   2. Panel Principal: justificación matemática + tabla de valores
#   3. Zona reservada para la gráfica (graficador.py)
# =============================================================================

import sys
import os
import customtkinter as ctk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from limites import construir_funcion

_FONDO       = "#0F1117"
_PANEL       = "#1A1D2E"
_ACENTO      = "#5E81F4"
_ACENTO2     = "#F4A261"
_ACENTO3     = "#A8DADC"  
_TEXTO       = "#E8EAF6"
_DIMMED      = "#7B83B0"
_ENTRY_FONDO = "#12152A"
_BORDE       = "#2E3254"

_F_BOLD = ("Segoe UI", 11, "bold")
_F_MONO = ("Courier New", 11)
_F_FUNC = ("Courier New", 14, "bold")


class VentanaLimites(ctk.CTkFrame):
    """
    Frame modular del módulo de límites.

    Uso desde ventana_rut.py (o main.py):
        frame = VentanaLimites(parent)
        frame.pack(fill="both", expand=True)
        frame.cargar_digitos([d1, d2, ..., d8])
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_FONDO, **kwargs)
        self._datos   = {}
        self._digitos = []

        self._construir_encabezado()
        self._construir_cuerpo()
        self._construir_zona_grafica()


    def _construir_encabezado(self):
        panel = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        panel.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(panel, text="Funcion por Tramos generada desde el RUT",
                     font=("Segoe UI", 11), text_color=_DIMMED
                     ).pack(anchor="w", padx=18, pady=(12, 0))

        self._lbl_func = ctk.CTkLabel(panel, text="—", font=_F_FUNC,
                                      text_color=_ACENTO3, wraplength=860,
                                      justify="left")
        self._lbl_func.pack(anchor="w", padx=18, pady=(2, 4))

        ctk.CTkFrame(panel, height=1, fg_color=_BORDE).pack(fill="x", padx=18, pady=(0, 6))

        self._lbl_desc = ctk.CTkLabel(panel, text="—", font=("Segoe UI", 11),
                                      text_color=_ACENTO2, wraplength=860, justify="left")
        self._lbl_desc.pack(anchor="w", padx=18, pady=(0, 14))

    def _construir_cuerpo(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=18, pady=6)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(0, weight=1)

        self._construir_justificacion(cont)

    def _construir_justificacion(self, padre):
        marco = ctk.CTkFrame(padre, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.grid(row=0, column=0, sticky="nsew", padx=0)

        ctk.CTkLabel(marco, text="Analisis Matematico y Tabla de Valores",
                     font=_F_BOLD, text_color=_ACENTO
                     ).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkFrame(marco, height=1, fg_color=_BORDE).pack(fill="x", padx=14, pady=(0, 6))

        self._textbox = ctk.CTkTextbox(marco, font=_F_MONO, fg_color=_ENTRY_FONDO,
                                       text_color=_TEXTO, border_width=0,
                                       activate_scrollbars=True, wrap="word",
                                       state="disabled")
        self._textbox.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _construir_zona_grafica(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="x", padx=18, pady=(6, 16))

        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=14, pady=(10, 0))
        ctk.CTkLabel(fila, text="Grafica de la Funcion",
                     font=_F_BOLD, text_color=_TEXTO).pack(side="left")
        self._btn_graf = ctk.CTkButton(fila, text="Generar Gráfica",
                                       font=("Segoe UI", 11, "bold"),
                                       fg_color="#3A3F6B", hover_color="#4A509E",
                                       width=150, command=self._solicitar_grafica,
                                       state="disabled")
        self._btn_graf.pack(side="right")

        self.zona_grafica = ctk.CTkFrame(marco, fg_color=_ENTRY_FONDO,
                                          corner_radius=8, height=180)
        self.zona_grafica.pack(fill="x", padx=14, pady=(8, 14))
        self.zona_grafica.pack_propagate(False)

        self._ph_graf = ctk.CTkLabel(self.zona_grafica,
                                     text="La grafica de la funcion aparecera aqui.",
                                     font=("Segoe UI", 11), text_color=_DIMMED)
        self._ph_graf.place(relx=0.5, rely=0.5, anchor="center")


    def cargar_digitos(self, digitos):
        """
        Recibe lista de 8 enteros [d1..d8] del RUT y genera la funcion por tramos.
        """
        self._digitos = digitos
        self._limpiar_entradas()
        self._generar()

    def _generar(self):
        self._datos = construir_funcion(self._digitos)

        self._lbl_func.configure(text=self._datos["formula_str"])
        self._lbl_desc.configure(text=self._datos["descripcion"])

        self._poblar_textbox()
        self._btn_graf.configure(state="normal")

    def _poblar_textbox(self):
        d = self._datos
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")

        # justificacion
        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", "  JUSTIFICACION MATEMATICA\n")
        self._textbox.insert("end", "═" * 54 + "\n\n")
        self._textbox.insert("end", d["justificacion"] + "\n\n")

        # tabla de valores
        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", "  TABLA DE VALORES  (evidencia numerica)\n")
        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", f"{'x':>12}  {'lado':>3}  {'f(x)':>18}\n")
        self._textbox.insert("end", "-" * 38 + "\n")

        a = d["a"]
        for fila in d["tabla"]:
            marca = "← " if fila["lado"] == "←" else "→ "
            self._textbox.insert("end",
                f"{str(fila['x']):>12}  {marca:>4}  {fila['fx_str']:>18}\n")
            # linea divisoria en el punto a
            if fila["lado"] == "←" and fila is d["tabla"][3]:
                self._textbox.insert("end", f"{'· · · · · x = ' + str(a) + ' · · · · ·':^38}\n")

        self._textbox.configure(state="disabled")

    def _limpiar_entradas(self):
        self._btn_graf.configure(state="disabled")

    def _solicitar_grafica(self):
        if hasattr(self, "on_grafica_solicitada") and callable(self.on_grafica_solicitada):
            self.on_grafica_solicitada(datos=self._datos, contenedor=self.zona_grafica)
        else:
            self._ph_graf.configure(
                text="grafica",
                text_color=_ACENTO2
            )
