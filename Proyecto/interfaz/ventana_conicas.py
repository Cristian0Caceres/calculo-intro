# =============================================================================
# interfaz/ventana_conicas.py
# Frame modular para el análisis de secciones cónicas.
# Se conecta con:
#   Logica.conicas      → analizar_conica(A,C,D,E,F)
#   Logica.Clasificador → descripcion_completa(A,C,D,E,F)
#
# Recibe los coeficientes ya calculados por ventana_rut.py y los muestra en:
#   1. Encabezado: ecuación general + tipo de cónica
#   2. Panel Principal: desarrollo matemático paso a paso (CTkTextbox scrollable)
#   3. Zona inferior: contenedor reservado para graficador.py
# =============================================================================

import sys
import os
import customtkinter as ctk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from conicas      import analizar_conica
from Clasificador import descripcion_completa


_FONDO         = "#0F1117"
_PANEL         = "#1A1D2E"
_ACENTO        = "#5E81F4"
_ACENTO2       = "#F4A261"
_TEXTO         = "#E8EAF6"
_DIMMED        = "#7B83B0"
_ENTRY_FONDO   = "#12152A"
_BORDE         = "#2E3254"


_F_EQ   = ("Courier New", 15, "bold")
_F_TIPO = ("Georgia", 17, "bold")
_F_BOLD = ("Segoe UI", 11, "bold")
_F_MONO = ("Courier New", 11)

_ICONOS = {
    "circunferencia": "◎",
    "elipse":         "⬭",
    "parabola":       "∩",
    "hiperbola":      "⌓",
}

class VentanaConicas(ctk.CTkFrame):
    """
    Frame reutilizable que muestra el análisis completo de una cónica.

    Uso desde ventana_rut.py:
        frame = VentanaConicas(parent)
        frame.pack(fill="both", expand=True)
        frame.cargar_coeficientes(A, C, D, E, F)
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_FONDO, **kwargs)

        self._A = self._C = self._D = self._E = self._F = 0
        self._datos = {}

        self._construir_encabezado()
        self._construir_cuerpo()
        self._construir_zona_grafica()

    # DISEÑO DE LA INTERFAZ

    def _construir_encabezado(self):
        panel = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        panel.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(panel, text="Ecuacion General  Ax² + Cy² + Dx + Ey + F = 0",
                     font=("Segoe UI", 11), text_color=_DIMMED
                     ).pack(anchor="w", padx=18, pady=(12, 0))

        self._lbl_ec = ctk.CTkLabel(panel, text="—", font=_F_EQ,
                                    text_color=_ACENTO, wraplength=860, justify="left")
        self._lbl_ec.pack(anchor="w", padx=18, pady=(2, 4))

        ctk.CTkFrame(panel, height=1, fg_color=_BORDE).pack(fill="x", padx=18, pady=(0, 6))

        self._lbl_tipo = ctk.CTkLabel(panel, text="—", font=_F_TIPO, text_color=_ACENTO2)
        self._lbl_tipo.pack(anchor="w", padx=18, pady=(0, 14))

    def _construir_cuerpo(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=18, pady=6)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(0, weight=1)

        self._construir_pasos(cont)

    def _construir_pasos(self, padre):
        marco = ctk.CTkFrame(padre, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.grid(row=0, column=0, sticky="nsew", padx=0)

        ctk.CTkLabel(marco, text="Desarrollo Matematico — Completacion del Cuadrado",
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
        ctk.CTkLabel(fila, text="Visualizacion Grafica",
                     font=_F_BOLD, text_color=_TEXTO).pack(side="left")
        self._btn_graf = ctk.CTkButton(fila, text="Generar Grafica", font=("Segoe UI", 11, "bold"),
                                       fg_color="#3A3F6B", hover_color="#4A509E",
                                       width=150, command=self._solicitar_grafica,
                                       state="disabled")
        self._btn_graf.pack(side="right")

        self.zona_grafica = ctk.CTkFrame(marco, fg_color=_ENTRY_FONDO,
                                         corner_radius=8, height=200)
        self.zona_grafica.pack(fill="x", padx=14, pady=(8, 14))
        self.zona_grafica.pack_propagate(False)

        self._ph_graf = ctk.CTkLabel(self.zona_grafica,
                                     text="La grafica aparecera aqui.",
                                     font=("Segoe UI", 11), text_color=_DIMMED)
        self._ph_graf.place(relx=0.5, rely=0.5, anchor="center")

    # API PÚBLICA

    def cargar_coeficientes(self, A, C, D, E, F):
        """Carga nuevos coeficientes y refresca toda la vista."""
        self._A, self._C, self._D, self._E, self._F = A, C, D, E, F
        self._limpiar_entradas()
        self._analizar()

    # LÓGICA INTERNA

    def _analizar(self):
        A, C, D, E, F = self._A, self._C, self._D, self._E, self._F

        info = descripcion_completa(A, C, D, E, F)
        tipo = info.get("tipo", "—")
        icono = _ICONOS.get(tipo, "?")

        self._lbl_ec.configure(text=info.get("ecuacion", "—"))
        self._lbl_tipo.configure(text=f"{icono}  Cónica: {tipo.capitalize()}")

        self._datos = analizar_conica(A, C, D, E, F)

        if self._datos.get("error"):
            self._escribir_textbox(f"⚠  Error:\n\n{self._datos['error']}\n")
            return

        self._poblar_pasos(self._datos.get("pasos", []))
        self._btn_graf.configure(state="normal")

    def _poblar_pasos(self, pasos):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        if not pasos:
            self._textbox.insert("end", "No se generaron pasos.\n")
        else:
            for i, paso in enumerate(pasos, 1):
                self._textbox.insert("end", f"▸ Paso {i}\n")
                for linea in paso.strip().splitlines():
                    self._textbox.insert("end", f"    {linea}\n")
                self._textbox.insert("end", "\n")
        self._textbox.configure(state="disabled")

    def _escribir_textbox(self, texto):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("end", texto)
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
