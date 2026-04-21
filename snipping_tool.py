"""
WinScreen — Capture d'écran & Enregistrement vidéo
Design : Dark Mode Élégant + accents néons
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import mss
import io
import subprocess
import threading
import time
import os

# ffmpeg.exe local (dans le même dossier) ou fallback PATH
_DIR = os.path.dirname(os.path.abspath(__file__))

def _ffmpeg() -> str:
    local = os.path.join(_DIR, "ffmpeg.exe")
    return local if os.path.exists(local) else "ffmpeg"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Palette ───────────────────────────────────────────────────
BG      = "#07070E"
SURFACE = "#0C0C18"
CARD    = "#10101C"
CARD_H  = "#15152A"
CARD_S  = "#160F38"
ACCENT  = "#7C6FFF"
A_HOVER = "#9488FF"
CYAN    = "#00CFFF"
GREEN   = "#00FF88"
PINK    = "#FF6B9D"
RED_REC = "#FF3355"
RED_H   = "#FF5577"
TEXT    = "#E8E8FF"
MUTED   = "#4A4A72"
DIM     = "#252538"
BORDER  = "#1A1A2E"

# ── Polices (init après fenêtre) ──────────────────────────────
F_TITLE = F_LABEL = F_BOLD = F_SMALL = F_ICON = None

def _init_fonts():
    global F_TITLE, F_LABEL, F_BOLD, F_SMALL, F_ICON
    F_TITLE = ctk.CTkFont(family="Segoe UI", size=17, weight="bold")
    F_LABEL = ctk.CTkFont(family="Segoe UI", size=11)
    F_BOLD  = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
    F_SMALL = ctk.CTkFont(family="Segoe UI", size=10)
    F_ICON  = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")


# ──────────────────────────────────────────────────────────────
class Tooltip:
    """Infobulle légère au survol."""
    def __init__(self, widget, text: str):
        self._text = text
        self._win  = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, e):
        x = e.widget.winfo_rootx() + 20
        y = e.widget.winfo_rooty() + 32
        self._win = tk.Toplevel()
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.geometry(f"+{x}+{y}")
        tk.Label(self._win, text=self._text, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 9), padx=7, pady=4).pack()

    def _hide(self, _):
        if self._win:
            self._win.destroy()
            self._win = None


# ──────────────────────────────────────────────────────────────
class SelectionOverlay:
    """Overlay plein écran — sélection rectangle uniquement."""

    def __init__(self, on_done=None, on_cancel=None):
        self.on_done   = on_done
        self.on_cancel = on_cancel
        self.sx = self.sy = 0

        self.ov = tk.Toplevel()
        self.ov.attributes("-fullscreen", True)
        self.ov.attributes("-topmost", True)
        self.ov.attributes("-alpha", 0.35)
        self.ov.config(bg="black", cursor="crosshair")
        self.ov.overrideredirect(True)

        self.cv = tk.Canvas(self.ov, bg="black",
                            cursor="crosshair", highlightthickness=0)
        self.cv.pack(fill=tk.BOTH, expand=True)

        sw = self.ov.winfo_screenwidth()
        self.cv.create_text(sw // 2, 28,
            text="Cliquez et glissez pour sélectionner.  Échap = annuler.",
            fill="white", font=("Segoe UI", 13, "bold"), tags="hint")

        self.cv.bind("<ButtonPress-1>",   self._press)
        self.cv.bind("<B1-Motion>",       self._drag)
        self.cv.bind("<ButtonRelease-1>", self._release)
        self.ov.bind("<Escape>",          self._escape)
        self.ov.focus_force()

    def _press(self, e):
        self.sx, self.sy = e.x, e.y

    def _drag(self, e):
        self.cv.delete("sel")
        self.cv.create_rectangle(self.sx, self.sy, e.x, e.y,
            outline=CYAN, width=2, tags="sel")
        w, h = abs(e.x - self.sx), abs(e.y - self.sy)
        self.cv.delete("hint")
        self.cv.create_text(e.x + 70, e.y + 16,
            text=f"{w} × {h} px", fill="white",
            font=("Segoe UI", 10, "bold"), tags="sel")

    def _release(self, e):
        self.ov.destroy()
        x1, y1 = min(self.sx, e.x), min(self.sy, e.y)
        x2, y2 = max(self.sx, e.x), max(self.sy, e.y)
        if x2 - x1 > 5 and y2 - y1 > 5 and self.on_done:
            self.on_done((x1, y1, x2, y2))
        elif self.on_cancel:
            self.on_cancel()

    def _escape(self, _):
        self.ov.destroy()
        if self.on_cancel:
            self.on_cancel()


# ──────────────────────────────────────────────────────────────
class ToolBtn(ctk.CTkButton):
    """Bouton icône compact avec état actif."""

    def __init__(self, parent, icon: str, value: str,
                 tool_var: tk.StringVar, on_change=None, **kw):
        super().__init__(
            parent, text=icon,
            width=36, height=30, corner_radius=9,
            fg_color="transparent", border_width=1,
            border_color=BORDER, text_color=MUTED,
            hover_color=CARD_H, font=F_ICON,
            command=lambda: (tool_var.set(value),
                             on_change and on_change()),
            **kw,
        )
        self.value = value
        self.tool_var = tool_var
        tool_var.trace_add("write", self._sync)
        self._sync()

    def _sync(self, *_):
        if self.tool_var.get() == self.value:
            self.configure(fg_color=ACCENT, border_color=ACCENT,
                           text_color="white", hover_color=A_HOVER)
        else:
            self.configure(fg_color="transparent", border_color=BORDER,
                           text_color=MUTED, hover_color=CARD_H)


# ──────────────────────────────────────────────────────────────
class ScreenRecorder:
    """Enregistrement d'écran via mss + ffmpeg."""

    RESOLUTIONS = {
        "1080p  (1920×1080)": (1920, 1080),
        "1440p  (2560×1440)": (2560, 1440),
        "4K  (3840×2160)":    (3840, 2160),
        "Natif (auto)":       None,
    }
    CODECS = {
        "H.264  (compatible)": {
            "nvenc": "h264_nvenc", "amd": "h264_amf",
            "qsv":  "h264_qsv",   "cpu": "libx264",
        },
        "H.265 / HEVC": {
            "nvenc": "hevc_nvenc", "amd": "hevc_amf",
            "qsv":  "hevc_qsv",   "cpu": "libx265",
        },
        "AV1": {
            "nvenc": "av1_nvenc", "amd": "av1_amf",
            "qsv":  "av1_qsv",   "cpu": "libsvtav1",
        },
    }
    ENCODERS = {
        "Auto  (GPU → CPU)":    "auto",
        "NVENC  (NVIDIA)":      "nvenc",
        "AMF  (AMD)":           "amd",
        "QuickSync  (Intel)":   "qsv",
        "CPU  (logiciel)":      "cpu",
    }
    BITRATE_DEFAULTS = {
        "1080p  (1920×1080)": {"30": 8000,  "60": 12000},
        "1440p  (2560×1440)": {"30": 16000, "60": 24000},
        "4K  (3840×2160)":    {"30": 35000, "60": 60000},
        "Natif (auto)":       {"30": 10000, "60": 15000},
    }

    def __init__(self):
        self.recording    = False
        self.paused       = False
        self._proc        = None
        self._start_time  = 0.0
        self._pause_start = 0.0

    # ── API publique ──────────────────────────────────────────

    @staticmethod
    def ffmpeg_available() -> bool:
        try:
            subprocess.run([_ffmpeg(), "-version"],
                           capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    @staticmethod
    def get_monitors() -> list:
        """Retourne [(label, mon_dict), ...] pour chaque moniteur physique."""
        result = []
        with mss.mss() as sct:
            for i, mon in enumerate(sct.monitors[1:], 1):
                label = f"Écran {i}  ({mon['width']}×{mon['height']})"
                if mon["left"] != 0 or mon["top"] != 0:
                    label += f"  +{mon['left']},{mon['top']}"
                result.append((label, dict(mon)))
        return result

    def start(self, output_path: str, res_label: str, fps: int,
              codec_name: str, bitrate: int, encoder_label: str,
              monitor: dict, audio_mode: str = "Aucun",
              on_error=None) -> bool:
        nw, nh = monitor["width"], monitor["height"]
        ox, oy = monitor["left"],  monitor["top"]

        res = self.RESOLUTIONS.get(res_label)
        tw, th = (nw, nh) if res is None else res

        enc_key = self.ENCODERS.get(encoder_label, "auto")
        try:
            vcodec = self._resolve_encoder(codec_name, enc_key)
        except Exception:
            vcodec = "libx264"

        cmd = [
            _ffmpeg(), "-y",
            "-f", "gdigrab",
            "-framerate", str(fps),
            "-probesize", "100M",
            "-offset_x", str(ox),
            "-offset_y", str(oy),
            "-video_size", f"{nw}x{nh}",
            "-draw_mouse", "1",
            "-i", "desktop",
        ]

        if audio_mode == "Microphone":
            cmd += ["-f", "wasapi", "-i", "default"]
        elif audio_mode == "Son système":
            cmd += ["-f", "wasapi", "-loopback", "1", "-i", "default"]

        vf_filters = []
        if (tw, th) != (nw, nh):
            vf_filters.append(f"scale={tw}:{th}")
        vf_filters.append(f"fps={fps}")
        cmd += ["-vf", ",".join(vf_filters)]
        cmd += [
            "-vcodec", vcodec,
            "-r", str(fps),
            "-vsync", "cfr",
            "-b:v",    f"{bitrate}k",
            "-maxrate", f"{bitrate * 2}k",
            "-bufsize",  f"{bitrate * 4}k",
            "-pix_fmt", "yuv420p",
        ]
        if audio_mode != "Aucun":
            cmd += ["-acodec", "aac", "-b:a", "192k"]
        cmd.append(output_path)

        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self._stderr_lines = []
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=flags,
            )
        except Exception as exc:
            if on_error:
                on_error(str(exc))
            return False

        # Drainer stderr dans un thread daemon pour éviter le blocage du buffer
        def _drain():
            try:
                for raw in self._proc.stderr:
                    line = raw.decode("utf-8", errors="replace").rstrip()
                    if line:
                        self._stderr_lines.append(line)
                        if len(self._stderr_lines) > 30:
                            self._stderr_lines.pop(0)
            except Exception:
                pass
        threading.Thread(target=_drain, daemon=True).start()

        self.recording   = True
        self.paused      = False
        self._start_time = time.time()
        return True

    def stop(self):
        """Arrête ffmpeg proprement en envoyant 'q' sur stdin."""
        if self.paused:
            self._resume_process()
        self.recording = False
        self.paused    = False
        if self._proc:
            try:
                self._proc.stdin.write(b"q")
                self._proc.stdin.flush()
            except Exception:
                pass
            try:
                self._proc.wait(timeout=60)
            except Exception:
                self._proc.kill()
        self._proc = None

    def pause(self):
        if self.recording and not self.paused and self._proc:
            self._suspend_process()
            self.paused       = True
            self._pause_start = time.time()

    def resume(self):
        if self.recording and self.paused and self._proc:
            self._resume_process()
            self._start_time += time.time() - self._pause_start
            self.paused = False

    def elapsed(self) -> str:
        if self.paused:
            s = int(self._pause_start - self._start_time)
        elif self.recording:
            s = int(time.time() - self._start_time)
        else:
            s = 0
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    def _suspend_process(self):
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, self._proc.pid)
        ctypes.windll.ntdll.NtSuspendProcess(h)
        ctypes.windll.kernel32.CloseHandle(h)

    def _resume_process(self):
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, self._proc.pid)
        ctypes.windll.ntdll.NtResumeProcess(h)
        ctypes.windll.kernel32.CloseHandle(h)

    # ── Interne ───────────────────────────────────────────────

    def _resolve_encoder(self, codec_name: str, enc_key: str) -> str:
        cmap = self.CODECS.get(codec_name, self.CODECS["H.264  (compatible)"])
        if enc_key != "auto":
            return cmap.get(enc_key, "libx264")
        for key in ("nvenc", "amd", "qsv", "cpu"):
            enc = cmap[key]
            r = subprocess.run(
                [_ffmpeg(), "-f", "lavfi", "-i",
                 "nullsrc=s=64x64:r=1:d=0.1",
                 "-vcodec", enc, "-f", "null", "-"],
                capture_output=True, timeout=6,
            )
            if r.returncode == 0:
                return enc
        return "libx264"


