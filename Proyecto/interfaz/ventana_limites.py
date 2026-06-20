# =============================================================================
# interfaz/ventana_limites.py
# Añade campos de defensa oral vacíos integrados junto a la gráfica.
# =============================================================================

import sys, os
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
_F_LBL  = ("Segoe UI", 10)


class VentanaLimites(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_FONDO, **kwargs)
        self._datos   = {}
        self._digitos = []

        self._construir_encabezado()
        self._construir_zona_defensa_y_grafica()
        self._construir_cuerpo()

    # ── Encabezado ────────────────────────────────────────────────────────────

    def _construir_encabezado(self):
        panel = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        panel.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(panel, text="Función por Tramos generada desde el RUT",
                     font=("Segoe UI", 11), text_color=_DIMMED
                     ).pack(anchor="w", padx=18, pady=(12, 0))

        self._lbl_func = ctk.CTkLabel(panel, text="—", font=_F_FUNC,
                                      text_color=_ACENTO3, wraplength=860, justify="left")
        self._lbl_func.pack(anchor="w", padx=18, pady=(2, 4))

        ctk.CTkFrame(panel, height=1, fg_color=_BORDE).pack(fill="x", padx=18, pady=(0, 6))

        self._lbl_desc = ctk.CTkLabel(panel, text="—", font=("Segoe UI", 11),
                                      text_color=_ACENTO2, wraplength=860, justify="left")
        self._lbl_desc.pack(anchor="w", padx=18, pady=(0, 14))

    # ── Cuerpo: justificación + tabla ─────────────────────────────────────────

    def _construir_cuerpo(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="x", padx=18, pady=(6, 16))

        fila_titulo = ctk.CTkFrame(marco, fg_color="transparent")
        fila_titulo.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(fila_titulo, text="Análisis Matemático y Tabla de Valores",
                     font=_F_BOLD, text_color=_ACENTO
                     ).pack(side="left")
        ctk.CTkLabel(fila_titulo, text="(detalle de referencia)",
                     font=("Segoe UI", 10), text_color=_DIMMED
                     ).pack(side="left", padx=(8, 0))
        ctk.CTkFrame(marco, height=1, fg_color=_BORDE).pack(fill="x", padx=14, pady=(0, 6))

        self._textbox = ctk.CTkTextbox(marco, font=_F_MONO, fg_color=_ENTRY_FONDO,
                                       text_color=_TEXTO, border_width=0,
                                       activate_scrollbars=True, wrap="word",
                                       state="disabled", height=160)
        self._textbox.pack(fill="x", padx=14, pady=(0, 14))

    # ── Zona inferior: campos defensa oral + gráfica ─────────────────────────

    def _construir_zona_defensa_y_grafica(self):
        marco = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=12,
                             border_width=1, border_color=_BORDE)
        marco.pack(fill="both", expand=True, padx=18, pady=(6, 6))

        fila = ctk.CTkFrame(marco, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(fila, text="Gráfica y Defensa Oral",
                     font=("Segoe UI", 14, "bold"), text_color=_TEXTO).pack(side="left")
        self._btn_graf = ctk.CTkButton(
            fila, text="Generar Gráfica", font=("Segoe UI", 12, "bold"),
            fg_color=_ACENTO, hover_color="#4A6BD8",
            width=170, height=36, command=self._solicitar_grafica, state="disabled"
        )
        self._btn_graf.pack(side="right")

        contenedor = ctk.CTkFrame(marco, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # Panel de campos de defensa oral (izquierda)
        panel_def = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                 corner_radius=8, width=300)
        panel_def.pack(side="left", fill="y", padx=(0, 10))
        panel_def.pack_propagate(False)

        ctk.CTkLabel(panel_def,
                     text="Completa durante la defensa oral:",
                     font=("Segoe UI", 12, "bold"), text_color=_ACENTO2
                     ).pack(anchor="w", padx=12, pady=(12, 6))

        campos_defensa = [
            ("Límite por la izquierda  lím(x→a⁻):"),
            ("Límite por la derecha   lím(x→a⁺):"),
            ("¿Existe el límite? (Sí/No):"),
            ("Valor de f(a) si existe:"),
            ("¿Es continua en x=a? (Sí/No):"),
            ("Tipo de discontinuidad:"),
            ("Justificación breve:"),
        ]

        self._entradas_defensa = {}
        panel_scroll = ctk.CTkScrollableFrame(panel_def, fg_color="transparent")
        panel_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 8))
        for etiqueta in campos_defensa:
            ctk.CTkLabel(panel_scroll, text=etiqueta,
                         font=("Segoe UI", 11), text_color=_DIMMED
                         ).pack(anchor="w", padx=6, pady=(8, 2))
            entry = ctk.CTkEntry(
                panel_scroll,
                placeholder_text="Tu respuesta...",
                width=260, height=32, font=("Segoe UI", 11),
                fg_color=_PANEL, border_color=_BORDE
            )
            entry.pack(anchor="w", padx=6, pady=(0, 4))
            self._entradas_defensa[etiqueta] = entry

        # Zona de la gráfica (derecha) — protagonista del panel
        self.zona_grafica = ctk.CTkFrame(contenedor, fg_color=_ENTRY_FONDO,
                                         corner_radius=8)
        self.zona_grafica.pack(side="left", fill="both", expand=True)

        self._ph_graf = ctk.CTkLabel(
            self.zona_grafica, text="La gráfica aparecerá aquí.",
            font=("Segoe UI", 12), text_color=_DIMMED
        )
        self._ph_graf.place(relx=0.5, rely=0.5, anchor="center")

    # ── API pública ──────────────────────────────────────────────────────────

    def cargar_digitos(self, digitos):
        self._digitos = digitos
        self._btn_graf.configure(state="disabled")
        self._generar()

    # ── Lógica interna ───────────────────────────────────────────────────────

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

        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", "  JUSTIFICACIÓN MATEMÁTICA\n")
        self._textbox.insert("end", "═" * 54 + "\n\n")
        self._textbox.insert("end", d["justificacion"] + "\n\n")

        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", "  TABLA DE VALORES  (evidencia numérica)\n")
        self._textbox.insert("end", "═" * 54 + "\n")
        self._textbox.insert("end", f"{'x':>12}  {'lado':>4}  {'f(x)':>18}\n")
        self._textbox.insert("end", "─" * 40 + "\n")

        a = d["a"]
        for idx, fila in enumerate(d["tabla"]):
            marca = "← " if fila["lado"] == "←" else "→ "
            self._textbox.insert(
                "end", f"{str(fila['x']):>12}  {marca:>4}  {fila['fx_str']:>18}\n"
            )
            if idx == 3:
                self._textbox.insert("end", f"{'· · · · x = ' + str(a) + ' · · · ·':^40}\n")

        self._textbox.configure(state="disabled")

    def _solicitar_grafica(self):
        if hasattr(self, "on_grafica_solicitada") and callable(self.on_grafica_solicitada):
            self.on_grafica_solicitada(datos=self._datos, contenedor=self.zona_grafica)