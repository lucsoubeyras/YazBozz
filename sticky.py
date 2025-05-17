import tkinter as tk
from tkinter import colorchooser, Menu, scrolledtext
import uuid
import json
import os
from tkinter.font import Font

class YazBozzNote:
    def __init__(self, master, note_manager, note_id=None, title="YazBozz Not", text="", color="#FFD166", position=None, size=(320, 320)):
        self.master = master
        self.note_manager = note_manager
        self.id = note_id if note_id else str(uuid.uuid4())
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.note_id = self.id
        
        # YazBozz renk teması
        self.bg_color = color
        self.header_color = self._adjust_color(color, -0.1)
        self.text_color = "#2D3047"
        self.border_color = self._adjust_color(color, -0.2)
        
        # Pencerenin başlangıç pozisyonu
        width, height = size
        x = position[0] if position else master.winfo_x() + 60
        y = position[1] if position else master.winfo_y() + 60
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # YazBozz özel pencere özellikleri
        self.window.configure(bg=self.bg_color)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Ana çerçeve
        self.main_frame = tk.Frame(self.window, bg=self.bg_color, bd=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Başlık çubuğu
        self.header = tk.Frame(self.main_frame, bg=self.header_color, height=36)
        self.header.pack(fill=tk.X)
        
        # Başlık
        self.title_var = tk.StringVar(value=title)
        self.title_label = tk.Label(self.header, textvariable=self.title_var, 
                                  bg=self.header_color, fg=self.text_color,
                                  font=("Verdana", 10, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        self.title_label.bind("<Double-Button-1>", self._edit_title)
        
        # Kapat butonu
        self.close_btn = tk.Label(self.header, text="✕", fg=self.text_color, 
                                font=("Verdana", 12), bg=self.header_color,
                                cursor="hand2")
        self.close_btn.pack(side=tk.RIGHT, padx=10)
        self.close_btn.bind("<Button-1>", lambda e: self._close())
        
        # İçerik alanı
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD,
                                                 font=("Verdana", 10),
                                                 bg=self.bg_color, fg=self.text_color,
                                                 insertbackground=self.text_color,
                                                 selectbackground="#06D6A0",
                                                 padx=15, pady=15, bd=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar'ı gizle
        self.text_area.vbar.pack_forget()
        
        # Varsayılan metin
        if text:
            self.text_area.insert(tk.END, text)
        
        # Boyutlandırma çerçevesi
        self._setup_resize_border()
        
        # Fare olayları
        self._setup_events()
        
        # Bağlam menüsü
        self._create_context_menu()
        
        # İlk kayıt
        self._save()

    def _setup_resize_border(self):
        """YazBozz boyutlandırma çerçevesi"""
        self.resize_border = tk.Frame(self.main_frame, bg=self.border_color, width=12, height=12)
        self.resize_border.place(relx=1.0, rely=1.0, anchor="se")
        self.resize_border.bind("<B1-Motion>", self._resize)
        self.resize_border.bind("<Button-1>", lambda e: self.window.focus_force())

    def _setup_events(self):
        """Fare olaylarını bağla"""
        self.header.bind("<Button-1>", self._start_move)
        self.header.bind("<B1-Motion>", self._on_move)
        self.title_label.bind("<Button-1>", self._start_move)
        self.title_label.bind("<B1-Motion>", self._on_move)

    def _create_context_menu(self):
        """YazBozz bağlam menüsü"""
        self.context_menu = Menu(self.window, tearoff=0, font=("Verdana", 9))
        
        # Renk seçenekleri
        color_menu = Menu(self.context_menu, tearoff=0)
        colors = [
            ("Sarı", "#FFD166"), ("Mavi", "#118AB2"),
            ("Yeşil", "#06D6A0"), ("Pembe", "#EF476F"),
            ("Mor", "#7209B7"), ("Açık Mavi", "#8ECAE6")
        ]
        for name, color in colors:
            color_menu.add_command(label=name, command=lambda c=color: self._change_color(c))
        
        self.context_menu.add_cascade(label="Renk Değiştir", menu=color_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Sil", command=self._close)
        
        self.text_area.bind("<Button-3>", self._show_menu)
        self.header.bind("<Button-3>", self._show_menu)

    def _edit_title(self, event):
        """Başlığı düzenle"""
        self.title_entry = tk.Entry(self.header, textvariable=self.title_var,
                                  font=("Verdana", 10), bd=0,
                                  bg="#FFFFFF", fg=self.text_color)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.title_entry.focus()
        self.title_entry.bind("<Return>", self._save_title)
        self.title_entry.bind("<FocusOut>", self._save_title)

    def _save_title(self, event):
        """Başlığı kaydet"""
        self.title_label.pack(side=tk.LEFT, padx=10)
        self.title_entry.destroy()
        self._save()

    def _start_move(self, event):
        """Taşıma başlangıcı"""
        self._start_x = event.x
        self._start_y = event.y

    def _on_move(self, event):
        """Pencereyi taşı"""
        x = self.window.winfo_x() + (event.x - self._start_x)
        y = self.window.winfo_y() + (event.y - self._start_y)
        self.window.geometry(f"+{x}+{y}")

    def _resize(self, event):
        """Pencereyi yeniden boyutlandır"""
        new_width = max(250, event.x_root - self.window.winfo_x())
        new_height = max(250, event.y_root - self.window.winfo_y())
        self.window.geometry(f"{new_width}x{new_height}")

    def _change_color(self, new_color):
        """Rengi değiştir"""
        self.bg_color = new_color
        self.header_color = self._adjust_color(new_color, -0.1)
        self.border_color = self._adjust_color(new_color, -0.2)
        
        self.window.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        self.header.configure(bg=self.header_color)
        self.title_label.configure(bg=self.header_color)
        self.close_btn.configure(bg=self.header_color)
        self.text_area.configure(bg=self.bg_color)
        self.resize_border.configure(bg=self.border_color)
        
        self._save()

    def _show_menu(self, event):
        """Bağlam menüsünü göster"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _close(self):
        """Notu kapat"""
        self._save()
        self.window.destroy()

    def _save(self):
        """Notu kaydet"""
        content = {
            "id": self.id,
            "title": self.title_var.get(),
            "text": self.text_area.get("1.0", tk.END).strip(),
            "color": self.bg_color,
            "position": (self.window.winfo_x(), self.window.winfo_y()),
            "size": (self.window.winfo_width(), self.window.winfo_height())
        }
        self.note_manager.save_note(content)

    def _adjust_color(self, hex_color, factor):
        """Rengi koyulaştır veya aç"""
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        new_rgb = [min(255, max(0, int(c + (c * factor)))) for c in rgb]
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"


class YazBozzManager:
    def __init__(self, app):
        self.app = app
        self.notes_file = "yazbozz_notes.json"
        self.notes = self._load_notes()

    def _load_notes(self):
        """Notları yükle"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_note(self, note_data):
        """Notu kaydet"""
        self.notes[note_data["id"]] = note_data
        self._save_to_file()
        self.app.update_list()

    def delete_note(self, note_id):
        """Notu sil"""
        if note_id in self.notes:
            del self.notes[note_id]
            self._save_to_file()
            self.app.update_list()

    def _save_to_file(self):
        """Notları dosyaya kaydet"""
        with open(self.notes_file, "w") as f:
            json.dump(self.notes, f, indent=2)


class YazBozzApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YazBozz - Akıllı Notlar")
        self.root.geometry("900x600")
        
        # YazBozz renk teması
        self.bg_color = "#F8F9FA"
        self.header_color = "#2D3047"
        self.text_color = "#2D3047"
        self.accent_color = "#06D6A0"
        
        self.root.configure(bg=self.bg_color)
        
        self.note_manager = YazBozzManager(self)
        
        # Arayüzü oluştur
        self._setup_ui()
        
        # Kayıtlı notları yükle
        self.update_list()

    def _setup_ui(self):
        """Arayüzü oluştur"""
        # Başlık çubuğu
        self.header = tk.Frame(self.root, bg=self.header_color, height=70)
        self.header.pack(fill=tk.X)
        
        # Logo ve başlık
        logo_frame = tk.Frame(self.header, bg=self.header_color)
        logo_frame.pack(side=tk.LEFT, padx=20)
        
        self.logo = tk.Label(logo_frame, text="YazBozz", 
                           font=("Verdana", 20, "bold"), 
                           fg="white", bg=self.header_color)
        self.logo.pack(side=tk.LEFT)
        
        # Yeni not butonu
        self.new_btn = tk.Button(self.header, text="+ Yeni YazBozz", 
                               font=("Verdana", 11), bg=self.accent_color,
                               fg="white", bd=0, command=self.new_note)
        self.new_btn.pack(side=tk.RIGHT, padx=20, ipady=5)
        
        # Ana içerik
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Liste başlığı
        tk.Label(self.main_frame, text="YazBozz Notlarım", 
                font=("Verdana", 14, "bold"), 
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        # Not listesi
        self.list_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Liste içeriği
        self.notes_list = tk.Frame(self.list_frame, bg=self.bg_color)
        self.notes_list.pack(fill=tk.BOTH, expand=True)
        
        # Yeni not butonu
        self.add_btn = tk.Button(self.notes_list, text="+ Yeni YazBozz Ekle", 
                               font=("Verdana", 11), bg=self.accent_color,
                               fg="white", bd=0, command=self.new_note)
        self.add_btn.pack(fill=tk.X, pady=10, ipady=8)

    def update_list(self):
        """Listeyi güncelle"""
        # Eski notları temizle
        for widget in self.notes_list.winfo_children():
            if widget != self.add_btn:
                widget.destroy()
        
        # Notları ekle
        for note_id, note_data in self.note_manager.notes.items():
            self._add_note_to_list(note_data)

    def _add_note_to_list(self, note_data):
        """Listeye not ekle"""
        note_frame = tk.Frame(self.notes_list, bg="white", bd=1, relief=tk.RAISED)
        note_frame.pack(fill=tk.X, pady=5)
        
        # Renk göstergesi
        tk.Frame(note_frame, width=5, bg=note_data["color"]).pack(side=tk.LEFT, fill=tk.Y)
        
        # İçerik
        content_frame = tk.Frame(note_frame, bg="white")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Başlık
        tk.Label(content_frame, text=note_data["title"], 
                font=("Verdana", 11, "bold"), 
                bg="white", fg=self.text_color, anchor=tk.W).pack(fill=tk.X)
        
        # Önizleme
        preview = note_data["text"][:60] + "..." if len(note_data["text"]) > 60 else note_data["text"]
        tk.Label(content_frame, text=preview, 
                font=("Verdana", 9), 
                bg="white", fg="#666666", anchor=tk.W).pack(fill=tk.X)
        
        # Butonlar
        btn_frame = tk.Frame(note_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        # Aç butonu
        tk.Button(btn_frame, text="Aç", font=("Verdana", 9), 
                 bg="#E9ECEF", fg=self.text_color, bd=0,
                 command=lambda id=note_data["id"]: self.open_note(id)).pack(side=tk.LEFT, padx=2)
        
        # Sil butonu
        tk.Button(btn_frame, text="Sil", font=("Verdana", 9), 
                 bg="#E9ECEF", fg="#EF476F", bd=0,
                 command=lambda id=note_data["id"]: self.delete_note(id)).pack(side=tk.LEFT, padx=2)

    def new_note(self):
        """Yeni not oluştur"""
        note = YazBozzNote(self.root, self.note_manager)
        note.window.focus_force()

    def open_note(self, note_id):
        """Notu aç"""
        note_data = self.note_manager.notes.get(note_id)
        if note_data:
            # Zaten açık mı kontrol et
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel) and hasattr(window, 'note_id') and window.note_id == note_id:
                    window.lift()
                    return
            
            # Yeni not penceresi oluştur
            YazBozzNote(
                self.root,
                self.note_manager,
                note_id=note_data["id"],
                title=note_data["title"],
                text=note_data["text"],
                color=note_data["color"],
                position=note_data["position"],
                size=note_data["size"])

    def delete_note(self, note_id):
        """Notu sil"""
        self.note_manager.delete_note(note_id)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Windows DPI ayarı
    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    app = YazBozzApp(root)
    root.mainloop()