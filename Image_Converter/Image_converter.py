import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import customtkinter as ctk
import os

class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Create file open button
        self.open_button = ctk.CTkButton(self.scrollable_frame, text="Elegir imagenes", command=self.open_files)
        self.open_button.grid(row=0, column=0, padx=5, pady=5)
        self.image_count_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.image_count_label.grid(row=0, column=1, padx=5, pady=5)

        # Create save directory button
        self.save_dir_button = ctk.CTkButton(self.scrollable_frame, text="Elegir directorio de guardado", command=self.select_save_dir)
        self.save_dir_button.grid(row=2, column=0, padx=5, pady=5)
        self.save_dir_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.save_dir_label.grid(row=2, column=1, padx=5, pady=5)

        # Create format selection dropdown
        self.format_label = ctk.CTkLabel(self.scrollable_frame, text="Elegir formato:")
        self.format_label.grid(row=1, column=0, padx=5, pady=5)
        self.format_var = ctk.StringVar(value="webp")
        self.format_dropdown = ctk.CTkOptionMenu(self.scrollable_frame, values=["webp"], variable=self.format_var)
        self.format_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # Create convert button
        self.convert_button = ctk.CTkButton(self.scrollable_frame, text="Convertir", command=self.convert_images, state="disabled",fg_color="green")
        self.convert_button.grid(row=3, column=0, padx=5, pady=5)

        self.files = []
        self.save_dir = ""

    def open_files(self):
        self.files = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.jpg;*.png;*.gif;*.bmp;*.tiff;*.webp")])
        self.update_image_count_label()
        self.update_convert_button_state()

    def select_save_dir(self):
        self.save_dir = filedialog.askdirectory(title="Select Save Directory")
        self.update_save_dir_label()
        self.update_convert_button_state()

    def update_image_count_label(self):
        image_count = len(self.files)
        self.image_count_label.configure(text=f"{image_count} image(s) selected")

    def update_save_dir_label(self):
        self.save_dir_label.configure(text=self.save_dir)

    def update_convert_button_state(self):
        if self.files and self.save_dir:
            self.convert_button.configure(state="normal")
        else:
            self.convert_button.configure(state="disabled")

    def convert_images(self):
        if not self.files:
            return

        target_format = self.format_var.get()
        success_count = 0
        error_count = 0

        for file in self.files:
            try:
                img = Image.open(file)
                filename, ext = os.path.splitext(os.path.basename(file))
                new_ext = f".{target_format}"
                save_path = os.path.join(self.save_dir, f"{filename}{new_ext}")
                img.save(save_path, target_format.upper())
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error converting {file}: {str(e)}")

        if success_count > 0:
            messagebox.showinfo("Conversion Exitosa", f"{success_count} imágenes convertidas exitosamente.")
            self.files = []
            self.update_image_count_label()
            self.update_convert_button_state()
        if error_count > 0:
            messagebox.showerror("Errores de Conversión", f"{error_count} imágenes no se pudieron convertir.")
            self.files = []
            self.update_image_count_label()
            self.update_convert_button_state()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.geometry("400x200")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.login_frame = MyFrame(master=self)
        self.login_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

app = App()
app.title("Conversor de imágenes")
app.mainloop()