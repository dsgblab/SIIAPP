import tkinter as TK
import customtkinter as ctk
from tkcalendar import DateEntry
import pyodbc
from tkinter import messagebox


class MyFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # List to store the column names
        self.column_names = []
        # List to store the entry widgets for data editing
        self.data_entries = []

        # Entry for entering the ID (entry_id).
        self.id_label = ctk.CTkLabel(self, text="ingrese el ID:")
        self.id_label.grid(row=0, column=0, padx=5, pady=5, sticky=ctk.W)

        self.entry_id = ctk.CTkEntry(self)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.W)

        # Create a frame for the buttons
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.grid(
            row=0, column=2, padx=10, pady=10, sticky=ctk.E)

        # CTkButton to fetch data
        self.fetch_button = ctk.CTkButton(
            self.buttons_frame, text="Traer Datos", command=self.fetch_data)
        self.fetch_button.grid(row=0, column=0, padx=10, pady=10)

        # CTkButton to update data
        self.update_button = ctk.CTkButton(
            self.buttons_frame, text="Actualizar Datos", command=self.update_data, state=ctk.DISABLED, fg_color="green")
        self.update_button.grid(row=0, column=1, padx=10, pady=10)

        # CTkButton to reset interface
        self.cancel_button = ctk.CTkButton(
            self.buttons_frame, text="Cancelar", command=self.reset_interface, fg_color="red")
        self.cancel_button.grid(row=0, column=2, padx=10, pady=10)

        # CTkLabel for displaying warning
        self.warning_label = ctk.CTkLabel(self.buttons_frame, text="")
        self.warning_label.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky=ctk.W)

        # List to store custom labels
        self.custom_labels = ["ID", "Fecha solicitud", "PT", "Nombre del producto", "Area que solicita", "Fraccion de la Formulacion a Homologar", "Nombre de la materia Prima", "Numero de proovedores consultados", "Entrega de informacion Tecnica", "Informacion tecnica cumple para recepcionar muestra",
                              "Fecha de entrega muestra por parte de proveedores a desarrollo", "Fecha de respuesta desarrollo", "Materia Prima cumple para Homologacion", "Proveedor seleccionado para homologar", "Nombre de la materia Prima aprobada", "Crear Nueva Version de PT", "Observaciones", "Estado"]
        self.select_date_buttons = []

    def fetch_data(self):
        try:
            # Clear the warning label
            self.warning_label.configure(text="")

            # Clear the list of column names before fetching new data
            self.column_names.clear()

            # Connect to the SQL Server database
            connection = pyodbc.connect(
                'DRIVER={SQL Server};SERVER=10.10.10.251\\softland;DATABASE=SIIAPP;UID=SIIAPP;PWD=1Qaz2wsx*')

            # Create a cursor
            cursor = connection.cursor()

            # Fetch column names from the information schema
            cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Solicitudes_Homologacion'")
            self.column_names.extend(
                [row.COLUMN_NAME for row in cursor.fetchall()])

            # Fetch data from the "Solicitudes_Homologacion" table using the primary key "ID"
            query = "SELECT * FROM Solicitudes_Homologacion WHERE ID = ?"
            # Get the ID entered by the user
            primary_key_value = int(self.entry_id.get())
            cursor.execute(query, primary_key_value)

            # Fetch the result
            result = cursor.fetchone()

            # Clear any previous data and disable the "Update" button
            for entry in self.data_entries:
                entry.destroy()
            self.data_entries.clear()
            self.update_button.configure(state=ctk.DISABLED)

            if result:
                # Display the result with custom labels in labels and entry fields
                for i, custom_label in enumerate(self.custom_labels):
                    label = ctk.CTkLabel(self, text=custom_label + ":")
                    label.grid(row=i, column=0, padx=5, pady=5, sticky=ctk.W)

                    if custom_label == 'Area que solicita':
                        # Use Combobox for specific entry fields
                        area_values = ["Financiero",
                                       "Bodega", "Compras", "Otra"]
                        combobox = ctk.CTkComboBox(
                            self, values=area_values, state='readonly')
                        combobox.set(
                            result[i]) if result[i] is not None else ""
                        combobox.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(combobox)
                    elif custom_label == 'Fraccion de la Formulacion a Homologar':
                        # Use Combobox for specific entry fields
                        fraccion_values = ["Fragancia",
                                           "Activo", "Base de la formulacion"]
                        combobox = ctk.CTkComboBox(
                            self, values=fraccion_values, state='readonly')
                        combobox.set(
                            result[i]) if result[i] is not None else ""
                        combobox.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(combobox)
                    elif custom_label == 'Proveedor seleccionado para homologar':
                        # Use Combobox for specific entry fields
                        proveedor_values = ["Otro", "Bellchem", "Protecnica", "Merquimia", "Rocsa", "Quimifast", "LyF", "Presquim SAS", "Croda", "Disan", "Mathiesen", "Quimicos Integrales", "Cromaroma", "Chemyunion", "IMCD", "Sumilab", "Sumiquim", "Quimica Lider", "Novacolor", "Conquimica", "Colorquimica", "Quimica Express", "PROES", "Ferhmann SA", "Golden", "Quimicos Adhara", "Symrise-Quimicos", "Nativus", "Mcassab", "Pochteca", "Ricardo Molina", "Aromatheka",
                                            "ECOCHEM", "Dunamis", "Colquimicos", "Stepan", "Factores y Mercadeo", "Brenntag", "Urigo SAS", "Handler", "Perysa", "Sensoria", "Fullarome", "fragansa", "Disaromas", "La Tour Fragancias", "Polaroma", "Fiproquim", "Biotechnis", "Aroc", "Quimicos del Cauca", "Retema", "Terracota Quimicos", "Polaroma", "Escol ( Essential Colombia)", "Inversiones Brakca", "ANBUCO SAS", "ImporQuim Group", "Ingredion", "Quimerco", "Seppic Colombia S.A.S."]
                        combobox = ctk.CTkComboBox(
                            self, values=proveedor_values, state='readonly')
                        combobox.set(
                            result[i]) if result[i] is not None else ""
                        combobox.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(combobox)
                    elif custom_label in ['Entrega de informacion Tecnica', 'Informacion tecnica cumple para recepcionar muestra', 'Materia Prima cumple para Homologacion', 'Crear Nueva Version de PT']:
                        # Use Combobox for specific entry fields
                        common_values = ["SI", "NO"]
                        combobox = ctk.CTkComboBox(
                            self, values=common_values, state='readonly')
                        combobox.set(
                            result[i]) if result[i] is not None else ""
                        combobox.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(combobox)
                    elif custom_label in ['Estado']:
                        # Use Combobox for specific entry fields
                        common_values = ["Investigacion Proveedores", "En espera de Materia prima",
                                         "En formulacion teorica", "Estabilidad Laboratorio", "Aplicacion por tecnico experto","Rechazado","Aprobado"]
                        combobox = ctk.CTkComboBox(
                            self, values=common_values, state='readonly')
                        combobox.set(
                            result[i]) if result[i] is not None else ""
                        combobox.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(combobox)
                    elif custom_label == 'ID':
                        id_entry = ctk.CTkEntry(self, state='disabled')
                        id_entry.grid(row=i, column=1, padx=5,
                                      pady=5, sticky=ctk.W)
                        self.data_entries.append(id_entry)
                    else:
                        data_entry = ctk.CTkEntry(self)
                        data_entry.insert(
                            0, str(result[i]) if result[i] is not None else "")
                        data_entry.grid(row=i, column=1, padx=5,
                                        pady=5, sticky=ctk.W)
                        self.data_entries.append(data_entry)

                # Enable the "Update" button
                self.update_button.configure(state=ctk.NORMAL)
                # Disable the "Traer Datos" button
                self.fetch_button.configure(state=ctk.DISABLED)
                for i, custom_label in enumerate(['Fecha solicitud']):
                    select_date_button = ctk.CTkButton(self, text=f'Elegir fecha para {
                                                       custom_label}', command=lambda label=custom_label: self.select_date(label))
                    select_date_button.grid(
                        row=i+1, column=2, padx=5, pady=5, sticky=ctk.W)
                    self.select_date_buttons.append(select_date_button)
                for i, custom_label in enumerate(['Fecha de entrega muestra por parte de proveedores a desarrollo']):
                    select_date_button = ctk.CTkButton(self, text=f'Elegir fecha para {
                                                       custom_label}', command=lambda label=custom_label: self.select_date(label))
                    select_date_button.grid(
                        row=10, column=2, padx=5, pady=5, sticky=ctk.W)
                    self.select_date_buttons.append(select_date_button)
                for i, custom_label in enumerate(['Fecha de respuesta desarrollo']):
                    select_date_button = ctk.CTkButton(self, text=f'Elegir fecha para {
                                                       custom_label}', command=lambda label=custom_label: self.select_date(label))
                    select_date_button.grid(
                        row=11, column=2, padx=5, pady=5, sticky=ctk.W)
                    self.select_date_buttons.append(select_date_button)
            else:
                # If no result is found, display a warning
                self.warning_label.configure(
                    text="ID no encontrado, Porfavor ingrese un ID valido")
            # Close the cursor and connection
            cursor.close()
            connection.close()

        except pyodbc.Error as e:
            print(f"Database Error: {e}")
            messagebox.showerror("Error", f"Database operation failed: {e}")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_date(self, label):
        date_picker = TK.Toplevel(app)
        date_picker.title(f'Selecionar fecha para {label}')

        # Make the date picker window stay on top
        date_picker.attributes('-topmost', 'true')

        # Set the size of the date picker window
        date_picker.geometry('300x200')  # Adjust the size as needed

        # Create DateEntry widget
        date_entry = DateEntry(
            date_picker, width=20, background='darkblue', foreground='white', borderwidth=5)
        date_entry.pack(padx=10, pady=15)

        # CTkButton to set the selected date
        set_date_button = ctk.CTkButton(
            date_picker, text='Fijar fecha', command=lambda: self.set_selected_date(date_entry, label))
        set_date_button.pack(padx=10, pady=10)

    def set_selected_date(self, date_entry, label):
        selected_date = date_entry.get_date()
        entry_index = self.custom_labels.index(label)

        # Update the corresponding entry widget with the selected date
        self.data_entries[entry_index].delete(0, ctk.END)
        self.data_entries[entry_index].insert(
            0, selected_date.strftime('%d/%m/%Y'))

        # Close the date picker window
        date_entry.winfo_toplevel().destroy()

    def update_data(self):
        try:
            # Connect to the SQL Server database
            connection = pyodbc.connect(
                'DRIVER={SQL Server};SERVER=10.10.10.251\\softland;DATABASE=SIIAPP;UID=SIIAPP;PWD=1Qaz2wsx*')

            # Create a cursor
            cursor = connection.cursor()

            # Update data in the "Solicitudes_Homologacion" table
            update_query = "UPDATE Solicitudes_Homologacion SET {} WHERE ID = ?"

            # Construct the SET clause for the update query (excluding ID)
            set_clause = ", ".join(
                f"{column_name} = ?" for column_name in self.column_names if column_name != 'ID')

            # Get values from the entry fields (excluding ID value)
            # Exclude the ID entry
            update_values = [entry.get() for entry in self.data_entries[1:]]

            # Add the ID value to the WHERE clause
            id_value = int(self.entry_id.get())
            update_values.append(id_value)

            # Execute the update query
            cursor.execute(update_query.format(set_clause), update_values)

            # Commit the changes
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Show success message
            messagebox.showinfo("Success", "Los datos han sido actualizados")

            # Disable the date entry buttons
            for button in self.select_date_buttons:
                button.configure(state=ctk.DISABLED)
            # Enable the "Traer Datos" button
            self.fetch_button.configure(state=ctk.NORMAL)

            # Clear any previous data and disable the "Update" button
            for entry in self.data_entries:
                entry.destroy()
            self.data_entries.clear()
            self.update_button.configure(state=ctk.DISABLED)

        except Exception as e:
            print(f"Error: {e}")
            # Show error message
            messagebox.showerror("Error", f"La actualizacion fallo: {e}")

    def reset_interface(self):
        # Clear any previous data and disable the "Update" button
        for entry in self.data_entries:
            entry.destroy()
        self.data_entries.clear()
        self.update_button.configure(state=ctk.DISABLED)
        self.entry_id.delete(0, ctk.END)  # Clear the ID entry
        self.entry_id.configure(state=ctk.NORMAL)
    # Disable the date entry buttons
        for button in self.select_date_buttons:
            button.configure(state=ctk.DISABLED)
        # Enable the "Traer Datos" button
        # Enable the ID entry for editing
        self.fetch_button.configure(state=ctk.NORMAL)

# Rest of the code remains unchanged

# Create a Tkinter window


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.my_frame = MyFrame(
            master=self, width=300, height=200, corner_radius=0, fg_color="transparent")
        self.my_frame.grid(row=0, column=0, sticky="nsew")


# Run the Tkinter main loop
app = App()
app.geometry("1100x600")
app.mainloop()
