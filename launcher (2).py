import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import tkinter as tk
import json, os, webbrowser, urllib.request, io, base64, threading, time

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── CONFIG ───────────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "nexus2024"
DATA_FILE      = "data.json"
VERSION        = "3.0.0"
REMOTE_URL     = "https://raw.githubusercontent.com/FNAF232619/Nexus-Launcher-json/refs/heads/main/data.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG      = "#0d1117"
SIDEBAR = "#161b22"
PANEL   = "#1c2128"
PANEL2  = "#22272e"
CARD    = "#1c2128"
BORDER  = "#30363d"
ACCENT  = "#c084fc"
ACC2    = "#818cf8"
ACC3    = "#38bdf8"
TEXT    = "#e6edf3"
TDIM    = "#8b949e"
GREEN   = "#3fb950"
RED     = "#f85149"
ORANGE  = "#d29922"
WHITE   = "#ffffff"

# ── HELPERS ──────────────────────────────────────────────────────────────────
def load_data():
    try:
        req = urllib.request.urlopen(REMOTE_URL, timeout=6)
        data = json.loads(req.read().decode("utf-8"))
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except: pass
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"apps": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_img(src, w, h):
    if not PIL_AVAILABLE or not src: return None
    try:
        if src.startswith("http"):
            with urllib.request.urlopen(src, timeout=5) as r: raw = r.read()
        else:
            b64 = src.split(",")[-1] if "," in src else src
            raw = base64.b64decode(b64)
        img = Image.open(io.BytesIO(raw)).resize((w, h), Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
    except: return None

def file_to_b64(path):
    if not PIL_AVAILABLE: return ""
    try:
        img = Image.open(path)
        img.thumbnail((800, 500), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""

# ── DETAIL POPUP ─────────────────────────────────────────────────────────────
class DetailPopup(ctk.CTkToplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.configure(fg_color=PANEL)
        self.title(app.get("name", ""))
        self.geometry("520x680")
        self.resizable(False, True)
        self.grab_set()
        self._refs = []
        self._build(app)

    def _build(self, app):
        # Title bar
        top = ctk.CTkFrame(self, fg_color=PANEL2, corner_radius=0, height=56)
        top.pack(fill="x"); top.pack_propagate(False)

        ctk.CTkLabel(top, text=app.get("name", ""),
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE).pack(side="left", padx=18, pady=14)

        ctk.CTkButton(top, text="✕", width=32, height=32,
                      fg_color="transparent", hover_color=BORDER,
                      text_color=TDIM, font=("Segoe UI", 13),
                      command=self.destroy).pack(side="right", padx=10, pady=10)

        # Subtitle row
        sub = ctk.CTkFrame(self, fg_color=PANEL2, corner_radius=0, height=30)
        sub.pack(fill="x"); sub.pack_propagate(False)

        subtitle_parts = []
        if app.get("tags"):
            subtitle_parts.append(f"Platform: {', '.join(app['tags'][:1])}")

        sub_text = "  •  ".join(subtitle_parts) if subtitle_parts else ""
        ctk.CTkLabel(sub, text=sub_text,
                     font=("Segoe UI", 10), text_color=TDIM).pack(side="left", padx=18)

        if app.get("new"):
            ctk.CTkLabel(sub, text="● NEU",
                         font=("Segoe UI", 10, "bold"),
                         text_color=ACCENT).pack(side="left", padx=4)

        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Scroll content
        scroll = ctk.CTkScrollableFrame(self, fg_color=PANEL,
                                         scrollbar_button_color=PANEL2)
        scroll.pack(fill="both", expand=True)

        p = ctk.CTkFrame(scroll, fg_color=PANEL)
        p.pack(fill="both", expand=True, padx=18, pady=16)

        # Main image
        imgs = app.get("images") or ([app["img"]] if app.get("img") else [])
        if imgs and PIL_AVAILABLE:
            frm = ctk.CTkFrame(p, fg_color=PANEL2, corner_radius=8, height=240)
            frm.pack(fill="x", pady=(0, 16)); frm.pack_propagate(False)
            lbl = ctk.CTkLabel(frm, text="⏳ Loading...", text_color=TDIM)
            lbl.pack(expand=True)
            def _load(src=imgs[0], l=lbl):
                ph = load_img(src, 480, 236)
                if ph:
                    self._refs.append(ph)
                    l.configure(image=ph, text="")
                else:
                    l.configure(text="🖼 Image not available")
            threading.Thread(target=_load, daemon=True).start()

        # Description header
        ctk.CTkFrame(p, fg_color=BORDER, height=1).pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(p, text="DESCRIPTION", font=("Segoe UI", 10, "bold"),
                     text_color=TDIM, anchor="w").pack(fill="x", pady=(0, 8))
        ctk.CTkFrame(p, fg_color=BORDER, height=1).pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(p, text=app.get("desc") or "No description available.",
                     font=("Segoe UI", 11), text_color=TEXT,
                     anchor="nw", justify="left", wraplength=460).pack(fill="x", pady=(0, 16))

        # Extra images
        extra = imgs[1:4] if len(imgs) > 1 else []
        if extra and PIL_AVAILABLE:
            eg = ctk.CTkFrame(p, fg_color=PANEL)
            eg.pack(fill="x", pady=(0, 16))
            for i, src in enumerate(extra):
                cell = ctk.CTkFrame(eg, fg_color=PANEL2, corner_radius=6, width=148, height=96)
                cell.grid(row=0, column=i, padx=(0, 8)); cell.pack_propagate(False)
                lbl2 = ctk.CTkLabel(cell, text="⏳", text_color=TDIM)
                lbl2.pack(expand=True)
                def _le(s=src, l=lbl2):
                    ph = load_img(s, 148, 96)
                    if ph:
                        self._refs.append(ph); l.configure(image=ph, text="")
                threading.Thread(target=_le, daemon=True).start()

        # Bottom buttons
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        btns = ctk.CTkFrame(self, fg_color=PANEL2, corner_radius=0, height=60)
        btns.pack(fill="x"); btns.pack_propagate(False)

        if app.get("url"):
            ctk.CTkButton(btns, text="Visit Website",
                          font=("Segoe UI", 12), fg_color=PANEL,
                          hover_color=BORDER, text_color=TEXT,
                          border_width=1, border_color=BORDER,
                          height=36, corner_radius=6,
                          command=lambda: webbrowser.open(app["url"])).pack(
                              side="left", padx=(14, 8), pady=12)

        ctk.CTkButton(btns, text="Close",
                      font=("Segoe UI", 12), fg_color=PANEL,
                      hover_color=BORDER, text_color=TEXT,
                      border_width=1, border_color=BORDER,
                      height=36, corner_radius=6,
                      command=self.destroy).pack(side="left", padx=(0, 14), pady=12)

        if app.get("discord"):
            ctk.CTkButton(btns, text="💬 Discord",
                          font=("Segoe UI", 12), fg_color="#5865F2",
                          hover_color="#4752c4", text_color=WHITE,
                          height=36, corner_radius=6,
                          command=lambda: webbrowser.open(app["discord"])).pack(
                              side="right", padx=14, pady=12)

# ── APP CARD ─────────────────────────────────────────────────────────────────
class AppCard(ctk.CTkFrame):
    def __init__(self, parent, app, on_more, on_website):
        super().__init__(parent, fg_color=CARD, corner_radius=10,
                         border_width=1, border_color=BORDER)
        self.app = app
        self._ref = None
        self._build(on_more, on_website)

    def _build(self, on_more, on_website):
        app = self.app

        # Image
        imf = ctk.CTkFrame(self, fg_color=PANEL2, corner_radius=8, height=160)
        imf.pack(fill="x", padx=2, pady=(2, 0)); imf.pack_propagate(False)
        self._il = ctk.CTkLabel(imf, text="🎮", font=("Segoe UI Emoji", 38), text_color=TDIM)
        self._il.pack(expand=True)

        if app.get("new"):
            ctk.CTkLabel(self, text=" NEU ", font=("Segoe UI", 8, "bold"),
                         text_color=WHITE, fg_color=ACCENT,
                         corner_radius=4).place(x=10, y=10)

        # Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(body, text=app.get("name", ""),
                     font=("Segoe UI", 14, "bold"),
                     text_color=WHITE, anchor="w").pack(fill="x")

        # Tags as "Plattform"
        if app.get("tags"):
            ctk.CTkLabel(body, text=f"Platform:  {', '.join(app['tags'][:2])}",
                         font=("Segoe UI", 10), text_color=TDIM, anchor="w").pack(fill="x", pady=(2, 0))

        # Version as "Bann Risiko" style info
        if app.get("version"):
            vrow = ctk.CTkFrame(body, fg_color="transparent")
            vrow.pack(anchor="w", pady=(2, 6))
            ctk.CTkLabel(vrow, text="Version:  ",
                         font=("Segoe UI", 10), text_color=TDIM).pack(side="left")
            ctk.CTkLabel(vrow, text=f"v{app['version']}",
                         font=("Segoe UI", 10, "bold"), text_color=ACCENT).pack(side="left")

        # Buttons
        brow = ctk.CTkFrame(body, fg_color="transparent")
        brow.pack(fill="x", pady=(4, 0))

        ctk.CTkButton(brow, text="More Info",
                      font=("Segoe UI", 11), fg_color=PANEL2,
                      hover_color=BORDER, text_color=TEXT,
                      border_width=1, border_color=BORDER,
                      height=32, corner_radius=6,
                      command=lambda: on_more(app)).pack(side="left", padx=(0, 8))

        if app.get("url"):
            ctk.CTkButton(brow, text="Website  →",
                          font=("Segoe UI", 11), fg_color=PANEL2,
                          hover_color=BORDER, text_color=TEXT,
                          border_width=1, border_color=BORDER,
                          height=32, corner_radius=6,
                          command=lambda: webbrowser.open(app["url"])).pack(side="left")

        # Load image
        imgs = app.get("images") or ([app["img"]] if app.get("img") else [])
        if imgs and PIL_AVAILABLE:
            threading.Thread(target=self._load_img, args=(imgs[0],), daemon=True).start()

    def _load_img(self, src):
        ph = load_img(src, 280, 160)
        if ph:
            self._ref = ph
            self._il.configure(image=ph, text="")

# ── MAIN APP ─────────────────────────────────────────────────────────────────
class NexusLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Nexus Launcher v{VERSION}")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG)
        self.connected = False

        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
            elif os.path.exists("icon.png") and PIL_AVAILABLE:
                img = Image.open("icon.png")
                self.iconphoto(True, ImageTk.PhotoImage(img))
        except: pass

        self.data = {"apps": []}
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.render_apps())
        self.current_page = "home"
        self._build_ui()
        self.after(300, lambda: threading.Thread(target=self._load_async, daemon=True).start())

    def _load_async(self):
        try:
            urllib.request.urlopen(REMOTE_URL, timeout=3)
            self.connected = True
        except:
            self.connected = False
        self.data = load_data()
        self.after(0, self._on_loaded)

    def _on_loaded(self):
        status = "Connected" if self.connected else "Offline"
        color = GREEN if self.connected else RED
        self.status_lbl.configure(text=f"Status: {status}", text_color=color)
        self.render_apps()

    def _build_ui(self):
        # ── SIDEBAR ──
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=0, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=SIDEBAR, height=70)
        logo_frame.pack(fill="x"); logo_frame.pack_propagate(False)
        lf = ctk.CTkFrame(logo_frame, fg_color=SIDEBAR)
        lf.pack(side="left", padx=18, pady=18)
        ctk.CTkLabel(lf, text="N", font=("Segoe UI", 22, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(lf, text="EXUS", font=("Segoe UI", 22, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(lf, text=f" v{VERSION}", font=("Segoe UI", 9), text_color=TDIM).pack(side="left", pady=(5,0))

        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Nav items
        nav_items = [
            ("🏠  Home",    "home"),
            ("🛡  Admin Panel",   "admin"),
            ("⚙  Settings", "settings"),
            ("ℹ  Info",          "info"),
        ]

        self.nav_btns = {}
        for label, page in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=label,
                                font=("Segoe UI", 13), height=44,
                                fg_color=PANEL if page == "home" else "transparent",
                                hover_color=PANEL2, text_color=WHITE if page=="home" else TDIM,
                                anchor="w", corner_radius=6,
                                command=lambda p=page: self._nav(p))
            btn.pack(fill="x", padx=10, pady=(6,0))
            self.nav_btns[page] = btn

        # Bottom status
        ctk.CTkFrame(self.sidebar, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", side="bottom", pady=(0,50))
        self.status_lbl = ctk.CTkLabel(self.sidebar, text="Status: Connecting...",
                                        font=("Segoe UI", 11), text_color=TDIM)
        self.status_lbl.pack(side="bottom", padx=16, pady=12, anchor="w")

        # ── MAIN CONTENT ──
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

        # Search bar
        search_bar = ctk.CTkFrame(self.main, fg_color=SIDEBAR, corner_radius=0, height=56)
        search_bar.pack(fill="x"); search_bar.pack_propagate(False)

        ctk.CTkEntry(search_bar, textvariable=self.search_var,
                     placeholder_text="🔍  Search...",
                     font=("Segoe UI", 12), height=36,
                     fg_color=PANEL, border_color=BORDER,
                     text_color=TEXT, placeholder_text_color=TDIM,
                     corner_radius=8).pack(side="left", fill="x", expand=True,
                                            padx=16, pady=10)

        self.count_lbl = ctk.CTkLabel(search_bar, text="",
                                       font=("Segoe UI", 11), text_color=TDIM)
        self.count_lbl.pack(side="right", padx=16)

        ctk.CTkFrame(self.main, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Page container
        self.page_frame = ctk.CTkFrame(self.main, fg_color=BG, corner_radius=0)
        self.page_frame.pack(fill="both", expand=True)

        self._show_home()

    def _nav(self, page):
        for p, btn in self.nav_btns.items():
            if p == page:
                btn.configure(fg_color=PANEL, text_color=WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=TDIM)
        self.current_page = page
        for w in self.page_frame.winfo_children(): w.destroy()

        if page == "home":     self._show_home()
        elif page == "admin":  self._show_admin_prompt()
        elif page == "settings": self._show_settings()
        elif page == "info":   self._show_info()

    def _show_home(self):
        self.scroll = ctk.CTkScrollableFrame(self.page_frame, fg_color=BG,
                                              scrollbar_button_color=PANEL2,
                                              scrollbar_button_hover_color=ACCENT)
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)
        self.after(100, self.render_apps)

    def render_apps(self):
        if not hasattr(self, 'scroll'): return
        for w in self.scroll.winfo_children(): w.destroy()

        q = self.search_var.get().lower()
        apps = [a for a in self.data.get("apps", [])
                if not q or q in a.get("name","").lower() or q in a.get("desc","").lower()]

        n = len(self.data.get("apps", []))
        self.count_lbl.configure(text=f"{n} Apps")

        if not apps:
            ctk.CTkLabel(self.scroll,
                         text="Noch keine Apps." if not q else "Nothing found.",
                         font=("Segoe UI", 15), text_color=TDIM,
                         justify="center").pack(pady=100)
            return

        cw = self.scroll.winfo_width() or 860
        cols = max(1, (cw - 20) // 300)

        for i, app in enumerate(apps):
            r, c = divmod(i, cols)
            card = AppCard(self.scroll, app,
                           on_more=self._open_detail,
                           on_website=lambda a: webbrowser.open(a.get("url","")))
            card.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")

        for c in range(cols):
            self.scroll.columnconfigure(c, weight=1, uniform="col")

    def _open_detail(self, app):
        DetailPopup(self, app)

    def _show_admin_prompt(self):
        pw = simpledialog.askstring("Admin Login", "Passwort:", show="*", parent=self)
        if pw is None:
            self._nav("home"); return
        if pw != ADMIN_PASSWORD:
            messagebox.showerror("Fehler", "Wrong password!")
            self._nav("home"); return
        AdminWindow(self)
        self._nav("home")

    def _show_settings(self):
        p = ctk.CTkFrame(self.page_frame, fg_color=BG)
        p.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(p, text="Settings", font=("Segoe UI", 20, "bold"),
                     text_color=WHITE).pack(anchor="w", pady=(0,20))

        box = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=10)
        box.pack(fill="x", pady=(0,12))
        ctk.CTkLabel(box, text="GitHub Data URL",
                     font=("Segoe UI", 11, "bold"), text_color=TEXT).pack(anchor="w", padx=16, pady=(14,4))
        ctk.CTkLabel(box, text=REMOTE_URL, font=("Segoe UI", 9),
                     text_color=TDIM, wraplength=600).pack(anchor="w", padx=16, pady=(0,14))

        ctk.CTkButton(p, text="↻  Refresh Now", height=38,
                      fg_color=ACCENT, hover_color=ACC2, text_color=WHITE,
                      font=("Segoe UI", 12), corner_radius=8, width=200,
                      command=self.refresh).pack(anchor="w", pady=10)

    def _show_info(self):
        p = ctk.CTkFrame(self.page_frame, fg_color=BG)
        p.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(p, text="Info", font=("Segoe UI", 20, "bold"),
                     text_color=WHITE).pack(anchor="w", pady=(0,20))

        box = ctk.CTkFrame(p, fg_color=PANEL, corner_radius=10)
        box.pack(fill="x")
        for label, val in [("App", f"NEXUS Launcher"),
                            ("Version", f"v{VERSION}"),
                            ("Built with", "Python + CustomTkinter"),
                            ("Data Source", "GitHub")]:
            row = ctk.CTkFrame(box, fg_color=PANEL)
            row.pack(fill="x", padx=16, pady=8)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 11),
                         text_color=TDIM, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Segoe UI", 11),
                         text_color=TEXT, anchor="w").pack(side="left")

    def refresh(self):
        self.status_lbl.configure(text="Status: Connecting...", text_color=TDIM)
        threading.Thread(target=self._load_async, daemon=True).start()

# ── ADMIN WINDOW ──────────────────────────────────────────────────────────────
class AdminWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("NEXUS — Admin Panel")
        self.geometry("960x680")
        self.configure(fg_color=BG)
        self.grab_set()
        self.editing_id = None
        self.images = []
        self._build()
        self._refresh_list()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=SIDEBAR, corner_radius=0, height=58)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🛡  Admin Panel",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(side="left", padx=20, pady=14)
        ctk.CTkButton(hdr, text="+ New App", width=130, height=36,
                      fg_color=ACCENT, hover_color=ACC2, text_color=WHITE,
                      font=("Segoe UI", 11, "bold"), corner_radius=8,
                      command=self._new).pack(side="right", padx=16, pady=10)
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.pack(fill="both", expand=True)

        # List
        left = ctk.CTkFrame(main, fg_color=SIDEBAR, corner_radius=0, width=240)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        ctk.CTkLabel(left, text="APPS", font=("Segoe UI", 9, "bold"),
                     text_color=TDIM).pack(anchor="w", padx=14, pady=(14,6))
        self.lb = tk.Listbox(left, font=("Segoe UI", 11), fg=TEXT, bg=SIDEBAR,
                              selectbackground=ACCENT, selectforeground=WHITE,
                              relief="flat", bd=0, highlightthickness=0, activestyle="none")
        self.lb.pack(fill="both", expand=True, padx=6)
        self.lb.bind("<<ListboxSelect>>", self._select)
        ctk.CTkButton(left, text="🗑  Delete", width=200, height=36,
                      fg_color="transparent", border_width=1, border_color=BORDER,
                      hover_color=PANEL, text_color=TDIM, font=("Segoe UI", 10),
                      corner_radius=8, command=self._delete).pack(padx=10, pady=10)

        ctk.CTkFrame(main, fg_color=BORDER, width=1, corner_radius=0).pack(side="left", fill="y")

        # Form
        right = ctk.CTkScrollableFrame(main, fg_color=BG, scrollbar_button_color=PANEL2)
        right.pack(side="left", fill="both", expand=True)
        p = ctk.CTkFrame(right, fg_color=BG)
        p.pack(fill="both", expand=True, padx=24, pady=20)

        self.form_title = ctk.CTkLabel(p, text="Select an app or create new",
                                        font=("Segoe UI", 14, "bold"), text_color=ACCENT, anchor="w")
        self.form_title.pack(fill="x", pady=(0, 16))

        self.fields = {}
        for key, lbl in [("name","App Name *"),("version","Version"),
                          ("url","Download URL *"),("discord","Discord Link (optional)"),
                          ("tags","Tags / Platform (comma separated)")]:
            ctk.CTkLabel(p, text=lbl, font=("Segoe UI", 10), text_color=TDIM, anchor="w").pack(fill="x", pady=(0,3))
            e = ctk.CTkEntry(p, font=("Segoe UI", 12), height=38,
                             fg_color=PANEL, border_color=BORDER, text_color=TEXT, corner_radius=8)
            e.pack(fill="x", pady=(0, 10))
            self.fields[key] = e

        ctk.CTkLabel(p, text="Description", font=("Segoe UI", 10), text_color=TDIM, anchor="w").pack(fill="x", pady=(0,3))
        self.desc = ctk.CTkTextbox(p, font=("Segoe UI", 11), height=110,
                                    fg_color=PANEL, border_color=BORDER, text_color=TEXT, corner_radius=8)
        self.desc.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(p, text="BILDER", font=("Segoe UI", 10, "bold"), text_color=TDIM, anchor="w").pack(fill="x", pady=(0,4))
        ctk.CTkLabel(p, text="Imageer direkt vom PC wählen – werden in der JSON saved!",
                     font=("Segoe UI", 9), text_color=ACC2, anchor="w").pack(fill="x", pady=(0,8))

        ibf = ctk.CTkFrame(p, fg_color="transparent")
        ibf.pack(fill="x", pady=(0,6))
        ctk.CTkButton(ibf, text="📁 Main Image", width=130, height=36,
                      fg_color=ACCENT, hover_color=ACC2, text_color=WHITE,
                      font=("Segoe UI", 10), corner_radius=8,
                      command=self._pick_main).pack(side="left", padx=(0,8))
        ctk.CTkButton(ibf, text="📁 + Image", width=110, height=36,
                      fg_color=PANEL, hover_color=PANEL2, border_width=1, border_color=BORDER,
                      text_color=TEXT, font=("Segoe UI", 10), corner_radius=8,
                      command=self._pick_extra).pack(side="left", padx=(0,8))
        ctk.CTkButton(ibf, text="🗑 Delete", width=110, height=36,
                      fg_color=PANEL, hover_color=PANEL2, text_color=TDIM,
                      font=("Segoe UI", 10), corner_radius=8,
                      command=self._clear_imgs).pack(side="left")

        self.img_lbl = ctk.CTkLabel(p, text="No images", font=("Segoe UI", 10), text_color=TDIM, anchor="w")
        self.img_lbl.pack(fill="x", pady=(0,14))

        self.new_var = ctk.BooleanVar()
        ctk.CTkCheckBox(p, text='Mark as "NEW"', variable=self.new_var,
                        font=("Segoe UI", 11), text_color=TEXT,
                        fg_color=ACCENT, hover_color=ACC2, corner_radius=4).pack(anchor="w", pady=(0,16))

        ctk.CTkButton(p, text="💾  SAVE", height=46,
                      fg_color=ACCENT, hover_color=ACC2, text_color=WHITE,
                      font=("Segoe UI", 13, "bold"), corner_radius=10,
                      command=self._save).pack(fill="x")

    def _refresh_list(self):
        self.lb.delete(0, tk.END)
        for a in self.parent.data.get("apps", []):
            self.lb.insert(tk.END, f"  {a.get('name','?')}")

    def _select(self, e):
        sel = self.lb.curselection()
        if not sel: return
        app = self.parent.data["apps"][sel[0]]
        self.editing_id = app.get("id")
        self.form_title.configure(text=f"✏  {app.get('name','')}")
        for k, entry in self.fields.items():
            entry.delete(0, tk.END)
            entry.insert(0, ", ".join(app.get("tags",[])) if k=="tags" else str(app.get(k,"") or ""))
        self.desc.delete("1.0", tk.END)
        self.desc.insert("1.0", app.get("desc",""))
        self.new_var.set(app.get("new", False))
        self.images = list(app.get("images",[]))
        self._upd_img()

    def _new(self):
        self.editing_id = None
        self.form_title.configure(text="➕  New App")
        for e in self.fields.values(): e.delete(0, tk.END)
        self.desc.delete("1.0", tk.END)
        self.new_var.set(False)
        self.images = []
        self._upd_img()
        self.lb.selection_clear(0, tk.END)

    def _pick_main(self):
        path = filedialog.askopenfilename(
            filetypes=[("Imageer","*.png *.jpg *.jpeg *.gif *.bmp *.webp")], parent=self)
        if not path: return
        b = file_to_b64(path)
        if b:
            if self.images: self.images[0] = b
            else: self.images.insert(0, b)
            self._upd_img()
            messagebox.showinfo("✓","Hauptbild saved!", parent=self)

    def _pick_extra(self):
        path = filedialog.askopenfilename(
            filetypes=[("Imageer","*.png *.jpg *.jpeg *.gif *.bmp *.webp")], parent=self)
        if not path: return
        b = file_to_b64(path)
        if b:
            self.images.append(b)
            self._upd_img()
            messagebox.showinfo("✓","Image added!", parent=self)

    def _clear_imgs(self):
        self.images = []; self._upd_img()

    def _upd_img(self):
        n = len(self.images)
        self.img_lbl.configure(
            text=f"✓ {n} Image{'er' if n>1 else ''} gespeichert" if n else "No images",
            text_color=GREEN if n else TDIM)

    def _save(self):
        name = self.fields["name"].get().strip()
        url  = self.fields["url"].get().strip()
        if not name:
            messagebox.showwarning("Fehler","Please enter an app name!", parent=self); return
        if not url:
            messagebox.showwarning("Fehler","Please enter a download URL!", parent=self); return
        tags = [t.strip() for t in self.fields["tags"].get().split(",") if t.strip()]
        app = {
            "id":      self.editing_id or int(time.time()*1000),
            "name":    name,
            "version": self.fields["version"].get().strip(),
            "url":     url,
            "discord": self.fields["discord"].get().strip(),
            "tags":    tags,
            "images":  self.images,
            "img":     self.images[0] if self.images else "",
            "desc":    self.desc.get("1.0", tk.END).strip(),
            "new":     self.new_var.get(),
        }
        apps = self.parent.data.setdefault("apps",[])
        if self.editing_id:
            idx = next((i for i,a in enumerate(apps) if a.get("id")==self.editing_id), None)
            if idx is not None: apps[idx] = app
        else:
            apps.append(app); self.editing_id = app["id"]
        save_data(self.parent.data)
        self._refresh_list()
        self.parent.render_apps()
        messagebox.showinfo("✓", f'"{name}" saved!', parent=self)

    def _delete(self):
        sel = self.lb.curselection()
        if not sel:
            messagebox.showinfo("Hinweis","Please select an app first.", parent=self); return
        app = self.parent.data["apps"][sel[0]]
        if not messagebox.askyesno("Delete", f'"{app["name"]}" really delete?', parent=self): return
        self.parent.data["apps"].pop(sel[0])
        save_data(self.parent.data)
        self._refresh_list()
        self._new()
        self.parent.render_apps()

if __name__ == "__main__":
    NexusLauncher().mainloop()
