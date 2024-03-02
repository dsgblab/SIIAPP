import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pyodbc

class MyFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self, text="OP:")
        self.label.grid(row=0, column=0, padx=20)
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter OP")
        self.entry.grid(row=0, column=1, padx=20)

        # Button to fetch data
        self.fetch_button = ctk.CTkButton(self, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.grid(row=0, column=2, columnspan=2, pady=10)

    def fetch_data(self):
        # Get the ID entered by the user
        entered_id = self.entry.get()

        # Connect to the SQL Server
        connection_string = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=ssf_genericos;UID=sa;PWD=Genericos0224'

        try:
            with pyodbc.connect(connection_string) as connection:
                # Execute a SQL query to fetch data based on the entered ID
                query = """
                SELECT V_fp_pedidos.Pedido, V_fp_pedidos.[Codigo Producto], in_items.itedesclarg AS NomProducto, V_fp_pedidos.[Fecha Requerida], V_fp_pedidos.[Cantidad Pedida], V_fp_pedidos.[Estado Pedido], V_fp_pedidos.OP, V_fp_pedidos.eobnombre AS [Estado OP], in_items.itecompania
                FROM V_fp_pedidos
                INNER JOIN in_items ON V_fp_pedidos.[Codigo Producto] = in_items.itecodigo
                WHERE (V_fp_pedidos.eobnombre IN ('Por ejecutar', 'En ejecucion')) AND (in_items.itecompania = '01')
                AND (V_fp_pedidos.OP = ?)
                """

                cursor = connection.cursor()
                cursor.execute(query, entered_id)

                # Fetch the data
                data = cursor.fetchone()
        except pyodbc.Error as e:
            print(f"Error: {e}")
            messagebox.showerror("Database Error", f"An error occurred while fetching data: {str(e)}")
            return

        # Check if data is found
        if data:
            # Create labels and entries for each field in the fetched data
            for i, column_value in enumerate(data):
                label_text = f"column{i + 1}"
                entry_text = str(column_value)

                label = ctk.CTkLabel(self, text=label_text)
                label.grid(row=i + 2, column=0, padx=20)

                entry = ctk.CTkLabel(self, text=entry_text, width=300)
                entry.grid(row=i + 2, column=1, padx=20)

        else:
            print(f"Error: {e}")
            messagebox.showinfo("No Data", "No data found for the entered ID.")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.my_frame = MyFrame(master=self, width=300, height=200, corner_radius=0, fg_color="transparent")
        self.my_frame.grid(row=0, column=0, sticky="nsew")

app = App()
app.geometry("800x400")
app.mainloop()