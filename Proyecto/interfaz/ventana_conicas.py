# =============================================================================
# interfaz/ventana_conicas.py
# Nomenclatura PDF: A·x² + B·y² + C·x + D·y + E = 0
#
# Añade:
#   • Procedimiento inverso (canónica → general) en el textbox
#   • Campos de defensa oral vacíos asociados a la gráfica
# =============================================================================

import sys, os
import customtkinter as ctk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from conicas      import analizar_conica
from Clasificador import descripcion_completa

_FONDO       = "#0F1117"
_PANEL       = "#1A1D2E"
_ACENTO      = "#5E81F4"
_ACENTO2     = "#F4A261"
_TEXTO       = "#E8EAF6"
_DIMMED      = "#7B83B0"
_ENTRY_FONDO = "#12152A"
_BORDE       = "#2E3254"

_F_EQ   = ("Courier New", 14, "bold")
_F_TIPO = ("Georgia", 16, "bold")
_F_BOLD = ("Segoe UI", 11, "bold")
_F_MONO = ("Courier New", 11)
_F_LBL  = ("Segoe UI", 10)

_ICONOS = {
    "circunferencia": "◎",
    "elipse":         "⬭",
    "parabola":       "∩",
    "hiperbola":      "⌓",
}

# Campos de defensa oral según tipo de cónica (etiqueta, clave en datos)
_CAMPOS_DEFENSA = {
    "circunferencia": [
        ("Centro (h, k):",  "centro"),
        ("Radio r:",        "radio"),
    ],
    "elipse": [
        ("Centro (h, k):",  "centro"),
        ("Semieje a:",      "a"),
        ("Semieje b:",      "b"),
        ("Focos F1 y F2:",  "focos"),
        ("Vértices:",       "vertices"),
        ("Eje mayor:",      "eje_mayor"),
    ],
    "parabola": [
        ("Vértice (h, k):", "vertice"),
        ("Foco:",           "foco"),
        ("Directriz:",      "directriz"),
        ("Eje:",            "eje"),
    ],
    "hiperbola": [
        ("Centro (h, k):",  "centro"),
        ("Semieje a:",      "a"),
        ("Semieje b:",      "b"),
        ("Focos F1 y F2:",  "focos"),
        ("Vértices:",       "vertices"),
        ("Asíntotas:",      "asintota_pendiente"),
    ],
}


