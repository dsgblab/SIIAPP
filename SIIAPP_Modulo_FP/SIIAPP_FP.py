import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pyodbc
import threading  # Import the threading module
import cachetools  # Import the cachetools module
from CTkXYFrame import *  # import custom scrollframe from CTkXYFrame
import CTkTable as ctkt

# Enable connection pooling
pyodbc.pooling = True

# Create a cache for frequently accessed data
cache = cachetools.LRUCache(maxsize=100)


class MyFrame(CTkXYFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # List to store the entry widgets for data editing
        self.data_entries = []
        # List to store custom labels
        self.custom_labels = ["Pedido", "Codigo Producto", "Nombre Producto", "Fecha Requerida", "Cantidad pedida", "Estado pedido",
                              "OP", "Estado OP", "Compañia", "Cantidad FP", "Fase de produccion", "Planta", "Comentarios"]

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self, text="OP:")
        self.label.grid(row=0, column=0, padx=20)
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter OP")
        self.entry.grid(row=0, column=1, padx=20)

        # Button to fetch data
        self.fetch_button = ctk.CTkButton(
            self, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.grid(row=0, column=2, pady=10)

        # Button to update data
        self.update_button = ctk.CTkButton(
            self, text="Update Data", command=self.update_data, fg_color="green", state="disabled")
        self.update_button.grid(row=0, column=3, pady=10)

        # Button to cancel everything
        self.cancel_button = ctk.CTkButton(
            self, text="Cancel", command=self.reset_interface, fg_color="red")
        self.cancel_button.grid(row=0, column=4, pady=10, padx=20)

        # Pagination variables
        self.page = 1
        self.page_size = 10
        self.total_pages = 0

        # Buttons to navigate pages
        self.prev_button = ctk.CTkButton(
            self, text="Previous Page", command=self.prev_page)
        self.prev_button.grid(row=1, column=2, pady=10, padx=20)
        self.next_button = ctk.CTkButton(
            self, text="Next Page", command=self.next_page)
        self.next_button.grid(row=1, column=3, pady=10)

        # Label to show current page
        self.page_label = ctk.CTkLabel(
            self, text=f"Page {self.page} of {self.total_pages}")
        self.page_label.grid(row=2, column=2, columnspan=2, pady=10, padx=20)

        # Store the essential widgets
        self.essential_widgets = [
            self.label,
            self.entry,
            self.fetch_button,
            self.update_button,
            self.cancel_button,
            self.prev_button,
            self.next_button,
            self.page_label
        ]

    def fetch_data(self):
        # Get the ID entered by the user
        entered_id = self.entry.get()

        # Use threading for asynchronous execution
        threading.Thread(target=self.fetch_data_async,
                         args=(entered_id,)).start()
        self.update_button.configure(state="normal")

    def fetch_data_async(self, entered_id):
        # Connect to the SQL Server
        connection_string = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=ssf_genericos;UID=sa;PWD=Genericos0224'

        try:
            # Use context managers to handle the connection and cursor objects
            with pyodbc.connect(connection_string) as connection, connection.cursor() as cursor:
                # Use parameterized queries instead of string concatenation
                query = """
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
                FP_PROGRES.[CANTIDAD_FP],
                FP_PROGRES.[FASE_PODUCC],
                FP_PROGRES.[PLANTA],
                FP_PROGRES.[COMENTARIES]
                FROM  
                    V_fp_pedidos 
                INNER JOIN
                    in_items ON V_fp_pedidos.[Codigo Producto] = in_items.itecodigo
                LEFT JOIN
                    FP_PROGRES ON V_fp_pedidos.OP = FP_PROGRES.orpconsecutivo -- Assuming 'Pedido' is the common column
                WHERE 
                    (V_fp_pedidos.eobnombre IN ('Por ejecutar', 'En ejecucion')) AND 
                    (in_items.itecompania = '01')
                AND (V_fp_pedidos.OP = ?);
                """

                # Execute the query with the entered ID as a parameter
                cursor.execute(query, entered_id)

                # Fetch all the data in one call
                data = cursor.fetchall()
                # Check if the OP exists in the FP_PROGRES table
                check_query = """
                SELECT COUNT(*) FROM FP_PROGRES WHERE orpconsecutivo = ?;
                """
                cursor.execute(check_query, entered_id)
                op_exists = cursor.fetchone()[0] > 0

                if not op_exists:
                    # If the OP doesn't exist, insert a new record with the OP
                    insert_query = """
                    INSERT INTO FP_PROGRES (orpconsecutivo) VALUES (?);
                    """
                    cursor.execute(insert_query, entered_id)
                    connection.commit()

        except pyodbc.Error as e:
            print(f"Error: {e}")
            messagebox.showerror(
                "Database Error", f"An error occurred while fetching data: {str(e)}")
            return

        # Check if data is found
        if data:
            # Cache the data for future use
            cache[entered_id] = data

            # Calculate the total pages
            self.total_pages = (len(data) - 1) // self.page_size + 1

            # Display the first page of data
            self.display_data(entered_id, self.page)

        else:
            print(f"No data found for the entered ID: {entered_id}")
            messagebox.showinfo(
                "No Data", f"No data found for the entered ID: {entered_id}.")

    def display_data(self, entered_id, page):
        app.geometry("1000x600")
        # Disable the fetch button and enable the update button after fetching data
        self.fetch_button.configure(state="normal")
        self.update_button.configure(state="normal")

        # Get the data from the cache
        data = cache[entered_id]

        # Get the subset of data for the current page
        start = (page - 1) * self.page_size
        end = min(start + self.page_size, len(data))
        page_data = data[start:end]

        # Use the custom_labels list to create labels for each field in the page data
        labels = [ctk.CTkLabel(self, text=f"{label}:")
                  for label in self.custom_labels]

        # Create entry widgets for editable fields and store them in self.data_entries
        self.data_entries = []
        for i, column_value in enumerate(page_data[0]):
            if i in [9, 10, 11, 12]:  # Indices of editable fields
                entry = ctk.CTkEntry(self, width=300)
                entry.insert(0, str(column_value))
                self.data_entries.append(entry)
            else:
                entry = ctk.CTkLabel(self, text=str(column_value), width=300)
                self.data_entries.append(entry)

        # Grid the labels and entries
        for i, (label, entry) in enumerate(zip(labels, self.data_entries)):
            label.grid(row=i + 2, column=0, padx=20)
            entry.grid(row=i + 2, column=1, padx=20)

        # Update the page label
        self.page_label.configure(
            text=f"Page {self.page} of {self.total_pages}")

    def update_data(self):
        # Get the updated values from the entry widgets
        updated_values = [entry.get() if isinstance(
            entry, ctk.CTkEntry) else entry.cget("text") for entry in self.data_entries]

        # Update the data in the cache
        entered_id = self.entry.get()
        cache[entered_id] = [tuple(updated_values)]

        # Update the data in the SQL database
        connection_string = 'DRIVER={SQL Server};SERVER=EQ040;DATABASE=ssf_genericos;UID=sa;PWD=Genericos0224'

        try:
            with pyodbc.connect(connection_string) as connection, connection.cursor() as cursor:
                # Use parameterized query to update the data
                update_query = """
                INSERT INTO FP_PROGRES (CANTIDAD_FP, FASE_PODUCC, PLANTA, COMENTARIES, orpconsecutivo)
            VALUES (?, ?, ?, ?, ?); 
                """

                # Execute the update query with the updated values and entered ID
                cursor.execute(
                    update_query, updated_values[9], updated_values[10], updated_values[11], updated_values[12], entered_id)

                # Commit the changes
                connection.commit()

            print(f"Data updated successfully for ID: {entered_id}")
            messagebox.showinfo(
                "Update Successful", f"Data updated successfully for ID: {entered_id}")

        except pyodbc.Error as e:
            print(f"Error: {e}")
            messagebox.showerror(
                "Database Error", f"An error occurred while updating data: {str(e)}")
        # Enable the fetch button, clear fields, and disable the update button after updating data
        self.reset_interface()

    def reset_interface(self):
        # Clear the entry field
        self.entry.delete(0, "end")

        # Reset pagination variables
        self.page = 1
        self.total_pages = 0
        self.page_label.configure(
            text=f"Page {self.page} of {self.total_pages}")

        # Clear the displayed data
        for widget in self.winfo_children():
            if widget not in self.essential_widgets and isinstance(widget, (ctk.CTkLabel, ctk.CTkEntry)):
                widget.destroy()

        # Clear the data entries list
        self.data_entries.clear()

        # Enable the fetch button and disable the update button
        self.fetch_button.configure(state="normal")
        self.update_button.configure(state="disabled")

    def prev_page(self):
        # Go to the previous page if possible
        if self.page > 1:
            self.page -= 1
            self.display_data(self.entry.get(), self.page)

    def next_page(self):
        # Go to the next page if possible
        if self.page < self.total_pages:
            self.page += 1
            self.display_data(self.entry.get(), self.page)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.my_frame = MyFrame(
            master=self, width=300, height=200, corner_radius=0)
        self.my_frame.grid(row=0, column=0, sticky="nsew")


app = App()
app.geometry("800x400")
app.mainloop()
