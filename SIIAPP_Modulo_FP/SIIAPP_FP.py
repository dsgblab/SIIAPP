import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
import pyodbc
from tksheet import Sheet


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create Tksheet widget
        self.sheet = Sheet(self)
        self.sheet.pack(fill="both", expand=True)

        # fases_produccion
        self.fases = [
            "",
            "Dispenciacion",
            "Pesaje",
            "Fabricacion",
            "Microbiologia",
            "Envasado",
            "Acondicionamiento",
            "Embalaje",
            "Despacho"
        ]
        # plantas de produccion
        self.plantas = ["", "01", "02"]

        # Configure column headers
        headers = [
            "Pedido",
            "Codigo Producto",
            "Nombre del Producto",
            "Fecha Requerida",
            "Cantidad Pedida",
            "Estado Pedido",
            "OP",
            "Estado OP",
            "Item Compañia",
            "FP_ID",
            "Cantidad en fase de produccion",
            "Fase de Produccion",
            "Planta",
            "Observaciones/Comentarios"
        ]
        self.sheet.headers(headers)

        # Configure column widths
        column_widths = [100, 120, 800, 120, 120,
                         120, 80, 120, 100, 100, 100, 80, 200]
        for i, width in enumerate(column_widths):
            self.sheet.column_width(column=i, width=width)

        # Enable row selection
        self.sheet.enable_bindings(("single_select", "row_select"))

        # Create a scrollable frame
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Create filter entry
        self.filter_entry = ctk.CTkEntry(
            self.scrollable_frame, placeholder_text="Filtrar por OP")
        self.filter_entry.pack(padx=10, pady=10, fill="x")
        self.filter_entry.bind("<Return>", self.filter_data)

        # Create buttons
        self.button_frame = ctk.CTkFrame(self.scrollable_frame)
        self.button_frame.pack(padx=10, pady=10, fill="x")

        self.create_child_button = ctk.CTkButton(
            self.button_frame, text="Crear Registro", command=self.create_child_record)
        self.create_child_button.pack(side="left", padx=5)

        self.edit_child_button = ctk.CTkButton(
            self.button_frame, text="Editar Registro", command=self.edit_child_record)
        self.edit_child_button.pack(side="left", padx=5)

        # Load data from the database
        self.load_data()

    def load_data(self):
        # Connect to the database
        conn_str = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=ssf_genericos;UID=sa;PWD=Genericos0224*'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Fetch data from the database
        query = query = """
                SELECT 
            V_fp_pedidos.Pedido, 
            V_fp_pedidos.[Codigo Producto], 
            in_items.itedesclarg AS NomProducto,
            V_fp_pedidos.[Fecha Requerida], 
            V_fp_pedidos.[Cantidad Pedida], 
            V_fp_pedidos.[Estado Pedido],
            V_fp_pedidos.OP, 
            V_fp_pedidos.eobnombre AS [Estado OP], 
            in_items.itecompania,
            FP_PROGRES.FP_ID, 
            FP_PROGRES.CANTIDAD_FP, 
            FP_PROGRES.FASE_PODUCC, 
            FP_PROGRES.PLANTA, 
            FP_PROGRES.COMENTARIES
        FROM 
            [ssf_genericos].[dbo].[V_fp_pedidos]
        INNER JOIN 
            [ssf_genericos].[dbo].[in_items] ON V_fp_pedidos.[Codigo Producto] = in_items.itecodigo
        LEFT JOIN 
            [SIIAPP].[dbo].[FP_PROGRES] AS FP_PROGRES 
            ON V_fp_pedidos.OP = FP_PROGRES.orpconsecutivo COLLATE Latin1_General_CI_AS
        WHERE 
            (V_fp_pedidos.eobnombre IN ('Por ejecutar', 'En ejecucion', 'En firme'))
            AND (in_items.itecompania = '01');
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Insert data into the Tksheet
        formatted_data = []
        for row in data:
            parent_row = [
                str(value) if value is not None else "" for value in row[:9]]
            fp_progres_values = row[9:]

            if any(fp_progres_values):
                parent_row.extend(
                    str(value) if value is not None else "" for value in fp_progres_values)
            else:
                # Add empty cells for FP_PROGRES columns
                parent_row.extend([""] * 5)

            formatted_data.append(parent_row)

        self.original_data = formatted_data
        self.sheet.set_sheet_data(formatted_data)

        # Highlight FP_PROGRES columns
        for i in range(9, 14):
            self.sheet.highlight_columns(
                columns=[i], bg="lightgray", fg="black")

        # Close the database connection
        cursor.close()
        conn.close()

    def filter_data(self, event):
        op_filter = self.filter_entry.get()
        if op_filter:
            filtered_data = [
                row for row in self.original_data if op_filter in row[6]]
            self.sheet.set_sheet_data(filtered_data)
        else:
            self.sheet.set_sheet_data(self.original_data)

    def create_child_record(self):
        selected_rows = self.sheet.get_selected_rows()
        if selected_rows:
            # Get the first selected row
            selected_row = next(iter(selected_rows))
            row_data = self.sheet.get_row_data(selected_row)
            op_value = row_data[6]  # Assuming 'OP' is at index 6
            it_comp = row_data[8]  # Assuming

            # Create a new window for entering child record data
            child_window = ctk.CTkToplevel(self)
            child_window.title("Crear Registro de Fase de Produccion")

            # Add input fields for child record data
            cantidad_fp_entry = ctk.CTkEntry(
                child_window, placeholder_text="Cantidad en fase de produccion")
            fase_producc_entry = ctk.CTkComboBox(
                child_window, values=self.fases, state="readonly")
            planta_entry = ctk.CTkComboBox(
                child_window,  values=self.plantas, state="readonly")
            comentarios_entry = ctk.CTkTextbox(
                child_window, height=50, width=200)
            comentarios_entry.configure(
                border_color='blue', border_width=0.5)
            # Grid view
            cantidad_fp_label = ctk.CTkLabel(
                child_window, text="Cantidad en fase de produccion:")
            cantidad_fp_label.grid(row=0, column=0, padx=5, pady=5)
            cantidad_fp_entry.grid(row=0, column=1, padx=5, pady=5)

            fase_producc_label = ctk.CTkLabel(
                child_window, text="Fase de Produccion:")
            fase_producc_label.grid(row=1, column=0, padx=5, pady=5)
            fase_producc_entry.grid(row=1, column=1, padx=5, pady=5)

            planta_label = ctk.CTkLabel(child_window, text="Planta:")
            planta_label.grid(row=2, column=0, padx=5, pady=5)
            planta_entry.grid(row=2, column=1, padx=5, pady=5)

            comentarios_label = ctk.CTkLabel(
                child_window, text="Observasiones/Comentarios:")
            comentarios_label.grid(row=3, column=0, padx=5, pady=5)
            comentarios_entry.grid(row=3, column=1, padx=5, pady=5)

            def save_child_record():
                cantidad_fp = cantidad_fp_entry.get()
                fase_producc = fase_producc_entry.get()
                planta = planta_entry.get()
                comentarios = comentarios_entry.get("0.0", "end")

                # Insert the child record into the database
                conn_str = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=SIIAPP;UID=sa;PWD=Genericos0224*'
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()

                insert_query = """
                INSERT INTO FP_PROGRES (orpconsecutivo, orpcompania, CANTIDAD_FP, FASE_PODUCC, PLANTA, COMENTARIES)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_query, (op_value, it_comp, cantidad_fp,
                               fase_producc, planta, comentarios))
                conn.commit()

                cursor.close()
                conn.close()

                child_window.destroy()
                self.reload_data()

            save_button = ctk.CTkButton(
                child_window, text="Guardar", command=save_child_record)
            save_button.grid(row=4, column=0, columnspan=2, pady=10)
        else:
            messagebox.showinfo(
                "Sin seleccion", "Porfavor eliga una fila para Crear un registro")

    def edit_child_record(self):
        selected_rows = self.sheet.get_selected_rows()
        if selected_rows:
            # Get the first selected row
            selected_row = next(iter(selected_rows))
            row_data = self.sheet.get_row_data(selected_row)
            op_value = row_data[6]  # Assuming 'OP' is at index 6
            fp_id = row_data[9]  # Assuming 'FP_ID' is at index 9

            # Create a new window for editing child record data
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Editar registro de fase de produccion")

            # Add input fields for child record data
            cantidad_fp_entry = ctk.CTkEntry(
                edit_window, placeholder_text="Cantidad en fase de produccion")
            # Pre-fill with existing data
            cantidad_fp_entry.insert(0, row_data[10])
            fase_producc_entry = ctk.CTkComboBox(
                edit_window, values=self.fases, state="readonly")
            # Pre-fill with existing data
            fase_producc_entry.set(row_data[11])
            planta_entry = ctk.CTkComboBox(
                edit_window,  values=self.plantas, state="readonly")
            planta_entry.set(row_data[12])
            # Pre-fill with existing data
            comentarios_entry = ctk.CTkTextbox(
                edit_window, height=50, width=200)
            # Pre-fill with existing data
            comentarios_entry.insert("0.0", row_data[13])
            comentarios_entry.configure(
                border_color='blue', border_width=0.5)
            # Grid view
            cantidad_fp_label = ctk.CTkLabel(
                edit_window, text="Cantidad en fase de produccion:")
            cantidad_fp_label.grid(row=0, column=0, padx=5, pady=5)
            cantidad_fp_entry.grid(row=0, column=1, padx=5, pady=5)

            fase_producc_label = ctk.CTkLabel(
                edit_window, text="Fase de Produccion:")
            fase_producc_label.grid(row=1, column=0, padx=5, pady=5)
            fase_producc_entry.grid(row=1, column=1, padx=5, pady=5)

            planta_label = ctk.CTkLabel(edit_window, text="Planta:")
            planta_label.grid(row=2, column=0, padx=5, pady=5)
            planta_entry.grid(row=2, column=1, padx=5, pady=5)

            comentarios_label = ctk.CTkLabel(
                edit_window, text="Observaciones/Comentarios:")
            comentarios_label.grid(row=3, column=0, padx=5, pady=5)
            comentarios_entry.grid(row=3, column=1, padx=5, pady=5)

            def save_edited_child_record():
                cantidad_fp = cantidad_fp_entry.get()
                fase_producc = fase_producc_entry.get()
                planta = planta_entry.get()
                comentarios = comentarios_entry.get("0.0", "end")

                # Update the child record in the database
                conn_str = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=SIIAPP;UID=sa;PWD=Genericos0224*'
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()

                update_query = """
                UPDATE FP_PROGRES
                SET CANTIDAD_FP = ?, FASE_PODUCC = ?, PLANTA = ?, COMENTARIES = ?
                WHERE FP_ID = ?
                """
                cursor.execute(update_query, (cantidad_fp,
                               fase_producc, planta, comentarios, fp_id))
                conn.commit()

                cursor.close()
                conn.close()

                edit_window.destroy()
                self.reload_data()

            save_button = ctk.CTkButton(
                edit_window, text="Guardar Cambios", command=save_edited_child_record)
            save_button.grid(row=4, column=0, columnspan=2, pady=10)
        else:
            messagebox.showinfo(
                "Sin seleccion", "Porfavor eliga una fila para editar un registro")

    def reload_data(self):
        # Clear existing data
        self.sheet.set_sheet_data([])

        # Load updated data from the database
        self.load_data()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.my_frame = MyFrame(master=self)
        self.my_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


app = App()
app.geometry("800x400")
app.mainloop()