class VentanaConicas(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_FONDO, **kwargs)
        self._A = self._C = self._D = self._E = self._F = 0
        self._datos = {}
        self._entradas_defensa = {}

        self._construir_encabezado()
        self._construir_cuerpo()
        self._construir_zona_defensa_y_grafica()

    # ── Encabezado ────────────────────────────────────────────────────────────

    def _construir_encabezado(self):
        panel = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        panel.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(panel,
                     text="Ecuación General  A·x² + C·y² + D·x + E·y + F = 0",
                     font=("Segoe UI", 11), text_color=_DIMMED
                     ).pack(anchor="w", padx=18, pady=(12, 0))

        self._lbl_ec = ctk.CTkLabel(panel, text="—", font=_F_EQ,
                                    text_color=_ACENTO, wraplength=860, justify="left")
        self._lbl_ec.pack(anchor="w", padx=18, pady=(2, 4))

        ctk.CTkFrame(panel, height=1, fg_color=_BORDE).pack(fill="x", padx=18, pady=(0, 6))

        self._lbl_tipo = ctk.CTkLabel(panel, text="—", font=_F_TIPO, text_color=_ACENTO2)
        self._lbl_tipo.pack(anchor="w", padx=18, pady=(0, 14))

    # ── Cuerpo: desarrollo matemático ────────────────────────────────────────

    def _construir_cuerpo(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="both", expand=True, padx=18, pady=6)

        ctk.CTkLabel(marco,
                     text="Desarrollo Matemático — General → Canónica → General",
                     font=_F_BOLD, text_color=_ACENTO
                     ).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkFrame(marco, height=1, fg_color=_BORDE).pack(fill="x", padx=14, pady=(0, 6))

        self._textbox = ctk.CTkTextbox(marco, font=_F_MONO, fg_color=_ENTRY_FONDO,
                                       text_color=_TEXTO, border_width=0,
                                       activate_scrollbars=True, wrap="word",
                                       state="disabled")
        self._textbox.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    # ── Zona inferior: campos defensa oral + gráfica ─────────────────────────

    def _construir_zona_defensa_y_grafica(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="x", padx=18, pady=(6, 16))

        # Fila de título + botón gráfica
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=14, pady=(10, 0))
        ctk.CTkLabel(fila, text="Visualización y Defensa Oral",
                     font=_F_BOLD, text_color=_TEXTO).pack(side="left")
        self._btn_graf = ctk.CTkButton(
            fila, text="Generar Gráfica", font=("Segoe UI", 11, "bold"),
            fg_color="#3A3F6B", hover_color="#4A509E",
            width=150, command=self._solicitar_grafica, state="disabled"
        )
        self._btn_graf.pack(side="right")

        # Contenedor horizontal: campos defensa (izq) | gráfica (der)
        contenedor = ctk.CTkFrame(marco, fg_color="transparent")
        contenedor.pack(fill="x", padx=14, pady=(8, 14))

        # Panel de campos de defensa oral (izquierda)
        self._panel_defensa = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                           corner_radius=8, width=260)
        self._panel_defensa.pack(side="left", fill="y", padx=(0, 8))
        self._panel_defensa.pack_propagate(False)

        ctk.CTkLabel(self._panel_defensa,
                     text="Completa durante la defensa oral:",
                     font=("Segoe UI", 10, "bold"), text_color=_ACENTO2
                     ).pack(anchor="w", padx=10, pady=(8, 4))

        self._frame_campos = ctk.CTkFrame(self._panel_defensa, fg_color="transparent")
        self._frame_campos.pack(fill="both", expand=True, padx=6)

        # Zona de la gráfica (derecha)
        self.zona_grafica = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                         corner_radius=8, height=220)
        self.zona_grafica.pack(side="left", fill="both", expand=True)
        self.zona_grafica.pack_propagate(False)

        self._ph_graf = ctk.CTkLabel(
            self.zona_grafica, text="La gráfica aparecerá aquí.",
            font=("Segoe UI", 11), text_color=_DIMMED
        )
        self._ph_graf.place(relx=0.5, rely=0.5, anchor="center")

    # ── API pública ──────────────────────────────────────────────────────────

    def cargar_coeficientes(self, A, C, D, E, F):
        self._A, self._C, self._D, self._E, self._F = A, C, D, E, F
        self._btn_graf.configure(state="disabled")
        self._analizar()

    # ── Lógica interna ───────────────────────────────────────────────────────

    def _analizar(self):
        A, C, D, E, F = self._A, self._C, self._D, self._E, self._F

        info = descripcion_completa(A, C, D, E, F)
        tipo = info.get("tipo", "—")
        icono = _ICONOS.get(tipo, "?")

        self._lbl_ec.configure(text=info.get("ecuacion", "—"))
        self._lbl_tipo.configure(text=f"{icono}  Cónica: {tipo.capitalize()}")

        self._datos = analizar_conica(A, C, D, E, F)

        if self._datos.get("error"):
            self._escribir_textbox(f"⚠ Error:\n\n{self._datos['error']}\n")
            return

        self._poblar_pasos(self._datos.get("pasos", []))
        self._poblar_campos_defensa(tipo)
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

    def _poblar_campos_defensa(self, tipo):
        # Limpiar campos anteriores
        for w in self._frame_campos.winfo_children():
            w.destroy()
        self._entradas_defensa.clear()

        campos = _CAMPOS_DEFENSA.get(tipo, [])
        if not campos:
            ctk.CTkLabel(self._frame_campos,
                         text="(sin campos para este tipo)",
                         font=_F_LBL, text_color=_DIMMED
                         ).pack(anchor="w", pady=2)
            return

        for etiqueta, _ in campos:
            ctk.CTkLabel(self._frame_campos, text=etiqueta,
                         font=_F_LBL, text_color=_DIMMED
                         ).pack(anchor="w", pady=(6, 0))
            entry = ctk.CTkEntry(
                self._frame_campos,
                placeholder_text="Tu respuesta...",
                width=220, font=_F_LBL,
                fg_color=_PANEL, border_color=_BORDE
            )
            entry.pack(anchor="w", pady=(0, 2))
            self._entradas_defensa[etiqueta] = entry

    def _escribir_textbox(self, texto):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("end", texto)
        self._textbox.configure(state="disabled")

    def _solicitar_grafica(self):
        if hasattr(self, "on_grafica_solicitada") and callable(self.on_grafica_solicitada):
            self.on_grafica_solicitada(datos=self._datos, contenedor=self.zona_grafica)