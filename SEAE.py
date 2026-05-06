"""
SEAE - Sistema de Evaluación de Alternativas Económicas
Universidad de El Salvador - Ingeniería de Negocios
Ciclo VII/2026
Métodos: VPN, CAE, TIR
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import datetime
import os

# ─────────────────────────────────────────────
#  PALETA Y ESTILOS
# ─────────────────────────────────────────────
BG_DARK   = "#0D1117"
BG_PANEL  = "#161B22"
BG_CARD   = "#1C2128"
ACCENT    = "#58A6FF"
ACCENT2   = "#3FB950"
ACCENT3   = "#F78166"
ACCENT4   = "#D2A8FF"
TEXT_PRI  = "#E6EDF3"
TEXT_SEC  = "#8B949E"
BORDER    = "#30363D"
GOLD      = "#E3B341"

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_RESULT = ("Consolas", 11)
FONT_BIG    = ("Segoe UI", 28, "bold")


# ─────────────────────────────────────────────
#  MOTOR DE CÁLCULO
# ─────────────────────────────────────────────
def calcular_vpn(inversion, flujos, tasa):
    """VPN = -Inversión + Σ Ft/(1+i)^t"""
    vpn = -inversion
    for t, ft in enumerate(flujos, start=1):
        vpn += ft / (1 + tasa) ** t
    return vpn

def calcular_cae(vpn, tasa, n):
    """CAE = VPN * [i(1+i)^n / ((1+i)^n - 1)]"""
    if tasa == 0:
        return vpn / n
    factor = (tasa * (1 + tasa) ** n) / ((1 + tasa) ** n - 1)
    return vpn * factor

def calcular_tir(inversion, flujos, precision=1e-7, max_iter=1000):
    """Bisección para encontrar la TIR"""
    def npv(rate):
        total = -inversion
        for t, ft in enumerate(flujos, start=1):
            total += ft / (1 + rate) ** t
        return total

    lo, hi = -0.9999, 10.0
    if npv(lo) * npv(hi) > 0:
        return None  # No hay TIR real

    for _ in range(max_iter):
        mid = (lo + hi) / 2
        val = npv(mid)
        if abs(val) < precision:
            return mid
        if npv(lo) * val < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ─────────────────────────────────────────────
#  WIDGET HELPERS
# ─────────────────────────────────────────────
def make_label(parent, text, font=FONT_LABEL, fg=TEXT_PRI, bg=None, **kw):
    bg = bg or BG_PANEL
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

def make_entry(parent, textvariable=None, width=18):
    e = tk.Entry(parent, textvariable=textvariable, width=width,
                 bg=BG_CARD, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", font=FONT_LABEL,
                 highlightbackground=BORDER, highlightcolor=ACCENT,
                 highlightthickness=1)
    return e

def make_btn(parent, text, command, color=ACCENT, fg=BG_DARK, width=18):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, font=("Segoe UI", 10, "bold"),
                    relief="flat", cursor="hand2", width=width,
                    activebackground=color, activeforeground=fg,
                    padx=8, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def _lighten(hex_color):
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02X}{g:02X}{b:02X}"

def separator(parent, bg=BORDER, height=1):
    tk.Frame(parent, bg=bg, height=height).pack(fill="x", pady=6)

def card_frame(parent, **kw):
    f = tk.Frame(parent, bg=BG_CARD, relief="flat",
                 highlightbackground=BORDER, highlightthickness=1, **kw)
    return f


# ─────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEAE – Sistema de Evaluación de Alternativas Económicas")
        self.geometry("1100x720")
        self.minsize(900, 640)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Estado global
        self.resultado_alt1 = {}
        self.resultado_alt2 = {}

        self._build_ui()

    # ── UI Principal ──
    def _build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=BG_PANEL, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Área de contenido
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        # Páginas
        self.pages = {}
        for PageClass in (PageVPN, PageCAE, PageTIR, PageComparar, PageReporte):
            page = PageClass(self.content, self)
            self.pages[PageClass.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_page("PageVPN")

    def _build_sidebar(self, sb):
        # Logo / título
        tk.Frame(sb, bg=ACCENT, height=4).pack(fill="x")
        tk.Label(sb, text="⟨SEAE⟩", font=("Segoe UI", 18, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(pady=(18, 0))
        tk.Label(sb, text="Alternativas Económicas",
                 font=FONT_SMALL, fg=TEXT_SEC, bg=BG_PANEL).pack(pady=(0, 18))
        separator(sb)

        nav = [
            ("📊  Valor Presente (VPN)", "PageVPN"),
            ("📅  Costo Anual (CAE)",    "PageCAE"),
            ("📈  Tasa de Retorno (TIR)", "PageTIR"),
            ("⚖️   Comparar Alternativas","PageComparar"),
            ("📄  Generar Reporte",       "PageReporte"),
        ]
        self.nav_btns = {}
        for label, page_name in nav:
            btn = tk.Button(sb, text=label, font=("Segoe UI", 10),
                            fg=TEXT_PRI, bg=BG_PANEL, relief="flat",
                            anchor="w", padx=18, pady=10, cursor="hand2",
                            activebackground=BG_CARD, activeforeground=ACCENT,
                            command=lambda p=page_name: self.show_page(p))
            btn.pack(fill="x")
            self.nav_btns[page_name] = btn

        separator(sb)
        tk.Label(sb, text="UES – Ciclo VII/2026\nIngeniería de Negocios",
                 font=FONT_SMALL, fg=TEXT_SEC, bg=BG_PANEL,
                 justify="center").pack(side="bottom", pady=16)

    def show_page(self, name):
        self.pages[name].lift()
        for pg, btn in self.nav_btns.items():
            if pg == name:
                btn.config(bg=BG_CARD, fg=ACCENT)
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_PRI)


# ─────────────────────────────────────────────
#  BASE DE PÁGINA
# ─────────────────────────────────────────────
class BasePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_DARK)
        self.app = app

    def page_header(self, title, subtitle, color=ACCENT):
        hdr = tk.Frame(self, bg=BG_PANEL)
        hdr.pack(fill="x", padx=0, pady=0)
        tk.Frame(hdr, bg=color, height=3).pack(fill="x")
        inner = tk.Frame(hdr, bg=BG_PANEL)
        inner.pack(fill="x", padx=28, pady=14)
        tk.Label(inner, text=title, font=FONT_TITLE,
                 fg=color, bg=BG_PANEL).pack(anchor="w")
        tk.Label(inner, text=subtitle, font=FONT_SMALL,
                 fg=TEXT_SEC, bg=BG_PANEL).pack(anchor="w")

    def result_box(self, parent, text, color=ACCENT2):
        box = card_frame(parent)
        box.pack(fill="x", padx=0, pady=6)
        tk.Frame(box, bg=color, width=4).pack(side="left", fill="y")
        tk.Label(box, text=text, font=FONT_RESULT,
                 fg=TEXT_PRI, bg=BG_CARD,
                 justify="left", wraplength=620, padx=12, pady=10).pack(side="left", fill="x", expand=True)
        return box

    def parse_flujos(self, raw: str):
        """Parsea '1000, 2000, 3000' → [1000.0, 2000.0, 3000.0]"""
        parts = raw.replace(";", ",").split(",")
        return [float(p.strip()) for p in parts if p.strip()]


# ─────────────────────────────────────────────
#  PÁGINA VPN
# ─────────────────────────────────────────────
class PageVPN(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Valor Presente Neto (VPN)",
                         "Evalúa si un proyecto genera valor por encima del costo de capital.", ACCENT)
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        # ── Columna izquierda: inputs ──
        left = card_frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="Parámetros de entrada", font=FONT_HEAD,
                 fg=ACCENT, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")

        fields = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        fields.pack(fill="x")

        self.v_inv   = tk.StringVar(value="50000")
        self.v_tasa  = tk.StringVar(value="10")
        self.v_n     = tk.StringVar(value="5")
        self.v_flujos = tk.StringVar(value="15000, 18000, 20000, 22000, 25000")
        self.v_vsal  = tk.StringVar(value="0")

        rows = [
            ("Inversión inicial ($):",   self.v_inv),
            ("Tasa de descuento (%):",   self.v_tasa),
            ("Vida del proyecto (años):", self.v_n),
            ("Valor de salvamento ($):", self.v_vsal),
        ]
        for i, (lbl, var) in enumerate(rows):
            make_label(fields, lbl, bg=BG_CARD, fg=TEXT_SEC).grid(row=i, column=0, sticky="w", pady=4)
            make_entry(fields, var).grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=4)

        make_label(fields, "Flujos de caja (separados por coma):", bg=BG_CARD, fg=TEXT_SEC).grid(
            row=len(rows), column=0, columnspan=2, sticky="w", pady=(8, 2))
        tk.Entry(fields, textvariable=self.v_flujos, width=40,
                 bg=BG_DARK, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", font=FONT_LABEL,
                 highlightbackground=BORDER, highlightcolor=ACCENT,
                 highlightthickness=1).grid(row=len(rows)+1, column=0, columnspan=2, sticky="ew")

        fields.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        btn_frame.pack(fill="x")
        make_btn(btn_frame, "▶  Calcular VPN", self.calcular, ACCENT).pack(side="left")
        make_btn(btn_frame, "💾  Guardar como Alt. 1", lambda: self.guardar(1), GOLD, BG_DARK, 20).pack(side="left", padx=(8, 0))
        make_btn(btn_frame, "💾  Guardar como Alt. 2", lambda: self.guardar(2), ACCENT4, BG_DARK, 20).pack(side="left", padx=(8, 0))

        # ── Columna derecha: resultados ──
        right = card_frame(body)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Resultados", font=FONT_HEAD,
                 fg=ACCENT2, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")

        self.res_frame = tk.Frame(right, bg=BG_CARD, padx=16, pady=12)
        self.res_frame.pack(fill="both", expand=True)
        make_label(self.res_frame, "Complete los datos y presione Calcular. " \
        "Solo usar numeros enteros sin nungun simbolo.",
                   fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

    def calcular(self):
        try:
            inv   = float(self.v_inv.get())
            tasa  = float(self.v_tasa.get()) / 100
            n     = int(self.v_n.get())
            vsal  = float(self.v_vsal.get())
            flujos = self.parse_flujos(self.v_flujos.get())

            if len(flujos) != n:
                messagebox.showwarning("Atención", f"Se esperaban {n} flujos de caja, pero se ingresaron {len(flujos)}.")
                return

            flujos[-1] += vsal  # sumar valor de salvamento al último flujo

            vpn = calcular_vpn(inv, flujos, tasa)
            decision = "✅ ACEPTAR – el proyecto genera valor." if vpn > 0 else "❌ RECHAZAR – el proyecto destruye valor."

            for w in self.res_frame.winfo_children():
                w.destroy()

            tk.Label(self.res_frame, text=f"${vpn:,.2f}",
                     font=FONT_BIG, fg=ACCENT2 if vpn > 0 else ACCENT3,
                     bg=BG_CARD).pack(anchor="w", pady=(8, 0))
            tk.Label(self.res_frame, text="Valor Presente Neto",
                     font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

            self.result_box(self.res_frame, decision,
                            color=ACCENT2 if vpn > 0 else ACCENT3)

            detalle = (
                f"  Inversión inicial : ${inv:>14,.2f}\n"
                f"  Tasa de descuento : {tasa*100:.2f}%\n"
                f"  Vida del proyecto : {n} años\n"
                f"  Val. de salvamento: ${vsal:>14,.2f}\n"
                f"  Flujos de caja    : {', '.join(f'${f:,.0f}' for f in flujos)}\n"
                f"  ─────────────────────────────\n"
                f"  VPN               : ${vpn:>14,.2f}"
            )
            self.result_box(self.res_frame, detalle, color=ACCENT)

            self._vpn = vpn
            self._datos = {"inversion": inv, "tasa": tasa, "n": n,
                           "vsal": vsal, "flujos": flujos, "vpn": vpn}

        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Verifica los datos.\nDetalle: {e}")

    def guardar(self, alt):
        if not hasattr(self, '_datos'):
            messagebox.showwarning("Sin datos", "Primero realiza un cálculo.")
            return
        if alt == 1:
            self.app.resultado_alt1 = {"metodo": "VPN", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 1 guardada con VPN.")
        else:
            self.app.resultado_alt2 = {"metodo": "VPN", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 2 guardada con VPN.")


# ─────────────────────────────────────────────
#  PÁGINA CAE
# ─────────────────────────────────────────────
class PageCAE(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Costo Anual Equivalente (CAE)",
                         "Convierte el VPN en un flujo uniforme anual para comparar proyectos de distinta vida.", GOLD)
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        left = card_frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="Parámetros de entrada", font=FONT_HEAD,
                 fg=GOLD, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")

        fields = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        fields.pack(fill="x")

        self.v_inv   = tk.StringVar(value="80000")
        self.v_tasa  = tk.StringVar(value="12")
        self.v_n     = tk.StringVar(value="6")
        self.v_flujos = tk.StringVar(value="20000, 22000, 24000, 26000, 28000, 30000")
        self.v_vsal  = tk.StringVar(value="5000")

        rows = [
            ("Inversión inicial ($):",    self.v_inv),
            ("Tasa de descuento (%):",    self.v_tasa),
            ("Vida del proyecto (años):", self.v_n),
            ("Valor de salvamento ($):",  self.v_vsal),
        ]
        for i, (lbl, var) in enumerate(rows):
            make_label(fields, lbl, bg=BG_CARD, fg=TEXT_SEC).grid(row=i, column=0, sticky="w", pady=4)
            make_entry(fields, var).grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=4)

        make_label(fields, "Flujos de caja (separados por coma):", bg=BG_CARD, fg=TEXT_SEC).grid(
            row=len(rows), column=0, columnspan=2, sticky="w", pady=(8, 2))
        tk.Entry(fields, textvariable=self.v_flujos, width=40,
                 bg=BG_DARK, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", font=FONT_LABEL,
                 highlightbackground=BORDER, highlightcolor=GOLD,
                 highlightthickness=1).grid(row=len(rows)+1, column=0, columnspan=2, sticky="ew")
        fields.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        btn_frame.pack(fill="x")
        make_btn(btn_frame, "▶  Calcular CAE", self.calcular, GOLD, BG_DARK).pack(side="left")
        make_btn(btn_frame, "💾  Guardar Alt. 1", lambda: self.guardar(1), ACCENT, fg=BG_DARK, width=16).pack(side="left", padx=(8, 0))
        make_btn(btn_frame, "💾  Guardar Alt. 2", lambda: self.guardar(2), ACCENT4, fg=BG_DARK, width=16).pack(side="left", padx=(8, 0))

        right = card_frame(body)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Resultados", font=FONT_HEAD,
                 fg=GOLD, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")

        self.res_frame = tk.Frame(right, bg=BG_CARD, padx=16, pady=12)
        self.res_frame.pack(fill="both", expand=True)
        make_label(self.res_frame, "Complete los datos y presione Calcular. " \
        "Solo usar numeros enteros sin nungun simbolo.",
                   fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

    def calcular(self):
        try:
            inv   = float(self.v_inv.get())
            tasa  = float(self.v_tasa.get()) / 100
            n     = int(self.v_n.get())
            vsal  = float(self.v_vsal.get())
            flujos = self.parse_flujos(self.v_flujos.get())

            if len(flujos) != n:
                messagebox.showwarning("Atención", f"Se esperaban {n} flujos, se ingresaron {len(flujos)}.")
                return

            flujos[-1] += vsal
            vpn = calcular_vpn(inv, flujos, tasa)
            cae = calcular_cae(vpn, tasa, n)

            decision = "✅ ACEPTAR – el CAE es positivo." if cae > 0 else "❌ RECHAZAR – el CAE es negativo."

            for w in self.res_frame.winfo_children():
                w.destroy()

            tk.Label(self.res_frame, text=f"${cae:,.2f}/año",
                     font=FONT_BIG, fg=ACCENT2 if cae > 0 else ACCENT3,
                     bg=BG_CARD).pack(anchor="w", pady=(8, 0))
            tk.Label(self.res_frame, text="Costo Anual Equivalente",
                     font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

            self.result_box(self.res_frame, decision,
                            color=ACCENT2 if cae > 0 else ACCENT3)

            detalle = (
                f"  Inversión inicial : ${inv:>14,.2f}\n"
                f"  Tasa de descuento : {tasa*100:.2f}%\n"
                f"  Vida del proyecto : {n} años\n"
                f"  Val. de salvamento: ${vsal:>14,.2f}\n"
                f"  VPN calculado     : ${vpn:>14,.2f}\n"
                f"  ─────────────────────────────\n"
                f"  CAE               : ${cae:>14,.2f}/año"
            )
            self.result_box(self.res_frame, detalle, color=GOLD)

            self._datos = {"inversion": inv, "tasa": tasa, "n": n,
                           "vsal": vsal, "flujos": flujos, "vpn": vpn, "cae": cae}

        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Verifica los datos.\nDetalle: {e}")

    def guardar(self, alt):
        if not hasattr(self, '_datos'):
            messagebox.showwarning("Sin datos", "Primero realiza un cálculo.")
            return
        if alt == 1:
            self.app.resultado_alt1 = {"metodo": "CAE", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 1 guardada con CAE.")
        else:
            self.app.resultado_alt2 = {"metodo": "CAE", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 2 guardada con CAE.")


# ─────────────────────────────────────────────
#  PÁGINA TIR
# ─────────────────────────────────────────────
class PageTIR(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Tasa Interna de Retorno (TIR)",
                         "Tasa que hace el VPN igual a cero. Se acepta si TIR ≥ tasa mínima requerida.", ACCENT4)
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        left = card_frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="Parámetros de entrada", font=FONT_HEAD,
                 fg=ACCENT4, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")

        fields = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        fields.pack(fill="x")

        self.v_inv   = tk.StringVar(value="100000")
        self.v_tmin  = tk.StringVar(value="10")
        self.v_n     = tk.StringVar(value="5")
        self.v_flujos = tk.StringVar(value="30000, 35000, 40000, 45000, 50000")
        self.v_vsal  = tk.StringVar(value="10000")

        rows = [
            ("Inversión inicial ($):",       self.v_inv),
            ("Tasa mínima requerida (%):",   self.v_tmin),
            ("Vida del proyecto (años):",    self.v_n),
            ("Valor de salvamento ($):",     self.v_vsal),
        ]
        for i, (lbl, var) in enumerate(rows):
            make_label(fields, lbl, bg=BG_CARD, fg=TEXT_SEC).grid(row=i, column=0, sticky="w", pady=4)
            make_entry(fields, var).grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=4)

        make_label(fields, "Flujos de caja (separados por coma):", bg=BG_CARD, fg=TEXT_SEC).grid(
            row=len(rows), column=0, columnspan=2, sticky="w", pady=(8, 2))
        tk.Entry(fields, textvariable=self.v_flujos, width=40,
                 bg=BG_DARK, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", font=FONT_LABEL,
                 highlightbackground=BORDER, highlightcolor=ACCENT4,
                 highlightthickness=1).grid(row=len(rows)+1, column=0, columnspan=2, sticky="ew")
        fields.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(left, bg=BG_CARD, padx=16, pady=12)
        btn_frame.pack(fill="x")
        make_btn(btn_frame, "▶  Calcular TIR", self.calcular, ACCENT4, BG_DARK).pack(side="left")
        make_btn(btn_frame, "💾  Guardar Alt. 1", lambda: self.guardar(1), ACCENT, fg=BG_DARK, width=16).pack(side="left", padx=(8, 0))
        make_btn(btn_frame, "💾  Guardar Alt. 2", lambda: self.guardar(2), GOLD, fg=BG_DARK, width=16).pack(side="left", padx=(8, 0))

        right = card_frame(body)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Resultados", font=FONT_HEAD,
                 fg=ACCENT4, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")

        self.res_frame = tk.Frame(right, bg=BG_CARD, padx=16, pady=12)
        self.res_frame.pack(fill="both", expand=True)
        make_label(self.res_frame, "Complete los datos y presione Calcular." \
        "Solo usar numeros enteros sin nungun simbolo.",
                   fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

    def calcular(self):
        try:
            inv   = float(self.v_inv.get())
            tmin  = float(self.v_tmin.get()) / 100
            n     = int(self.v_n.get())
            vsal  = float(self.v_vsal.get())
            flujos = self.parse_flujos(self.v_flujos.get())

            if len(flujos) != n:
                messagebox.showwarning("Atención", f"Se esperaban {n} flujos, se ingresaron {len(flujos)}.")
                return

            flujos[-1] += vsal
            tir = calcular_tir(inv, flujos)

            for w in self.res_frame.winfo_children():
                w.destroy()

            if tir is None:
                tk.Label(self.res_frame, text="No existe TIR real",
                         font=FONT_BIG, fg=ACCENT3, bg=BG_CARD).pack(anchor="w", pady=8)
                return

            acepta = tir >= tmin
            decision = f"✅ ACEPTAR – TIR ({tir*100:.2f}%) ≥ TMAR ({tmin*100:.2f}%)" if acepta else \
                       f"❌ RECHAZAR – TIR ({tir*100:.2f}%) < TMAR ({tmin*100:.2f}%)"

            tk.Label(self.res_frame, text=f"{tir*100:.4f}%",
                     font=FONT_BIG, fg=ACCENT2 if acepta else ACCENT3,
                     bg=BG_CARD).pack(anchor="w", pady=(8, 0))
            tk.Label(self.res_frame, text="Tasa Interna de Retorno",
                     font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")

            self.result_box(self.res_frame, decision,
                            color=ACCENT2 if acepta else ACCENT3)

            detalle = (
                f"  Inversión inicial  : ${inv:>14,.2f}\n"
                f"  TMAR               : {tmin*100:.2f}%\n"
                f"  Vida del proyecto  : {n} años\n"
                f"  Val. de salvamento : ${vsal:>14,.2f}\n"
                f"  Flujos de caja     : {', '.join(f'${f:,.0f}' for f in flujos)}\n"
                f"  ──────────────────────────────\n"
                f"  TIR                : {tir*100:.4f}%"
            )
            self.result_box(self.res_frame, detalle, color=ACCENT4)

            self._datos = {"inversion": inv, "tasa": tmin, "n": n,
                           "vsal": vsal, "flujos": flujos, "tir": tir, "tmin": tmin}

        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Verifica los datos.\nDetalle: {e}")

    def guardar(self, alt):
        if not hasattr(self, '_datos'):
            messagebox.showwarning("Sin datos", "Primero realiza un cálculo.")
            return
        if alt == 1:
            self.app.resultado_alt1 = {"metodo": "TIR", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 1 guardada con TIR.")
        else:
            self.app.resultado_alt2 = {"metodo": "TIR", **self._datos}
            messagebox.showinfo("Guardado", "Alternativa 2 guardada con TIR.")


# ─────────────────────────────────────────────
#  PÁGINA COMPARAR
# ─────────────────────────────────────────────
class PageComparar(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Comparación de Alternativas",
                         "Compara dos alternativas económicas para elegir la más conveniente.", ACCENT3)
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        make_btn(body, "🔄  Comparar ahora", self.comparar, ACCENT3, BG_DARK, 20).pack(anchor="w", pady=(0, 12))

        self.res_frame = tk.Frame(body, bg=BG_DARK)
        self.res_frame.pack(fill="both", expand=True)

        make_label(self.res_frame,
                   "Primero calcula y guarda dos alternativas desde las secciones VPN, CAE o TIR.\n"
                   "Luego regresa aquí y presiona Comparar.",
                   fg=TEXT_SEC, bg=BG_DARK, justify="left").pack(anchor="w")

    def comparar(self):
        a1 = self.app.resultado_alt1
        a2 = self.app.resultado_alt2

        for w in self.res_frame.winfo_children():
            w.destroy()

        if not a1 or not a2:
            make_label(self.res_frame,
                       "⚠️  Necesitas guardar dos alternativas primero.",
                       fg=ACCENT3, bg=BG_DARK).pack(anchor="w")
            return

        # Mostrar tabla
        cols_frame = tk.Frame(self.res_frame, bg=BG_DARK)
        cols_frame.pack(fill="x")

        for idx, (alt, color) in enumerate([(a1, ACCENT), (a2, ACCENT4)]):
            card = card_frame(cols_frame)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx==0 else 8, 0))

            tk.Label(card, text=f"Alternativa {idx+1}", font=FONT_HEAD,
                     fg=color, bg=BG_CARD, padx=14, pady=8).pack(anchor="w")
            tk.Frame(card, bg=BORDER, height=1).pack(fill="x")

            info = tk.Frame(card, bg=BG_CARD, padx=14, pady=10)
            info.pack(fill="x")

            make_label(info, f"Método: {alt['metodo']}", bg=BG_CARD, fg=TEXT_SEC).pack(anchor="w")
            make_label(info, f"Inversión: ${alt['inversion']:,.2f}", bg=BG_CARD, fg=TEXT_PRI).pack(anchor="w")
            make_label(info, f"Tasa: {alt['tasa']*100:.2f}%", bg=BG_CARD, fg=TEXT_PRI).pack(anchor="w")
            make_label(info, f"Vida: {alt['n']} años", bg=BG_CARD, fg=TEXT_PRI).pack(anchor="w")

            if alt['metodo'] == "VPN":
                val = alt.get('vpn', 0)
                make_label(info, f"VPN: ${val:,.2f}", bg=BG_CARD,
                           fg=ACCENT2 if val > 0 else ACCENT3,
                           font=FONT_HEAD).pack(anchor="w", pady=(6, 0))
            elif alt['metodo'] == "CAE":
                val = alt.get('cae', 0)
                make_label(info, f"CAE: ${val:,.2f}/año", bg=BG_CARD,
                           fg=ACCENT2 if val > 0 else ACCENT3,
                           font=FONT_HEAD).pack(anchor="w", pady=(6, 0))
            elif alt['metodo'] == "TIR":
                tir = alt.get('tir', 0)
                tmin = alt.get('tmin', 0)
                acepta = tir >= tmin
                make_label(info, f"TIR: {tir*100:.4f}%", bg=BG_CARD,
                           fg=ACCENT2 if acepta else ACCENT3,
                           font=FONT_HEAD).pack(anchor="w", pady=(6, 0))

        cols_frame.columnconfigure(0, weight=1)
        cols_frame.columnconfigure(1, weight=1)

        # Veredicto
        ganador, texto, color = self._veredicto(a1, a2)
        tk.Frame(self.res_frame, bg=BORDER, height=1).pack(fill="x", pady=12)
        box = card_frame(self.res_frame)
        box.pack(fill="x")
        tk.Frame(box, bg=color, width=6).pack(side="left", fill="y")
        tk.Label(box, text=f"  {texto}",
                 font=("Segoe UI", 13, "bold"), fg=color, bg=BG_CARD,
                 padx=12, pady=14).pack(side="left")

    def _veredicto(self, a1, a2):
        def valor(a):
            m = a['metodo']
            if m == "VPN": return a.get('vpn', None), "vpn"
            if m == "CAE": return a.get('cae', None), "cae"
            if m == "TIR": return a.get('tir', None), "tir"

        v1, tipo1 = valor(a1)
        v2, tipo2 = valor(a2)

        if tipo1 != tipo2:
            return None, "⚠️  Las alternativas usan métodos distintos. Compáralas manualmente.", GOLD

        if tipo1 in ("vpn", "cae"):
            if v1 > v2:
                return 1, f"🏆  Alternativa 1 es SUPERIOR  (${v1:,.2f} vs ${v2:,.2f})", ACCENT2
            elif v2 > v1:
                return 2, f"🏆  Alternativa 2 es SUPERIOR  (${v2:,.2f} vs ${v1:,.2f})", ACCENT4
            else:
                return 0, "⚖️  Ambas alternativas son equivalentes.", GOLD
        else:  # TIR
            tmin = a1.get('tmin', 0)
            a1ok = v1 >= tmin
            a2ok = v2 >= a2.get('tmin', 0)
            if a1ok and not a2ok:
                return 1, f"🏆  Solo Alternativa 1 supera la TMAR (TIR={v1*100:.2f}%)", ACCENT2
            elif a2ok and not a1ok:
                return 2, f"🏆  Solo Alternativa 2 supera la TMAR (TIR={v2*100:.2f}%)", ACCENT4
            elif a1ok and a2ok:
                if v1 >= v2:
                    return 1, f"🏆  Ambas aceptables. Alt. 1 con mayor TIR ({v1*100:.2f}%)", ACCENT2
                else:
                    return 2, f"🏆  Ambas aceptables. Alt. 2 con mayor TIR ({v2*100:.2f}%)", ACCENT4
            else:
                return 0, "❌  Ninguna alternativa supera la TMAR.", ACCENT3


# ─────────────────────────────────────────────
#  PÁGINA REPORTE
# ─────────────────────────────────────────────
class PageReporte(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Generación de Reporte",
                         "Exporta los resultados calculados a un archivo TXT o CSV.", ACCENT2)
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        # Formulario portada
        top = card_frame(body)
        top.pack(fill="x", pady=(0, 12))
        tk.Label(top, text="Datos de portada", font=FONT_HEAD,
                 fg=ACCENT2, bg=BG_CARD, padx=16, pady=10).pack(anchor="w")
        tk.Frame(top, bg=BORDER, height=1).pack(fill="x")

        flds = tk.Frame(top, bg=BG_CARD, padx=16, pady=12)
        flds.pack(fill="x")

        self.v_uni    = tk.StringVar(value="Universidad de El Salvador")
        self.v_mat    = tk.StringVar(value="Ingeniería de Negocios")
        self.v_ciclo  = tk.StringVar(value="Ciclo VII/2026")
        self.v_equipo = tk.StringVar(value="Nombre del equipo")
        self.v_integ  = tk.StringVar(value="Integrante 1, Integrante 2, Integrante 3")

        pares = [
            ("Universidad:", self.v_uni),
            ("Materia:",     self.v_mat),
            ("Ciclo:",       self.v_ciclo),
            ("Equipo:",      self.v_equipo),
            ("Integrantes:", self.v_integ),
        ]
        for i, (lbl, var) in enumerate(pares):
            make_label(flds, lbl, bg=BG_CARD, fg=TEXT_SEC).grid(row=i, column=0, sticky="w", pady=3)
            tk.Entry(flds, textvariable=var, width=55,
                     bg=BG_DARK, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                     relief="flat", font=FONT_LABEL,
                     highlightbackground=BORDER, highlightcolor=ACCENT2,
                     highlightthickness=1).grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=3)
        flds.columnconfigure(1, weight=1)

        # Botones
        btn_row = tk.Frame(body, bg=BG_DARK)
        btn_row.pack(fill="x", pady=(0, 12))
        make_btn(btn_row, "📄  Exportar TXT",  self.exportar_txt,  ACCENT2).pack(side="left")
        make_btn(btn_row, "📊  Exportar CSV",  self.exportar_csv,  ACCENT,  width=18).pack(side="left", padx=(8, 0))
        make_btn(btn_row, "👁  Vista previa",  self.preview,       GOLD, BG_DARK).pack(side="left", padx=(8, 0))

        # Preview
        prev_card = card_frame(body)
        prev_card.pack(fill="both", expand=True)
        tk.Label(prev_card, text="Vista previa del reporte", font=FONT_HEAD,
                 fg=TEXT_SEC, bg=BG_CARD, padx=16, pady=8).pack(anchor="w")
        tk.Frame(prev_card, bg=BORDER, height=1).pack(fill="x")

        self.preview_text = tk.Text(prev_card, bg=BG_DARK, fg=TEXT_PRI,
                                    font=("Consolas", 9), relief="flat",
                                    wrap="word", padx=12, pady=10)
        scroll = ttk.Scrollbar(prev_card, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.preview_text.pack(fill="both", expand=True)

    def _generar_texto(self):
        lineas = []
        sep = "=" * 60
        sep2 = "-" * 60

        lineas.append(sep)
        lineas.append(f"  {self.v_uni.get()}")
        lineas.append(f"  {self.v_mat.get()}  |  {self.v_ciclo.get()}")
        lineas.append(f"  Equipo: {self.v_equipo.get()}")
        lineas.append(f"  Integrantes: {self.v_integ.get()}")
        lineas.append(f"  Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lineas.append(sep)
        lineas.append("  REPORTE – Sistema de Evaluación de Alternativas Económicas")
        lineas.append(sep)

        def bloque(titulo, d, color_label=""):
            if not d:
                return [f"\n  {titulo}: Sin datos registrados."]
            blq = [f"\n  {titulo}"]
            blq.append(sep2)
            blq.append(f"  Método    : {d.get('metodo','N/A')}")
            blq.append(f"  Inversión : ${d.get('inversion',0):,.2f}")
            blq.append(f"  Tasa      : {d.get('tasa',0)*100:.2f}%")
            blq.append(f"  Vida      : {d.get('n',0)} años")
            blq.append(f"  Val. Sal. : ${d.get('vsal',0):,.2f}")
            flujos = d.get('flujos', [])
            blq.append(f"  Flujos    : {', '.join(f'${f:,.0f}' for f in flujos)}")
            if d.get('metodo') == "VPN":
                blq.append(f"  VPN       : ${d.get('vpn',0):,.2f}")
                blq.append(f"  Decisión  : {'ACEPTAR' if d.get('vpn',0) > 0 else 'RECHAZAR'}")
            elif d.get('metodo') == "CAE":
                blq.append(f"  VPN       : ${d.get('vpn',0):,.2f}")
                blq.append(f"  CAE       : ${d.get('cae',0):,.2f}/año")
                blq.append(f"  Decisión  : {'ACEPTAR' if d.get('cae',0) > 0 else 'RECHAZAR'}")
            elif d.get('metodo') == "TIR":
                tir = d.get('tir', 0)
                tmin = d.get('tmin', 0)
                blq.append(f"  TIR       : {tir*100:.4f}%")
                blq.append(f"  TMAR      : {tmin*100:.2f}%")
                blq.append(f"  Decisión  : {'ACEPTAR' if tir >= tmin else 'RECHAZAR'}")
            return blq

        lineas += bloque("ALTERNATIVA 1", self.app.resultado_alt1)
        lineas += bloque("ALTERNATIVA 2", self.app.resultado_alt2)

        lineas.append(f"\n{sep}")
        lineas.append("  Generado con SEAE – Sistema de Evaluación de Alternativas Económicas")
        lineas.append(sep)

        return "\n".join(lineas)

    def preview(self):
        txt = self._generar_texto()
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", txt)
        self.preview_text.config(state="disabled")

    def exportar_txt(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            title="Guardar reporte TXT",
            initialfile="reporte_SEAE.txt"
        )
        if not ruta:
            return
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self._generar_texto())
        messagebox.showinfo("Éxito", f"Reporte exportado:\n{ruta}")

    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            title="Guardar reporte CSV",
            initialfile="reporte_SEAE.csv"
        )
        if not ruta:
            return

        lineas = [
            "Campo,Alternativa 1,Alternativa 2",
            f"Método,{self.app.resultado_alt1.get('metodo','N/A')},{self.app.resultado_alt2.get('metodo','N/A')}",
            f"Inversión,{self.app.resultado_alt1.get('inversion',0)},{self.app.resultado_alt2.get('inversion',0)}",
            f"Tasa (%),{self.app.resultado_alt1.get('tasa',0)*100:.2f},{self.app.resultado_alt2.get('tasa',0)*100:.2f}",
            f"Vida (años),{self.app.resultado_alt1.get('n',0)},{self.app.resultado_alt2.get('n',0)}",
        ]
        for a, label in [(self.app.resultado_alt1, "Alt1"), (self.app.resultado_alt2, "Alt2")]:
            m = a.get('metodo', '')
            if m == "VPN":
                lineas.append(f"VPN,{a.get('vpn','')}," if label == "Alt1" else f",{a.get('vpn','')}")
            elif m == "CAE":
                lineas.append(f"CAE,{a.get('cae','')}," if label == "Alt1" else f",{a.get('cae','')}")
            elif m == "TIR":
                lineas.append(f"TIR (%),{a.get('tir',0)*100:.4f}," if label == "Alt1" else f",{a.get('tir',0)*100:.4f}")

        lineas.append(f"Equipo,{self.v_equipo.get()},")
        lineas.append(f"Integrantes,{self.v_integ.get()},")
        lineas.append(f"Fecha,{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')},")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
        messagebox.showinfo("Éxito", f"CSV exportado:\n{ruta}")


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
