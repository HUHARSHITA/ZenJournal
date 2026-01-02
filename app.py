import customtkinter as ctk
from datetime import datetime
import json
import os
from PIL import Image
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CRITICAL FIX FOR PERSISTENCE ---
# Store data in the user's home directory so it's not deleted with temp files
DATA_DIR = os.path.join(os.path.expanduser("~"), "ZenJournalApp")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

STORAGE_FILE = os.path.join(DATA_DIR, "ZenJournal_Data.json")

# --- Premium Color Palettes ---
THEMES = [
    {   # Midnight Lavender
        "name": "Lavender Dream",
        "bg": "#D1D5F0", "card": "#1A2238", "card_sec": "#252D47", 
        "accent": "#FFD1DC", "text": "#FFFFFF", "dim": "#8A95B2"
    },
    {   # Yellow Theme
        "name": "Sunny Sunstone",
        "bg": "#FEF9C3", "card": "#451A03", "card_sec": "#78350F", 
        "accent": "#FACC15", "text": "#FFFFFF", "dim": "#a16207"
    },
    {   # Sunset Rose
        "name": "Sunset Rose",
        "bg": "#FAD0C4", "card": "#3E232F", "card_sec": "#5D3748", 
        "accent": "#FF9A9E", "text": "#FFFFFF", "dim": "#A08794"
    },
    {   # Matcha Theme 
        "name": "Matcha Moss",
        "bg": "#DCFCE7", "card": "#064e3b", "card_sec": "#065f46", 
        "accent": "#4ade80", "text": "#FFFFFF", "dim": "#7dccb6"
    }
]

STORAGE_FILE = resource_path("ZenJournal.json")

class ZenJournal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zen Journal")
        self.geometry("600x750")
        
        # Load Data
        stored_data = self.load_all_data()
        self.journal_entries = stored_data.get("entries", {})
        self.theme_index = stored_data.get("theme_preference", 0)
        
        # Logo Logic - Use resource_path for the bundled image
        self.logo = None
        logo_path = resource_path("logo.png") 
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            self.logo = ctk.CTkImage(light_image=img, dark_image=img, size=(70, 70))

        self.setup_ui()

    def setup_ui(self):
        current = THEMES[self.theme_index]
        self.configure(fg_color=current["bg"])

        self.main_card = ctk.CTkFrame(self, corner_radius=40, fg_color=current["card"])
        self.main_card.place(relx=0.5, rely=0.5, relwidth=0.88, relheight=0.88, anchor="center")
        self.main_card.grid_columnconfigure(0, weight=1)
        self.main_card.grid_rowconfigure(0, weight=1)

        self.vibe_btn = ctk.CTkButton(self, text=f"✧ Vibe: {current['name']}", command=self.cycle_theme,
                                      fg_color="transparent", text_color=current["card"],
                                      hover=False, font=("Georgia", 13, "italic"))
        self.vibe_btn.place(relx=0.98, rely=0.02, anchor="ne")

        self.frames = {}
        for F in (JournalView, HistoryView):
            self.frames[F] = F(parent=self.main_card, controller=self)
            self.frames[F].grid(row=0, column=0, sticky="nsew")

        self.show_frame(JournalView)

    def cycle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.apply_theme()
        self.save_all_data() # Save preference immediately

    def apply_theme(self):
        current = THEMES[self.theme_index]
        self.configure(fg_color=current["bg"])
        self.vibe_btn.configure(text=f"✧ Vibe: {current['name']}", text_color=current["card"])
        self.main_card.configure(fg_color=current["card"])
        for frame in self.frames.values():
            frame.update_colors(current)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()
        frame.on_show()

    def load_all_data(self):
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        return {"entries": {}, "theme_preference": 0}

    def save_all_data(self):
        data_to_save = {
            "entries": self.journal_entries,
            "theme_preference": self.theme_index
        }
        # Writing to the persistent home directory path
        with open(STORAGE_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)

class JournalView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

