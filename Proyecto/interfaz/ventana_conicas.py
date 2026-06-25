# interfaz/ventana_conicas.py
# Nomenclatura PDF: A·x² + C·y² + D·x + E·y + F = 0
#
# Layout (de arriba hacia abajo):
#   1. BLOQUE SUPERIOR     — Ecuación General + tipo de cónica detectada
#   2. BLOQUE CENTRAL      — Dos columnas lado a lado:
#       • Columna Izquierda: campos de defensa oral
#       • Columna Derecha:   gráfica Matplotlib + barra de herramientas
#   3. BLOQUE INFERIOR     — Desarrollo matemático (ancho completo)
# =============================================================================

import sys, os
import customtkinter as ctk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Logica"))
from conicas      import analizar_conica
from Clasificador import descripcion_completa

# ── Paleta de colores ────────────────────────────────────────────────────────
_FONDO       = "#0F1117"
_PANEL       = "#1A1D2E"
_ACENTO      = "#5E81F4"
_ACENTO2     = "#F4A261"
_LAVANDA     = "#B39DDB"
_TEXTO       = "#E8EAF6"
_DIMMED      = "#7B83B0"
_ENTRY_FONDO = "#12152A"
_BORDE       = "#2E3254"
_NEUTRO_BG   = "#12152A"

# ── Tipografías ──────────────────────────────────────────────────────────────
_F_EQ   = ("Courier New", 14, "bold")
_F_TIPO = ("Georgia",     16, "bold")
_F_BOLD = ("Segoe UI",    11, "bold")
_F_MONO = ("Courier New", 11)
_F_LBL  = ("Segoe UI",    10)
_F_CAMP = ("Segoe UI",    11)

_ICONOS = {
    "circunferencia": "◎",
    "elipse":         "⬭",
    "parabola":       "∩",
    "hiperbola":      "⌓",
}

