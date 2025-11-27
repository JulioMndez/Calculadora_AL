import tkinter as tk

# Centralized style variables to keep visual consistency across modules
BG_COLOR = "#2E2E2E"
BUTTON_COLOR = "#505050"
ACCENT_COLOR = "#D32F2F"
TEXT_COLOR = "#FFFFFF"
BUTTON_HOVER_COLOR = "#6a6a6a"

FONT_FAMILY = "Arial"
TITLE_FONT = (FONT_FAMILY, 16, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 11)
BUTTON_FONT = (FONT_FAMILY, 11, "bold")
MONO_FONT = (FONT_FAMILY, 10)

def style_tk_button(btn, hover=True):
    try:
        btn.config(bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=ACCENT_COLOR, activeforeground=TEXT_COLOR, font=BUTTON_FONT, relief="flat")
        if hover:
            btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_HOVER_COLOR))
            btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_COLOR))
    except Exception:
        pass

def style_label(lbl, title=False):
    try:
        lbl.config(bg=BG_COLOR, fg=TEXT_COLOR)
        if title:
            lbl.config(font=TITLE_FONT)
        else:
            lbl.config(font=SUBTITLE_FONT)
    except Exception:
        pass

def style_text(txt):
    try:
        txt.config(bg="#1E1E1E", fg=TEXT_COLOR, font=MONO_FONT, insertbackground=TEXT_COLOR)
    except Exception:
        pass
