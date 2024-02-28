import tkinter as TK
import customtkinter as CTk
from tkcalendar import DateEntry
import pyodbc
from tkinter import messagebox

# List to store the column names
column_names = []

# List to store custom labels
custom_labels = ["ID", "Fecha solicitud", "PT", "Nombre del producto", "Area que solicita", "Fraccion de la Formulacion a Homologar", "Nombre de la materia Prima", "Numero de proovedores consultados", "Entrega de informacion Tecnica", "Informacion tecnica cumple para recepcionar muestra", "Fecha de entrega muestra por parte de proveedores a desarrollo", "Fecha de respuesta desarrollo", "Materia Prima cumple para Homologacion", "Proveedor seleccionado para homologar", "Nombre de la materia Prima aprobada", "Crear Nuevo GR", "Observaciones","Estado"]
select_date_buttons = []
def fetch_data():
    try:
        # Clear the warning label
        warning_label.configure(text="")
        
        # Clear the list of column names before fetching new data
        column_names.clear()

        # Connect to the SQL Server database
        connection = pyodbc.connect('DRIVER={SQL Server};SERVER=10.10.10.251\\softland;DATABASE=SIIAPP;UID=SIIAPP;PWD=1Qaz2wsx*')

        # Create a cursor
        cursor = connection.cursor()

        # Fetch column names from the information schema
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Solicitudes_Homologacion'")
        column_names.extend([row.COLUMN_NAME for row in cursor.fetchall()])

        # Fetch data from the "Solicitudes_Homologacion" table using the primary key "ID"
        query = "SELECT * FROM Solicitudes_Homologacion WHERE ID = ?"
        primary_key_value = int(entry_id.get())  # Get the ID entered by the user
        cursor.execute(query, primary_key_value)

        # Fetch the result
        result = cursor.fetchone()

        # Clear any previous data and disable the "Update" button
        for entry in data_entries:
            entry.destroy()
        data_entries.clear()
        update_button.configure(state=CTk.DISABLED)

        if result:
            # Display the result with custom labels in labels and entry fields
            for i, custom_label in enumerate(custom_labels):
                label = CTk.CTkLabel(window, text=custom_label + ":")
                label.grid(row=i, column=0, padx=5, pady=5, sticky=CTk.W)

                if custom_label == 'Area que solicita':
                    # Use Combobox for specific entry fields
                    area_values = ["Financiero", "Bodega", "Compras", "Otra"]
                    combobox = CTk.CTkComboBox(window, values=area_values, state='readonly')
                    combobox.set(result[i]) if result[i] is not None else ""
                    combobox.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(combobox)
                elif custom_label == 'Fraccion de la Formulacion a Homologar':
                    # Use Combobox for specific entry fields
                    fraccion_values = ["Fragancia", "Activo", "Base de la formulacion"]
                    combobox = CTk.CTkComboBox(window, values=fraccion_values, state='readonly')
                    combobox.set(result[i]) if result[i] is not None else ""
                    combobox.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(combobox)
                elif custom_label == 'Proveedor seleccionado para homologar':
                    # Use Combobox for specific entry fields
                    proveedor_values = ["Otro","Bellchem","Protecnica","Merquimia","Rocsa","Quimifast","LyF","Presquim SAS","Croda","Disan","Mathiesen","Quimicos Integrales","Cromaroma","Chemyunion","IMCD","Sumilab","Sumiquim","Quimica Lider","Novacolor","Conquimica","Colorquimica","Quimica Express","PROES","Ferhmann SA","Golden","Quimicos Adhara","Symrise-Quimicos","Nativus","Mcassab","Pochteca","Ricardo Molina","Aromatheka","ECOCHEM","Dunamis","Colquimicos","Stepan","Factores y Mercadeo","Brenntag","Urigo SAS","Handler","Perysa","Sensoria","Fullarome","fragansa","Disaromas","La Tour Fragancias","Polaroma","Fiproquim","Biotechnis","Aroc","Quimicos del Cauca","Retema","Terracota Quimicos","Polaroma","Escol ( Essential Colombia)","Inversiones Brakca","ANBUCO SAS","ImporQuim Group","Ingredion","Quimerco","Seppic Colombia S.A.S."]
                    combobox = CTk.CTkComboBox(window, values=proveedor_values, state='readonly')
                    combobox.set(result[i]) if result[i] is not None else ""
                    combobox.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(combobox)
                elif custom_label in ['Entrega de informacion Tecnica', 'Informacion tecnica cumple para recepcionar muestra', 'Materia Prima cumple para Homologacion', 'Crear Nuevo GR']:
                    # Use Combobox for specific entry fields
                    common_values = ["SI", "NO"]
                    combobox = CTk.CTkComboBox(window, values=common_values, state='readonly')
                    combobox.set(result[i]) if result[i] is not None else ""
                    combobox.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(combobox)
                elif custom_label in ['Estado']:
                    # Use Combobox for specific entry fields
                    common_values = ["Investigacion Proveedores", "En espera de Materia prima","En formulacion teorica","Estabilidad Laboratorio"]
                    combobox = CTk.CTkComboBox(window, values=common_values, state='readonly')
                    combobox.set(result[i]) if result[i] is not None else ""
                    combobox.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(combobox)
                elif custom_label == 'ID':
                    id_entry = CTk.CTkEntry(window, state='disabled')
                    id_entry.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(id_entry)
                else:
                    data_entry = CTk.CTkEntry(window)
                    data_entry.insert(0, str(result[i]) if result[i] is not None else "")
                    data_entry.grid(row=i, column=1, padx=5, pady=5, sticky=CTk.W)
                    data_entries.append(data_entry)
            
            # Enable the "Update" button
            update_button.configure(state=CTk.NORMAL)
            # Disable the "Traer Datos" button
            fetch_button.configure(state=CTk.DISABLED)
            for i, custom_label in enumerate(['Fecha solicitud']):
                select_date_button = CTk.CTkButton(window, text=f'Elegir fecha para {custom_label}', command=lambda label=custom_label: select_date(label))
                select_date_button.grid(row=i+1, column=2, padx=5, pady=5, sticky=CTk.W)
                select_date_buttons.append(select_date_button)
            for i, custom_label in enumerate(['Fecha de entrega muestra por parte de proveedores a desarrollo']):
                select_date_button = CTk.CTkButton(window, text=f'Elegir fecha para {custom_label}', command=lambda label=custom_label: select_date(label))
                select_date_button.grid(row=10, column=2, padx=5, pady=5, sticky=CTk.W)
                select_date_buttons.append(select_date_button)
            for i, custom_label in enumerate(['Fecha de respuesta desarrollo']):
                select_date_button = CTk.CTkButton(window, text=f'Elegir fecha para {custom_label}', command=lambda label=custom_label: select_date(label))
                select_date_button.grid(row=11, column=2, padx=5, pady=5, sticky=CTk.W)
                select_date_buttons.append(select_date_button)
        else:
            # If no result is found, display a warning
            warning_label.configure(text="ID no encontrado, Porfavor ingrese un ID valido")
        # Close the cursor and connection
        cursor.close()
        connection.close()

    except pyodbc.Error as e:
        print(f"Database Error: {e}")
        messagebox.showerror("Error", f"Database operation failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def select_date(label):
    date_picker = TK.Toplevel(window)
    date_picker.title(f'Selecionar fecha para {label}')
    
    # Make the date picker window stay on top
    date_picker.attributes('-topmost', 'true')

    # Set the size of the date picker window
    date_picker.geometry('300x200')  # Adjust the size as needed

    # Create DateEntry widget
    date_entry = DateEntry(date_picker, width=20, background='darkblue', foreground='white', borderwidth=5)
    date_entry.pack(padx=10, pady=15)

    # CTkButton to set the selected date
    set_date_button = CTk.CTkButton(date_picker, text='Fijar fecha', command=lambda: set_selected_date(date_entry, label))
    set_date_button.pack(padx=10, pady=10)

def set_selected_date(date_entry, label):
    selected_date = date_entry.get_date()
    entry_index = custom_labels.index(label)
    
    # Update the corresponding entry widget with the selected date
    data_entries[entry_index].delete(0, CTk.END)
    data_entries[entry_index].insert(0, selected_date.strftime('%d/%m/%Y'))
    
    # Close the date picker window
    date_entry.winfo_toplevel().destroy()

def update_data():
    try:
        # Connect to the SQL Server database
        connection = pyodbc.connect('DRIVER={SQL Server};SERVER=10.10.10.251\\softland;DATABASE=SIIAPP;UID=SIIAPP;PWD=1Qaz2wsx*')

        # Create a cursor
        cursor = connection.cursor()

        # Update data in the "Solicitudes_Homologacion" table
        update_query = "UPDATE Solicitudes_Homologacion SET {} WHERE ID = ?"

        # Construct the SET clause for the update query (excluding ID)
        set_clause = ", ".join(f"{column_name} = ?" for column_name in column_names if column_name != 'ID')

        # Get values from the entry fields (excluding ID value)
        update_values = [entry.get() for entry in data_entries[1:]]  # Exclude the ID entry

        # Add the ID value to the WHERE clause
        id_value = int(entry_id.get())
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
        for button in select_date_buttons:
            button.configure(state=CTk.DISABLED)
        # Enable the "Traer Datos" button
        fetch_button.configure(state=CTk.NORMAL)

        # Clear any previous data and disable the "Update" button
        for entry in data_entries:
            entry.destroy()
        data_entries.clear()
        update_button.configure(state=CTk.DISABLED)
        

    except Exception as e:
        print(f"Error: {e}")
        # Show error message
        messagebox.showerror("Error", f"La actualizacion fallo: {e}")

def reset_interface():
    # Clear any previous data and disable the "Update" button
    for entry in data_entries:
        entry.destroy()
    data_entries.clear()
    update_button.configure(state=CTk.DISABLED)
    entry_id.delete(0, CTk.END)  # Clear the ID entry
    entry_id.configure(state=CTk.NORMAL)
# Disable the date entry buttons
    for button in select_date_buttons:
        button.configure(state=CTk.DISABLED)
    # Enable the "Traer Datos" button
    fetch_button.configure(state=CTk.NORMAL)# Enable the ID entry for editing

# Rest of the code remains unchanged

# Create a Tkinter window
window = CTk.CTk()
window.title("Formato Homologaciones")

# List to store the entry widgets for data editing
data_entries = []

# Entry for entering the ID (entry_id).
id_label = CTk.CTkLabel(window, text="ingrese el ID:")
id_label.grid(row=0, column=0, padx=5, pady=5, sticky=CTk.W)

entry_id = CTk.CTkEntry(window)
entry_id.grid(row=0, column=1, padx=5, pady=5, sticky=CTk.W)

# Create a frame for the buttons
buttons_frame = CTk.CTkFrame(window)
buttons_frame.grid(row=0, column=2, padx=10, pady=10, sticky=CTk.E)

# CTkButton to fetch data
fetch_button = CTk.CTkButton(buttons_frame, text="Traer Datos", command=fetch_data)
fetch_button.grid(row=0, column=0, padx=10, pady=10)

# CTkButton to update data
update_button = CTk.CTkButton(buttons_frame, text="Actualizar Datos", command=update_data, state=CTk.DISABLED, fg_color="green")
update_button.grid(row=0, column=1, padx=10, pady=10)

# CTkButton to reset interface
cancel_button = CTk.CTkButton(buttons_frame, text="Cancelar", command=reset_interface, fg_color="red")
cancel_button.grid(row=0, column=2, padx=10, pady=10)

# CTkLabel for displaying warning
warning_label = CTk.CTkLabel(buttons_frame, text="")
warning_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=CTk.W)

# Run the Tkinter main loop
window.mainloop()