# ──────────────────────────────────────────────────────────────
class WinScreen:

    CURSOR_FOR_TOOL = {
        "pen": "crosshair", "highlighter": "crosshair",
        "eraser": "circle",  "text": "xterm",
    }

    def __init__(self):
        self.root = ctk.CTk()
        _init_fonts()
        self.root.title("WinScreen")
        self.root.geometry("980x720")
        self.root.minsize(700, 500)
        self.root.configure(fg_color=BG)

        # état capture
        self.tool_var       = tk.StringVar(value="pen")
        self.width_var      = tk.IntVar(value=2)
        self.pen_color      = "#FF4D8D"
        self.captured_image = None
        self.photo_image    = None
        self.drawing        = False
        self.last_x = self.last_y = 0
        self.undo_stack: list = []
        self.redo_stack: list = []

        # état enregistrement
        self.recorder     = ScreenRecorder()
        self._monitors    = ScreenRecorder.get_monitors()  # [(label, dict), ...]
        self._monitor_var = tk.StringVar(
            value=self._monitors[0][0] if self._monitors else "")
        self._res_var     = tk.StringVar(value="1080p  (1920×1080)")
        self._fps_var     = tk.StringVar(value="60")
        self._codec_var   = tk.StringVar(value="H.264  (compatible)")
        self._enc_var     = tk.StringVar(value="Auto  (GPU → CPU)")
        self._bitrate_var = tk.IntVar(value=12000)
        self._audio_var   = tk.StringVar(value="Aucun")

        self._build_ui()
        self.root.mainloop()

    # ── Construction UI ───────────────────────────────────────

    def _build_ui(self):
        self._build_menu()
        self._build_header()
        self._build_tools_row()
        self._build_record_panel()
        self._build_canvas()
        self._build_statusbar()
        self._bind_shortcuts()

    def _build_menu(self):
        mb = tk.Menu(self.root, bg=CARD, fg=TEXT,
                     activebackground=ACCENT, activeforeground="white",
                     bd=0, tearoff=False)
        fm = tk.Menu(mb, bg=CARD, fg=TEXT,
                     activebackground=ACCENT, activeforeground="white",
                     bd=0, tearoff=False)
        fm.add_command(label="Nouvelle capture   Ctrl+N", command=self.new_capture)
        fm.add_separator()
        fm.add_command(label="Enregistrer sous…  Ctrl+S", command=self.save_image)
        fm.add_command(label="Copier             Ctrl+C", command=self.copy_to_clipboard)
        fm.add_separator()
        fm.add_command(label="Quitter", command=self.root.quit)
        mb.add_cascade(label="Fichier", menu=fm)
        em = tk.Menu(mb, bg=CARD, fg=TEXT,
                     activebackground=ACCENT, activeforeground="white",
                     bd=0, tearoff=False)
        em.add_command(label="Annuler   Ctrl+Z", command=self.undo)
        em.add_command(label="Rétablir  Ctrl+Y", command=self.redo)
        mb.add_cascade(label="Modifier", menu=em)
        self.root.config(menu=mb)

    def _build_header(self):
        hdr = ctk.CTkFrame(self.root, fg_color=SURFACE,
                           corner_radius=0, height=58)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.pack(side=tk.LEFT, padx=20, pady=10)
        ctk.CTkLabel(logo, text="◈ ", font=ctk.CTkFont(size=18),
                     text_color=ACCENT).pack(side=tk.LEFT)
        ctk.CTkLabel(logo, text="WinScreen", font=F_TITLE,
                     text_color=TEXT).pack(side=tk.LEFT)

        btns = ctk.CTkFrame(hdr, fg_color="transparent")
        btns.pack(side=tk.RIGHT, padx=16, pady=10)

        for txt, cmd, primary, color in [
            ("📋  Copier",       self.copy_to_clipboard, False, None),
            ("💾  Enregistrer",  self.save_image,         False, None),
            ("  📷  Capturer",   self.new_capture,        True,  ACCENT),
        ]:
            ctk.CTkButton(
                btns, text=txt, command=cmd,
                width=158 if primary else 126,
                height=38 if primary else 34,
                corner_radius=19 if primary else 17,
                fg_color=color or "transparent",
                hover_color=A_HOVER if primary else CARD_H,
                border_width=0 if primary else 1,
                border_color=BORDER,
                text_color="white" if primary else MUTED,
                font=ctk.CTkFont(
                    family="Segoe UI", size=12, weight="bold"
                ) if primary else F_BOLD,
            ).pack(side=tk.LEFT, padx=4)

    def _build_tools_row(self):
        card = ctk.CTkFrame(self.root, corner_radius=14, fg_color=CARD,
                            border_width=1, border_color=BORDER)
        card.pack(fill=tk.X, padx=14, pady=(10, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(padx=12, pady=6, fill=tk.X)

        # Outils (icônes compactes)
        tools = [
            ("✏", "pen",         "Stylo"),
            ("▐", "highlighter", "Surligneur"),
            ("◻", "eraser",      "Gomme"),
            ("T", "text",        "Texte"),
        ]
        for icon, val, tip in tools:
            btn = ToolBtn(row, icon=icon, value=val,
                          tool_var=self.tool_var,
                          on_change=self._on_tool_change)
            btn.pack(side=tk.LEFT, padx=2)
            Tooltip(btn, tip)

        self._vsep(row)

        # Swatch couleur
        self._swatch = tk.Canvas(row, width=26, height=26, bg=CARD,
                                  highlightthickness=2,
                                  highlightbackground=DIM, cursor="hand2")
        self._swatch.pack(side=tk.LEFT, padx=(0, 4))
        self._draw_swatch()
        self._swatch.bind("<Button-1>", lambda _: self._choose_color())
        self._swatch.bind("<Enter>",
            lambda _: self._swatch.config(highlightbackground=ACCENT))
        self._swatch.bind("<Leave>",
            lambda _: self._swatch.config(highlightbackground=DIM))
        Tooltip(self._swatch, "Couleur")

        self._vsep(row)

        # Épaisseur
        ctk.CTkLabel(row, text="px", font=F_SMALL,
                     text_color=MUTED).pack(side=tk.LEFT, padx=(0, 4))
        ctk.CTkSlider(
            row, from_=1, to=20, variable=self.width_var,
            width=90, height=14,
            fg_color=DIM, progress_color=ACCENT,
            button_color=ACCENT, button_hover_color=A_HOVER,
        ).pack(side=tk.LEFT)
        self._wlbl = ctk.CTkLabel(row, text="2", font=F_SMALL,
                                   text_color=MUTED, width=20)
        self._wlbl.pack(side=tk.LEFT, padx=(4, 0))
        self.width_var.trace_add(
            "write",
            lambda *_: self._wlbl.configure(text=str(self.width_var.get())),
        )

        self._vsep(row)

        # Annuler / Rétablir
        for icon, tip, cmd in [("↩", "Annuler  Ctrl+Z", self.undo),
                                ("↪", "Rétablir Ctrl+Y", self.redo)]:
            b = ctk.CTkButton(
                row, text=icon, width=34, height=30, corner_radius=9,
                fg_color="transparent", border_width=1,
                border_color=BORDER, text_color=MUTED,
                hover_color=CARD_H, font=F_BOLD, command=cmd,
            )
            b.pack(side=tk.LEFT, padx=2)
            Tooltip(b, tip)

    def _build_record_panel(self):
        card = ctk.CTkFrame(self.root, corner_radius=14, fg_color=CARD,
                            border_width=1, border_color=BORDER)
        card.pack(fill=tk.X, padx=14, pady=(0, 8))

        # ── Ligne 1 : titre + timer ───────────────────────────
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill=tk.X, padx=14, pady=(10, 4))
        ctk.CTkLabel(top, text="⏺  Enregistrement",
                     font=F_BOLD, text_color=TEXT).pack(side=tk.LEFT)
        self._timer_lbl = ctk.CTkLabel(
            top, text="00:00:00", font=F_BOLD, text_color=MUTED)
        self._timer_lbl.pack(side=tk.RIGHT)

        # ── Ligne 2 : écran + audio ───────────────────────────
        mon_row = ctk.CTkFrame(card, fg_color="transparent")
        mon_row.pack(fill=tk.X, padx=14, pady=(0, 4))

        mon_labels = [lbl for lbl, _ in self._monitors] or ["Aucun écran détecté"]
        self._add_param(mon_row, "Écran à enregistrer",
                        mon_labels, self._monitor_var, None, 260)

        self._add_param(mon_row, "Audio",
                        ["Aucun", "Microphone", "Son système"],
                        self._audio_var, None, 160)

        # ── Ligne 3 : paramètres vidéo ────────────────────────
        params = ctk.CTkFrame(card, fg_color="transparent")
        params.pack(fill=tk.X, padx=14, pady=(0, 4))

        self._add_param(params, "Résolution",
                        list(ScreenRecorder.RESOLUTIONS.keys()),
                        self._res_var, self._on_res_change, 170)

        self._add_param(params, "FPS",
                        ["30", "60"],
                        self._fps_var, self._on_fps_change, 80)

        self._add_param(params, "Codec",
                        list(ScreenRecorder.CODECS.keys()),
                        self._codec_var, None, 170)

        self._add_param(params, "Encodeur",
                        list(ScreenRecorder.ENCODERS.keys()),
                        self._enc_var, None, 170)

        # ── Ligne 4 : bitrate + pause + bouton ───────────────
        brow = ctk.CTkFrame(card, fg_color="transparent")
        brow.pack(fill=tk.X, padx=14, pady=(0, 10))

        ctk.CTkLabel(brow, text="Débit", font=F_SMALL,
                     text_color=MUTED).pack(side=tk.LEFT, padx=(0, 6))
        ctk.CTkSlider(
            brow, from_=1000, to=60000, variable=self._bitrate_var,
            width=180, height=14,
            fg_color=DIM, progress_color=PINK,
            button_color=PINK, button_hover_color="#FF8AB0",
        ).pack(side=tk.LEFT)
        self._br_lbl = ctk.CTkLabel(
            brow, text="12 000 kbps", font=F_SMALL,
            text_color=MUTED, width=100)
        self._br_lbl.pack(side=tk.LEFT, padx=6)
        self._bitrate_var.trace_add(
            "write",
            lambda *_: self._br_lbl.configure(
                text=f"{self._bitrate_var.get():,} kbps".replace(",", " ")),
        )
        ctk.CTkLabel(brow, text="VBR", font=F_SMALL,
                     text_color=GREEN).pack(side=tk.LEFT, padx=(4, 0))

        self._rec_btn = ctk.CTkButton(
            brow, text="⏺  Démarrer",
            width=148, height=32, corner_radius=16,
            fg_color=RED_REC, hover_color=RED_H,
            text_color="white", font=F_BOLD,
            command=self._toggle_recording,
        )
        self._rec_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self._pause_btn = ctk.CTkButton(
            brow, text="⏸  Pause",
            width=110, height=32, corner_radius=16,
            fg_color="transparent", border_width=1,
            border_color=BORDER, text_color=MUTED,
            hover_color=CARD_H, font=F_BOLD,
            state="disabled",
            command=self._toggle_pause,
        )
        self._pause_btn.pack(side=tk.RIGHT, padx=(0, 4))

    def _add_param(self, parent, label, values, var, cmd, width=150):
        grp = ctk.CTkFrame(parent, fg_color="transparent")
        grp.pack(side=tk.LEFT, padx=(0, 12))
        ctk.CTkLabel(grp, text=label, font=F_SMALL,
                     text_color=MUTED).pack(anchor=tk.W)
        ctk.CTkOptionMenu(
            grp, values=values, variable=var, width=width,
            height=26, corner_radius=10,
            fg_color=DIM, button_color=ACCENT,
            button_hover_color=A_HOVER,
            dropdown_fg_color=CARD,
            dropdown_hover_color=CARD_H,
            text_color=TEXT, font=F_SMALL,
            command=cmd if cmd else lambda _: None,
        ).pack()

    def _build_canvas(self):
        outer = ctk.CTkFrame(self.root, corner_radius=14, fg_color=CARD,
                             border_width=1, border_color=BORDER)
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 6))

        wrap = tk.Frame(outer, bg=SURFACE)
        wrap.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        hbar = tk.Scrollbar(wrap, orient=tk.HORIZONTAL,
                             bg=DIM, troughcolor=SURFACE,
                             activebackground=ACCENT, width=10)
        vbar = tk.Scrollbar(wrap, orient=tk.VERTICAL,
                             bg=DIM, troughcolor=SURFACE,
                             activebackground=ACCENT, width=10)

        self.canvas = tk.Canvas(wrap, bg=SURFACE, cursor="crosshair",
                                 highlightthickness=0,
                                 xscrollcommand=hbar.set,
                                 yscrollcommand=vbar.set)
        hbar.config(command=self.canvas.xview)
        vbar.config(command=self.canvas.yview)

        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT,  fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._draw_welcome()
        self.canvas.bind("<ButtonPress-1>",   self._on_canvas_press)
        self.canvas.bind("<B1-Motion>",       self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Configure>",       self._on_canvas_resize)

    def _draw_welcome(self):
        self.canvas.delete("welcome")
        w = max(self.canvas.winfo_width(),  880)
        h = max(self.canvas.winfo_height(), 300)
        cx, cy = w // 2, h // 2
        px, py = 110, 48
        self.canvas.create_rectangle(
            cx - px, cy - py, cx + px, cy + py,
            outline=BORDER, width=1, dash=(6, 4), fill="", tags="welcome")
        self.canvas.create_text(cx, cy - 12, text="📷",
            font=("Segoe UI", 22), fill=MUTED, tags="welcome")
        self.canvas.create_text(cx, cy + 12, text="Nouvelle capture",
            font=("Segoe UI", 12, "bold"), fill=MUTED, tags="welcome")
        self.canvas.create_text(cx, cy + 30, text="Ctrl + N",
            font=("Segoe UI", 9), fill=DIM, tags="welcome")

    def _on_canvas_resize(self, _):
        if self.captured_image is None:
            self._draw_welcome()

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self.root, fg_color=SURFACE,
                           corner_radius=0, height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self._dot = ctk.CTkLabel(bar, text="●", font=F_SMALL,
                                  text_color=GREEN, width=18)
        self._dot.pack(side=tk.LEFT, padx=(14, 0))
        self.status_var = tk.StringVar(value="Prêt")
        ctk.CTkLabel(bar, textvariable=self.status_var,
                     font=F_SMALL, text_color=MUTED,
                     anchor=tk.W).pack(side=tk.LEFT, padx=4)
        self._dimlbl = ctk.CTkLabel(bar, text="", font=F_SMALL,
                                     text_color=DIM, anchor=tk.E)
        self._dimlbl.pack(side=tk.RIGHT, padx=14)

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda _: self.new_capture())
        self.root.bind("<Control-s>", lambda _: self.save_image())
        self.root.bind("<Control-c>", lambda _: self.copy_to_clipboard())
        self.root.bind("<Control-z>", lambda _: self.undo())
        self.root.bind("<Control-y>", lambda _: self.redo())

    def _vsep(self, parent):
        ctk.CTkFrame(parent, width=1, fg_color=BORDER).pack(
            side=tk.LEFT, fill=tk.Y, padx=10, pady=4)

    # ── Capture ───────────────────────────────────────────────

    def new_capture(self):
        self.root.withdraw()
        self.root.after(150, lambda: SelectionOverlay(
            on_done=self._on_done,
            on_cancel=self._on_cancel,
        ))

    def _on_done(self, rect):
        self.root.deiconify()
        self.root.after(100, lambda: self._capture_rect(rect))

    def _on_cancel(self):
        self.root.deiconify()
        self.status_var.set("Capture annulée")

    def _capture_rect(self, rect):
        x1, y1, x2, y2 = rect
        with mss.mss() as sct:
            shot = sct.grab({"top": y1, "left": x1,
                              "width": x2 - x1, "height": y2 - y1})
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        self._set_captured(img)

    # ── Affichage ─────────────────────────────────────────────

    def _set_captured(self, img):
        self.captured_image = img
        self.undo_stack     = [img.copy()]
        self.redo_stack.clear()
        self.canvas.delete("welcome")
        self._refresh_canvas()
        self._dimlbl.configure(text=f"{img.width} × {img.height} px")
        self.status_var.set("Capture réussie  —  Annotez avec les outils.")

    def _refresh_canvas(self):
        if self.captured_image is None:
            return
        img = self.captured_image.copy()
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (12, 12, 24))
            bg.paste(img, mask=img.split()[3])
            img = bg
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.delete("img")
        self.canvas.create_image(0, 0, anchor=tk.NW,
                                  image=self.photo_image, tags="img")
        self.canvas.tag_lower("img")
        self.canvas.config(scrollregion=(0, 0, img.width, img.height))

    # ── Annotations ───────────────────────────────────────────

    def _on_tool_change(self):
        self.canvas.config(
            cursor=self.CURSOR_FOR_TOOL.get(self.tool_var.get(), "crosshair"))

    def _draw_swatch(self):
        self._swatch.delete("all")
        self._swatch.create_oval(3, 3, 23, 23,
                                  fill=self.pen_color, outline="")

    def _choose_color(self):
        color = colorchooser.askcolor(
            color=self.pen_color, title="Couleur — WinScreen")[1]
        if color:
            self.pen_color = color
            self._draw_swatch()

    def _on_canvas_press(self, e):
        if self.captured_image is None:
            return
        self.drawing = True
        self.last_x  = self.canvas.canvasx(e.x)
        self.last_y  = self.canvas.canvasy(e.y)
        if self.tool_var.get() == "text":
            self.drawing = False
            self._add_text(self.last_x, self.last_y)

    def _on_canvas_drag(self, e):
        if not self.drawing or self.captured_image is None:
            return
        cx = self.canvas.canvasx(e.x)
        cy = self.canvas.canvasy(e.y)
        tool = self.tool_var.get()
        w    = self.width_var.get()
        x1, y1 = int(self.last_x), int(self.last_y)
        x2, y2 = int(cx), int(cy)

        if tool == "pen":
            self.canvas.create_line(
                self.last_x, self.last_y, cx, cy,
                fill=self.pen_color, width=w,
                smooth=True, capstyle=tk.ROUND)
            ImageDraw.Draw(self._ensure_rgb()).line(
                [(x1, y1), (x2, y2)], fill=self.pen_color, width=w)

        elif tool == "highlighter":
            hw = w * 6
            self.canvas.create_line(
                self.last_x, self.last_y, cx, cy,
                fill=self.pen_color, width=hw,
                stipple="gray50", smooth=True, capstyle=tk.ROUND)
            if self.captured_image.mode != "RGBA":
                self.captured_image = self.captured_image.convert("RGBA")
            ov = Image.new("RGBA", self.captured_image.size, (0, 0, 0, 0))
            r = int(self.pen_color[1:3], 16)
            g = int(self.pen_color[3:5], 16)
            b = int(self.pen_color[5:7], 16)
            ImageDraw.Draw(ov).line(
                [(x1, y1), (x2, y2)], fill=(r, g, b, 90), width=hw)
            self.captured_image = Image.alpha_composite(
                self.captured_image, ov)

        elif tool == "eraser":
            ew = w * 6
            self.canvas.create_rectangle(
                self.last_x - ew, self.last_y - ew,
                cx + ew, cy + ew, fill=SURFACE, outline="")
            bg_rgb = tuple(int(SURFACE[i:i+2], 16) for i in (1, 3, 5))
            ImageDraw.Draw(self._ensure_rgb()).rectangle(
                [x1 - ew, y1 - ew, x2 + ew, y2 + ew], fill=bg_rgb)

        self.last_x, self.last_y = cx, cy

    def _on_canvas_release(self, _):
        if not self.drawing or self.captured_image is None:
            return
        self.drawing = False
        self._push_undo()
        if self.tool_var.get() == "eraser":
            self._refresh_canvas()

    def _ensure_rgb(self):
        if self.captured_image.mode != "RGB":
            self.captured_image = self.captured_image.convert("RGB")
        return self.captured_image

    def _push_undo(self):
        self.undo_stack.append(self.captured_image.copy())
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _add_text(self, x, y):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Texte — WinScreen")
        dlg.geometry("340x190")
        dlg.resizable(False, False)
        dlg.configure(fg_color=SURFACE)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Texte", font=F_BOLD,
                     text_color=MUTED).pack(padx=20, pady=(16, 4), anchor=tk.W)
        tv    = tk.StringVar()
        entry = ctk.CTkEntry(dlg, textvariable=tv, width=300, height=34,
                              corner_radius=10, fg_color=CARD,
                              border_color=BORDER, text_color=TEXT, font=F_LABEL)
        entry.pack(padx=20, pady=4)
        entry.focus()

        row = ctk.CTkFrame(dlg, fg_color="transparent")
        row.pack(padx=20, pady=6, fill=tk.X)
        ctk.CTkLabel(row, text="Taille :", font=F_SMALL,
                     text_color=MUTED).pack(side=tk.LEFT)
        sv  = tk.IntVar(value=18)
        sl  = ctk.CTkSlider(row, from_=8, to=72, variable=sv, width=150,
                             fg_color=DIM, progress_color=ACCENT,
                             button_color=ACCENT, button_hover_color=A_HOVER)
        sl.pack(side=tk.LEFT, padx=8)
        szl = ctk.CTkLabel(row, text="18 px", font=F_SMALL,
                            text_color=MUTED, width=40)
        szl.pack(side=tk.LEFT)
        sv.trace_add("write", lambda *_: szl.configure(text=f"{sv.get()} px"))

        br = ctk.CTkFrame(dlg, fg_color="transparent")
        br.pack(pady=10)

        def confirm():
            txt = tv.get().strip()
            if txt:
                self.canvas.create_text(
                    x, y, text=txt, fill=self.pen_color,
                    font=("Segoe UI", sv.get()), anchor=tk.NW)
                draw = ImageDraw.Draw(self._ensure_rgb())
                try:
                    font = ImageFont.truetype("arial.ttf", sv.get())
                except Exception:
                    font = ImageFont.load_default()
                draw.text((int(x), int(y)), txt,
                           fill=self.pen_color, font=font)
                self._push_undo()
            dlg.destroy()

        ctk.CTkButton(br, text="Valider", width=120, height=32,
                       corner_radius=16, fg_color=ACCENT,
                       hover_color=A_HOVER, text_color="white",
                       font=F_BOLD, command=confirm).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(br, text="Annuler", width=100, height=32,
                       corner_radius=16, fg_color="transparent",
                       border_width=1, border_color=BORDER,
                       text_color=MUTED, hover_color=CARD_H,
                       font=F_BOLD, command=dlg.destroy).pack(
            side=tk.LEFT, padx=6)
        dlg.bind("<Return>", lambda _: confirm())
        dlg.bind("<Escape>", lambda _: dlg.destroy())

    # ── Undo / Redo ───────────────────────────────────────────

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.captured_image = self.undo_stack[-1].copy()
            self._refresh_canvas()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.captured_image = state.copy()
            self._refresh_canvas()

    # ── Enregistrement ────────────────────────────────────────

    def _on_res_change(self, res):
        fps = self._fps_var.get()
        preset = ScreenRecorder.BITRATE_DEFAULTS.get(res, {})
        if fps in preset:
            self._bitrate_var.set(preset[fps])

    def _on_fps_change(self, fps):
        res = self._res_var.get()
        preset = ScreenRecorder.BITRATE_DEFAULTS.get(res, {})
        if fps in preset:
            self._bitrate_var.set(preset[fps])

    def _toggle_recording(self):
        if not self.recorder.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        if not ScreenRecorder.ffmpeg_available():
            messagebox.showerror(
                "WinScreen — FFmpeg introuvable",
                "FFmpeg n'est pas installé ou absent du PATH.\n\n"
                "Téléchargez FFmpeg sur  ffmpeg.org\n"
                "puis ajoutez-le au PATH système.",
            )
            return

        # Résoudre le moniteur sélectionné
        sel_label = self._monitor_var.get()
        monitor   = next(
            (m for lbl, m in self._monitors if lbl == sel_label),
            self._monitors[0][1] if self._monitors else None,
        )
        if monitor is None:
            messagebox.showerror("WinScreen", "Aucun écran détecté.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4"), ("MKV", "*.mkv"),
                       ("Tous", "*.*")],
            title="Enregistrer la vidéo — WinScreen",
        )
        if not path:
            return

        self._rec_btn.configure(state="disabled")
        self._countdown(3, lambda: self._do_start(path, monitor))

    def _countdown(self, n: int, callback):
        """Affiche un compte à rebours plein écran puis appelle callback."""
        if n <= 0:
            callback()
            return
        ov = tk.Toplevel(self.root)
        ov.overrideredirect(True)
        ov.attributes("-topmost", True)
        ov.attributes("-alpha", 0.45)
        ov.config(bg="black")
        # Sur Windows, overrideredirect + -fullscreen est cassé :
        # on positionne manuellement sur tout l'écran virtuel
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ov.geometry(f"{sw}x{sh}+0+0")
        ov.update_idletasks()
        cv = tk.Canvas(ov, bg="black", highlightthickness=0,
                       width=sw, height=sh)
        cv.place(x=0, y=0)
        cv.create_text(sw // 2, sh // 2, text=str(n),
                       fill="white", font=("Segoe UI", 140, "bold"))
        cv.create_text(sw // 2, sh // 2 + 110,
                       text="Enregistrement dans…",
                       fill="#aaaacc", font=("Segoe UI", 18))
        self.root.after(1000, lambda: (ov.destroy(),
                                       self._countdown(n - 1, callback)))

    def _do_start(self, path: str, monitor: dict):
        self.status_var.set("Initialisation de l'encodeur…")
        self._dot.configure(text_color=PINK)

        def on_error(e):
            messagebox.showerror("WinScreen", f"Erreur FFmpeg :\n{e}")
            self._rec_btn.configure(
                text="⏺  Démarrer", fg_color=RED_REC,
                hover_color=RED_H, state="normal")
            self._pause_btn.configure(state="disabled")

        ok = self.recorder.start(
            output_path=path,
            res_label=self._res_var.get(),
            fps=int(self._fps_var.get()),
            codec_name=self._codec_var.get(),
            bitrate=self._bitrate_var.get(),
            encoder_label=self._enc_var.get(),
            monitor=monitor,
            audio_mode=self._audio_var.get(),
            on_error=on_error,
        )
        if ok:
            self._rec_btn.configure(
                text="⏹  Arrêter",
                fg_color="#333348", hover_color=CARD_H,
                state="normal")
            self._pause_btn.configure(state="normal")
            self.status_var.set("⏺  Enregistrement en cours…")
            self._dot.configure(text_color=RED_REC)
            self._update_timer()
            # Vérifier que ffmpeg est toujours vivant après 1,5 s
            self.root.after(1500, self._check_recording_alive)

    def _check_recording_alive(self):
        """Vérifie que ffmpeg tourne encore 1,5 s après le démarrage."""
        if not self.recorder.recording:
            return
        proc = self.recorder._proc
        if proc and proc.poll() is not None:
            # Processus mort — récupérer les dernières lignes d'erreur
            self.recorder.recording = False
            self.recorder.paused    = False
            self._rec_btn.configure(
                text="⏺  Démarrer",
                fg_color=RED_REC, hover_color=RED_H, state="normal")
            self._pause_btn.configure(state="disabled")
            self._timer_lbl.configure(text="00:00:00")
            self._dot.configure(text_color=GREEN)
            self.status_var.set("Erreur — ffmpeg s'est arrêté.")
            lines = self.recorder._stderr_lines
            detail = "\n".join(lines[-15:]) if lines else "(aucun détail)"
            messagebox.showerror(
                "WinScreen — Erreur ffmpeg",
                f"ffmpeg s'est arrêté immédiatement.\n\n{detail}")

    def _stop_recording(self):
        self.status_var.set("Finalisation…")
        self.recorder.stop()
        self._rec_btn.configure(
            text="⏺  Démarrer",
            fg_color=RED_REC, hover_color=RED_H, state="normal")
        self._pause_btn.configure(
            text="⏸  Pause", state="disabled",
            fg_color="transparent", text_color=MUTED)
        self._timer_lbl.configure(text="00:00:00")
        self._dot.configure(text_color=GREEN)
        self.status_var.set("Enregistrement terminé.")

    def _toggle_pause(self):
        if self.recorder.paused:
            self.recorder.resume()
            self._pause_btn.configure(
                text="⏸  Pause",
                fg_color="transparent", text_color=MUTED)
            self._dot.configure(text_color=RED_REC)
            self.status_var.set("⏺  Enregistrement en cours…")
        else:
            self.recorder.pause()
            self._pause_btn.configure(
                text="▶  Reprendre",
                fg_color=ACCENT, text_color="white")
            self._dot.configure(text_color=MUTED)
            self.status_var.set("⏸  Enregistrement en pause.")

    def _update_timer(self):
        if self.recorder.recording:
            self._timer_lbl.configure(text=self.recorder.elapsed())
            self.root.after(1000, self._update_timer)

    # ── Enregistrer image / Copier ────────────────────────────

    def save_image(self):
        if self.captured_image is None:
            messagebox.showinfo("WinScreen", "Aucune capture à enregistrer.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"),
                       ("GIF", "*.gif"), ("Tous", "*.*")],
            title="Enregistrer — WinScreen",
        )
        if not path:
            return
        img = self.captured_image
        if img.mode == "RGBA" and path.lower().endswith((".jpg", ".jpeg")):
            bg = Image.new("RGB", img.size, "white")
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.save(path)
        self.status_var.set(f"Enregistré  →  {path}")

    def copy_to_clipboard(self):
        if self.captured_image is None:
            return
        try:
            import win32clipboard
            img = self.captured_image
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, "white")
                bg.paste(img, mask=img.split()[3])
                img = bg
            buf = io.BytesIO()
            img.convert("RGB").save(buf, "BMP")
            data = buf.getvalue()[14:]
            buf.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            self.status_var.set("Image copiée dans le presse-papiers.")
        except Exception as ex:
            messagebox.showerror("WinScreen", f"Impossible de copier :\n{ex}")


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    WinScreen()