# Logo Display
        self.logo_label = ctk.CTkLabel(self, text="", image=self.controller.logo)
        self.logo_label.grid(row=0, column=0, pady=(30, 0))
        
        self.date_lbl = ctk.CTkLabel(self, text="", font=("Georgia", 14, "italic"))
        self.date_lbl.grid(row=0, column=0, pady=(35, 5))

        self.header = ctk.CTkLabel(self, text="How was the Day?!", font=("Georgia", 34, "bold"))
        self.header.grid(row=1, column=0, pady=5)

        self.input_area = ctk.CTkFrame(self, corner_radius=30)
        self.input_area.grid(row=2, column=0, padx=35, pady=20, sticky="nsew")
        self.input_area.grid_columnconfigure(0, weight=1)
        self.input_area.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.input_area, fg_color="transparent", text_color="#E0E0E0", 
                                      font=("Georgia", 18), spacing3=15, wrap="word")
        self.textbox.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")

        self.status_msg = ctk.CTkLabel(self, text="", font=("Verdana", 11, "bold"))
        self.status_msg.grid(row=3, column=0, pady=5)

        self.btn_row = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_row.grid(row=4, column=0, pady=25)

        self.save_btn = ctk.CTkButton(self.btn_row, text="Save", command=self.save_action, 
                                     fg_color="white", corner_radius=100, font=("Georgia", 19, "bold"), height=55, width=140)
        self.save_btn.grid(row=0, column=0, padx=12)

        self.edit_btn = ctk.CTkButton(self.btn_row, text="Edit", command=self.edit_action, 
                                     fg_color="white", corner_radius=100, font=("Georgia", 19, "bold"), height=55, width=140)
        self.edit_btn.grid(row=0, column=1, padx=12)

        self.hist_link = ctk.CTkButton(self, text="View Previous Messages!", fg_color="transparent", hover=False, 
                                       font=("Verdana", 11, "underline"), command=lambda: controller.show_frame(HistoryView))
        self.hist_link.grid(row=5, column=0, pady=(0, 40))
        
        self.update_colors(THEMES[controller.theme_index])

    def update_colors(self, theme):
        self.date_lbl.configure(text_color=theme["dim"])
        self.header.configure(text_color=theme["text"])
        self.input_area.configure(fg_color=theme["card_sec"])
        self.status_msg.configure(text_color=theme["accent"])
        self.save_btn.configure(text_color=theme["card"])
        self.edit_btn.configure(text_color=theme["card"])
        self.hist_link.configure(text_color=theme["dim"])

    def on_show(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_lbl.configure(text=datetime.now().strftime("%A %d, %Y"))
        if today in self.controller.journal_entries:
            entry = self.controller.journal_entries[today]
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", entry["content"])
            self.textbox.configure(state="disabled")
            self.status_msg.configure(text=f"Saved at {entry['time']} ✨")
        else:
            self.textbox.configure(state="normal")
            self.status_msg.configure(text="A clean slate for today...")

    def save_action(self):
        content = self.textbox.get("1.0", "end-1c").strip()
        if content:
            today = datetime.now().strftime("%Y-%m-%d")
            self.controller.journal_entries[today] = {
                "content": content, "time": datetime.now().strftime("%I:%M %p"),
                "full_date": datetime.now().strftime("%A %d, %Y")
            }
            self.controller.save_all_data()
            self.on_show()

    def edit_action(self):
        self.textbox.configure(state="normal")
        self.textbox.focus()

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text="Past Memories", font=("Georgia", 32, "bold"))
        self.title_lbl.grid(row=0, column=0, pady=40)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=25)

        self.back_btn = ctk.CTkButton(self, text="Back to Today", command=lambda: controller.show_frame(JournalView),
                                     fg_color="white", corner_radius=100, font=("Georgia", 18, "bold"), height=50, width=160)
        self.back_btn.grid(row=2, column=0, pady=30)
        
        self.update_colors(THEMES[controller.theme_index])

    def update_colors(self, theme):
        self.title_lbl.configure(text_color=theme["text"])
        self.back_btn.configure(text_color=theme["card"])
        # FORCE THE CARDS TO REPAINT
        self.on_show()

    def on_show(self):
        for w in self.scroll.winfo_children(): w.destroy()
        data = self.controller.journal_entries
        current = THEMES[self.controller.theme_index]
        
        for k in sorted(data.keys(), reverse=True):
            card = ctk.CTkFrame(self.scroll, fg_color=current["card_sec"], corner_radius=0)
            card.pack(fill="x", pady=12, padx=10)
            
            header = f"{data[k]['full_date']}  •  {data[k]['time']}"
            ctk.CTkLabel(card, text=header, font=("Georgia", 13, "bold"), text_color=current["accent"]).pack(anchor="nw", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=data[k]['content'], font=("Georgia", 16), text_color="#CFD8DC", wraplength=400, justify="left").pack(anchor="nw", padx=20, pady=(0, 15))

if __name__ == "__main__":
    app = ZenJournal()
    app.mainloop()