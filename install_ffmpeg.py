"""
Télécharge et installe ffmpeg.exe dans le dossier WinScreen.
Source : gyan.dev (build officielle Windows statique)
"""
import urllib.request
import zipfile
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading

URL        = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_EXE = os.path.join(SCRIPT_DIR, "ffmpeg.exe")
ZIP_TMP    = os.path.join(SCRIPT_DIR, "_ffmpeg_tmp.zip")

# ── Palette ───────────────────────────────────────────────────
BG     = "#07070E"
CARD   = "#10101C"
ACCENT = "#7C6FFF"
GREEN  = "#00FF88"
TEXT   = "#E8E8FF"
MUTED  = "#4A4A72"
BORDER = "#1A1A2E"


class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WinScreen — Installation FFmpeg")
        self.root.geometry("460x210")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.eval("tk::PlaceWindow . center")

        # ── Titre ─────────────────────────────────────────────
        tk.Label(self.root, text="◈  WinScreen",
                 bg=BG, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(18, 2))
        tk.Label(self.root, text="Installation de FFmpeg",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack()

        # ── Statut ────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Vérification…")
        tk.Label(self.root, textvariable=self.status_var,
                 bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(pady=(12, 4))

        # ── Barre de progression ──────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("W.Horizontal.TProgressbar",
                         troughcolor=CARD, background=ACCENT,
                         bordercolor=BORDER, lightcolor=ACCENT,
                         darkcolor=ACCENT)
        self.progress = ttk.Progressbar(
            self.root, length=400, mode="determinate",
            style="W.Horizontal.TProgressbar")
        self.progress.pack()

        # ── Taille ────────────────────────────────────────────
        self.size_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.size_var,
                 bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(pady=4)

        threading.Thread(target=self._run, daemon=True).start()
        self.root.mainloop()

    # ─────────────────────────────────────────────────────────

    def _status(self, txt):
        self.root.after(0, lambda: self.status_var.set(txt))

    def _set_progress(self, pct, done_mb=None, total_mb=None):
        def _up():
            self.progress.configure(value=pct)
            if done_mb is not None:
                self.size_var.set(f"{done_mb:.1f} Mo / {total_mb:.1f} Mo")
        self.root.after(0, _up)

    def _run(self):
        if os.path.exists(FFMPEG_EXE):
            self._status("✓  FFmpeg est déjà installé !")
            self._set_progress(100)
            self.root.after(1800, self.root.quit)
            return

        try:
            # ── Téléchargement ────────────────────────────────
            self._status("Téléchargement de FFmpeg  (~75 Mo)…")

            def hook(count, block, total):
                if total > 0:
                    pct  = min(int(count * block * 100 / total), 99)
                    done = count * block / 1_048_576
                    tot  = total / 1_048_576
                    self._set_progress(pct, done, tot)

            urllib.request.urlretrieve(URL, ZIP_TMP, reporthook=hook)
            self._set_progress(99)

            # ── Extraction ────────────────────────────────────
            self._status("Extraction de ffmpeg.exe…")
            self.size_var.set("")
            found = False
            with zipfile.ZipFile(ZIP_TMP, "r") as z:
                for name in z.namelist():
                    if name.endswith("ffmpeg.exe") and "/bin/" in name:
                        data = z.read(name)
                        with open(FFMPEG_EXE, "wb") as f:
                            f.write(data)
                        found = True
                        break

            if os.path.exists(ZIP_TMP):
                os.remove(ZIP_TMP)

            if found:
                self._set_progress(100)
                self._status("✓  FFmpeg installé !  Vous pouvez fermer cette fenêtre.")
                self.root.after(2500, self.root.quit)
            else:
                raise RuntimeError(
                    "ffmpeg.exe introuvable dans l'archive.")

        except Exception as exc:
            if os.path.exists(ZIP_TMP):
                os.remove(ZIP_TMP)
            self.root.after(0, lambda: messagebox.showerror(
                "Erreur d'installation",
                f"Impossible d'installer FFmpeg :\n\n{exc}\n\n"
                "Téléchargez-le manuellement sur  ffmpeg.org\n"
                f"et placez  ffmpeg.exe  dans :\n{SCRIPT_DIR}",
            ))
            self.root.after(0, self.root.quit)


if __name__ == "__main__":
    Installer()