# =============================================================================
# DEFINICIÓN DE CAMPOS POR TIPO (Solo etiquetas de referencia)
# =============================================================================
_CAMPOS_DEFENSA = {
    "circunferencia": [
        ("Centro (h, k):", "centro"),
        ("Radio r:",        "radio"),
    ],
    "elipse": [
        ("Centro (h, k):", "centro"),
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
    "hiperbola": {
        "columna_1": [
            ("Centro (h, k):",  "centro"),
            ("Vértices:",       "vertices"),
            ("Focos F1 y F2:",  "focos"),
            ("Eje Real (2a):",  "a"),
        ],
        "columna_2": [
            ("Eje Imag. (2b):", "b"),
            ("Excentricidad e:","c"),
            ("Asíntota L1:",    "asintota_pendiente"),
            ("Asíntota L2:",    "asintota_pendiente"),
        ],
    },
}


# =============================================================================
# VENTANA PRINCIPAL
# =============================================================================

class VentanaConicas(ctk.CTkFrame):
    """
    Pestaña de análisis de cónicas con campos de apoyo para defensa oral.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_FONDO, **kwargs)
        self._A = self._C = self._D = self._E = self._F = 0
        self._datos  = {}
        self._tipo   = ""
        # Diccionario simple: etiqueta → CTkEntry
        self._campos = {}

        self._construir_bloque_superior()
        self._construir_bloque_central()
        self._construir_bloque_inferior()

    # =========================================================================
    # BLOQUE SUPERIOR — Ecuación + tipo
    # =========================================================================

    def _construir_bloque_superior(self):
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

    # =========================================================================
    # BLOQUE CENTRAL — Panel defensa (izq) | Gráfica (der)
    # =========================================================================

    def _construir_bloque_central(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="both", expand=True, padx=18, pady=(6, 6))

        # Fila de título + botón Generar Gráfica
        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(14, 0))

        ctk.CTkLabel(fila, text="Visualización y Defensa Oral",
                     font=("Segoe UI", 14, "bold"), text_color=_TEXTO
                     ).pack(side="left")

        self._btn_graf = ctk.CTkButton(
            fila, text="Generar Gráfica",
            font=("Segoe UI", 12, "bold"),
            fg_color=_ACENTO, hover_color="#4A6BD8",
            width=170, height=36,
            command=self._solicitar_grafica,
            state="disabled"
        )
        self._btn_graf.pack(side="right")

        # Contenedor horizontal
        contenedor = ctk.CTkFrame(marco, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # ── Panel de defensa (izquierda, ancho fijo) ──────────────────────────
        self._panel_defensa = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                           corner_radius=8, width=330)
        self._panel_defensa.pack(side="left", fill="y", padx=(0, 10))
        self._panel_defensa.pack_propagate(False)

        ctk.CTkLabel(self._panel_defensa,
                     text="Completa durante la defensa oral:",
                     font=("Segoe UI", 12, "bold"), text_color=_ACENTO2
                     ).pack(anchor="w", padx=12, pady=(12, 4))

        self._scroll_campos = ctk.CTkScrollableFrame(
            self._panel_defensa, fg_color="transparent",
            scrollbar_button_color=_BORDE,
            scrollbar_button_hover_color=_ACENTO
        )
        self._scroll_campos.pack(fill="both", expand=True, padx=6, pady=(0, 12))

        # Frame interior donde se crean los campos dinámicamente
        self._frame_campos = ctk.CTkFrame(self._scroll_campos, fg_color="transparent")
        self._frame_campos.pack(fill="both", expand=True)

        # ── Zona gráfica (derecha) ─────────────────────────────────────────────
        self.zona_grafica = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                         corner_radius=8)
        self.zona_grafica.pack(side="left", fill="both", expand=True)

        self._ph_graf = ctk.CTkLabel(
            self.zona_grafica,
            text="La gráfica aparecerá aquí.\nPresiona «Generar Gráfica» para visualizar.",
            font=("Segoe UI", 12), text_color=_DIMMED, justify="center"
        )
        self._ph_graf.place(relx=0.5, rely=0.5, anchor="center")

    # =========================================================================
    # BLOQUE INFERIOR — Desarrollo matemático
    # =========================================================================

    def _construir_bloque_inferior(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="x", padx=18, pady=(6, 16))

        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(fila,
                     text="Desarrollo Matemático — General → Canónica → General",
                     font=_F_BOLD, text_color=_ACENTO
                     ).pack(side="left")
        ctk.CTkLabel(fila, text="(detalle de referencia)",
                     font=("Segoe UI", 10), text_color=_DIMMED
                     ).pack(side="left", padx=(8, 0))

        ctk.CTkFrame(marco, height=1, fg_color=_BORDE).pack(fill="x", padx=14, pady=(0, 6))

        self._textbox = ctk.CTkTextbox(
            marco, font=_F_MONO, fg_color=_ENTRY_FONDO,
            text_color=_TEXTO, border_width=0,
            activate_scrollbars=True, wrap="word",
            state="disabled", height=170
        )
        self._textbox.pack(fill="x", padx=14, pady=(0, 14))

    # =========================================================================
    # API PÚBLICA
    # =========================================================================

    def cargar_coeficientes(self, A, C, D, E, F):
        self._A, self._C, self._D, self._E, self._F = A, C, D, E, F
        self._btn_graf.configure(state="disabled")
        self._analizar()

    # =========================================================================
    # LÓGICA INTERNA — Análisis
    # =========================================================================

    def _analizar(self):
        A, C, D, E, F = self._A, self._C, self._D, self._E, self._F

        info  = descripcion_completa(A, C, D, E, F)
        tipo  = info.get("tipo", "—")
        icono = _ICONOS.get(tipo, "?")

        self._lbl_ec.configure(text=info.get("ecuacion", "—"))
        self._lbl_tipo.configure(text=f"{icono}  Cónica: {tipo.capitalize()}")

        self._datos = analizar_conica(A, C, D, E, F)
        self._tipo  = tipo

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
        """Destruye campos anteriores y genera los nuevos según el tipo."""
        for w in self._frame_campos.winfo_children():
            w.destroy()
        self._campos.clear()

        if tipo == "hiperbola":
            self._poblar_campos_hiperbola()
        else:
            self._poblar_campos_generico(tipo)

    # ── Constructores de campos ───────────────────────────────────────────────

    def _crear_campo(self, parent, etiqueta, width=290, compact=False):
        """Crea un par label + entry de solo texto de manera simple."""
        pady_lbl = (4, 1) if compact else (8, 2)
        pady_ent = (0, 2) if compact else (0, 6)
        font_lbl = ("Segoe UI", 10) if compact else _F_CAMP

        ctk.CTkLabel(parent, text=etiqueta,
                     font=font_lbl, text_color=_DIMMED
                     ).pack(anchor="w", pady=pady_lbl)

        entry = ctk.CTkEntry(
            parent,
            placeholder_text="Tu respuesta...",
            width=width, height=30 if compact else 32,
            font=("Segoe UI", 10 if compact else 11),
            fg_color=_NEUTRO_BG, border_color=_BORDE
        )
        entry.pack(anchor="w", pady=pady_ent)

        self._campos[etiqueta] = entry
        return entry

    def _poblar_campos_generico(self, tipo):
        """Una sola columna para circunferencia, elipse y parábola."""
        campos = _CAMPOS_DEFENSA.get(tipo, [])
        if not campos:
            ctk.CTkLabel(self._frame_campos, text="(sin campos para este tipo)",
                         font=_F_LBL, text_color=_DIMMED
                         ).pack(anchor="w", pady=2)
            return
        for etiqueta, _ in campos:
            self._crear_campo(self._frame_campos, etiqueta)

    def _poblar_campos_hiperbola(self):
        """Dos columnas compactas para la hipérbola."""
        defn = _CAMPOS_DEFENSA["hiperbola"]

        fila = ctk.CTkFrame(self._frame_campos, fg_color="transparent")
        fila.pack(fill="both", expand=True)

        col1 = ctk.CTkFrame(fila, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=(0, 4))

        col2 = ctk.CTkFrame(fila, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=(4, 0))

        for etiqueta, _ in defn["columna_1"]:
            self._crear_campo(col1, etiqueta, width=130, compact=True)

        for etiqueta, _ in defn["columna_2"]:
            self._crear_campo(col2, etiqueta, width=130, compact=True)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _escribir_textbox(self, texto):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("end", texto)
        self._textbox.configure(state="disabled")

    def _solicitar_grafica(self):
        if hasattr(self, "on_grafica_solicitada") and callable(self.on_grafica_solicitada):
            self.on_grafica_solicitada(datos=self._datos, contenedor=self.zona_grafica)
