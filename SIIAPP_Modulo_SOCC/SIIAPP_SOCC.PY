import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import pyodbc
from tksheet import Sheet
import sys
import os
from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import logging

logging.basicConfig(filename='auth.log', level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create Tksheet widget
        self.sheet = Sheet(self)
        self.sheet.pack(fill="both", expand=True)

        # Configure column headers
        headers = [
            "UID",
            "# OC",
            "CODIGO ITEM",
            "DESCRIPCION ITEM",
            "NIT PROVEEDOR",
            "DESCRIPCION PROVEEDOR",
            "UNIDADES PEDIDAS",
            "VALOR NETO",
            "FECHA COMPROMETIDA",
            "FECHA REQUERIDA",
            "ESTADO OC",
            "ESTADO SEGUIMIENTO",
            "COMENTARIOS"
        ]
        self.sheet.headers(headers)

        # Enable row selection
        self.sheet.enable_bindings(("single_select", "row_select","arrowkeys"))

        # Create a scrollable frame
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Create filter entry
        self.filter_entry = ctk.CTkEntry(
            self.scrollable_frame, placeholder_text="Buscar por # OC, CODIGO ITEM, ITEM, NIT, PROVEEDOR")
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

        self.hot_reload_button = ctk.CTkButton(
            self.button_frame, text="Refrescar", command=self.reload_data)
        self.hot_reload_button.pack(side="left", padx=5)

        # Load data from the database
        self.load_data()

    def load_data(self):
        try:
            # Connect to the database
            conn_str = (
                f"DRIVER={os.getenv('DB1_DRIVER')};"
                f"SERVER={os.getenv('DB1_SERVER')};"
                f"DATABASE={os.getenv('DB1_DATABASE')};"
                f"UID={os.getenv('DB1_UID')};"
                f"PWD={os.getenv('DB1_PWD')}"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Fetch data from the database using parameterized query
            query = """
                SELECT
                   vw_in_ordeabasdeta_with_uid.UID
                  ,vw_in_ordeabasdeta_with_uid.[# OC]
                  ,vw_in_ordeabasdeta_with_uid.[CODIGO ITEM]
                  ,vw_in_ordeabasdeta_with_uid.[DESCRIPCION ITEM]
                  ,vw_in_ordeabasdeta_with_uid.[NIT PROVEEDOR]
                  ,vw_in_ordeabasdeta_with_uid.[DESCRIPCION PROVEEDOR]
                  ,vw_in_ordeabasdeta_with_uid.[UNIDADES PEDIDAS]
                  ,vw_in_ordeabasdeta_with_uid.[VALOR NETO]
                  ,vw_in_ordeabasdeta_with_uid.[FECHA COMPROMETIDA]
                  ,vw_in_ordeabasdeta_with_uid.[FECHA REQUERIDA]
                  ,vw_in_ordeabasdeta_with_uid.[ESTADO OC]
                  ,CON_SEG_OC.OCFSTATE
                  ,CON_SEG_OC.COMMENTS
                  FROM dbo.vw_in_ordeabasdeta_with_uid
                  LEFT OUTER JOIN dbo.CON_SEG_OC
                    ON vw_in_ordeabasdeta_with_uid.UID = CON_SEG_OC.UID COLLATE Latin1_General_CI_AS
                  ORDER BY vw_in_ordeabasdeta_with_uid.[# OC]
            """
            cursor.execute(query)
            data = cursor.fetchall()

            # Insert data into the Tksheet
            formatted_data = [
                [str(value) if value is not None else "" for value in row]
                for row in data
            ]

            self.original_data = formatted_data
            self.sheet.set_sheet_data(formatted_data)

            # Configure column widths
            self.column_widths = [0, 140, 120, 500, 120, 500, 120, 120, 140, 140, 120, 160, 600]

            for i, width in enumerate(self.column_widths):
                self.sheet.column_width(column=i, width=width)

        except pyodbc.Error as e:
            print(f"An error occurred while loading data: {str(e)}", file=sys.stderr)
        finally:
            # Close the database connection and cursor
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def filter_data(self, event):
        self.column_widths = [0, 140, 120, 500, 120, 500, 120, 120, 140, 140, 120, 160, 600]
        search_text = self.filter_entry.get().lower()
        if search_text:
            filtered_data = [
                row for row in self.original_data
                if search_text in str(row[1]).lower() or  # Search by "# OC"
                   search_text in str(row[2]).lower() or  # Search by "CODIGO ITEM"
                   search_text in str(row[4]).lower() or  # Search by "NIT PROVEEDOR"
                   search_text in str(row[3]).lower() or  # Search by "DESCRIPCION ITEM"
                   search_text in str(row[5]).lower()     # Search by "DESCRIPCION PROVEEDOR"
            ]
            self.sheet.set_sheet_data(filtered_data)
            for i, width in enumerate(self.column_widths):
                self.sheet.column_width(column=i, width=width)
        else:
            self.sheet.set_sheet_data(self.original_data)
            for i, width in enumerate(self.column_widths):
                self.sheet.column_width(column=i, width=width)
    def create_child_record(self):
        selected_rows = self.sheet.get_selected_rows()
        if selected_rows:
            # Get the first selected row
            selected_row = next(iter(selected_rows))
            row_data = self.sheet.get_row_data(selected_row)
            uid_value = row_data[0]  # Assuming 'UID' is at index 0
            try:
                conn_str = (
                    f"DRIVER={os.getenv('DB1_DRIVER')};"
                    f"SERVER={os.getenv('DB1_SERVER')};"
                    f"DATABASE={os.getenv('DB1_DATABASE')};"
                    f"UID={os.getenv('DB1_UID')};"
                    f"PWD={os.getenv('DB1_PWD')}"
                )
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()

                check_query = "SELECT COUNT(*) FROM CON_SEG_OC WHERE UID = ?"
                cursor.execute(check_query, uid_value)
                count = cursor.fetchone()[0]

                if count > 0:
                    messagebox.showerror("Error", "Ya existe un registro con este UID.")
                    return

            except pyodbc.Error as e:
                print(f"An error occurred while checking for existing UID: {str(e)}", file=sys.stderr)
                return
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                    
            # Create a new window for entering child record data
            child_window = ctk.CTkToplevel(self)
            child_window.title("Crear Registro de Seguimiento")

            # Add input fields for child record data
            ocfstate_entry = ctk.CTkEntry(child_window, placeholder_text="Estado de Seguimiento")
            comments_entry = ctk.CTkTextbox(child_window, height=50, width=200)
            comments_entry.configure(border_color='blue', border_width=0.5)

            # Grid view
            ocfstate_label = ctk.CTkLabel(child_window, text="Estado de Seguimiento:")
            ocfstate_label.grid(row=0, column=0, padx=5, pady=5)
            ocfstate_entry.grid(row=0, column=1, padx=5, pady=5)

            comments_label = ctk.CTkLabel(child_window, text="Comentarios:")
            comments_label.grid(row=1, column=0, padx=5, pady=5)
            comments_entry.grid(row=1, column=1, padx=5, pady=5)

            def save_child_record():
                ocfstate = ocfstate_entry.get()
                comments = comments_entry.get("0.0", "end")

                if not ocfstate:
                    messagebox.showerror("Error", "Por favor, ingrese el estado de seguimiento antes de guardar el registro.")
                    child_window.destroy()
                    return

                try:
                    # Insert the child record into the database using parameterized query
                    conn_str = (
                        f"DRIVER={os.getenv('DB1_DRIVER')};"
                        f"SERVER={os.getenv('DB1_SERVER')};"
                        f"DATABASE={os.getenv('DB1_DATABASE')};"
                        f"UID={os.getenv('DB1_UID')};"
                        f"PWD={os.getenv('DB1_PWD')}"
                    )
                    conn = pyodbc.connect(conn_str)
                    cursor = conn.cursor()

                    insert_query = """
                        INSERT INTO CON_SEG_OC (UID, OCFSTATE, COMMENTS)
                        VALUES (?, ?, ?)
                    """
                    params = (uid_value, ocfstate, comments)
                    cursor.execute(insert_query, params)
                    conn.commit()

                except pyodbc.Error as e:
                    print(f"An error occurred while saving child record: {str(e)}", file=sys.stderr)
                finally:
                    # Close the database connection and cursor
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()

                child_window.destroy()
                self.reload_data()

            save_button = ctk.CTkButton(child_window, text="Guardar", command=save_child_record)
            save_button.grid(row=2, column=0, columnspan=2, pady=10)
        else:
            messagebox.showinfo("Sin seleccion", "Porfavor eliga una fila para Crear un registro")
    def edit_child_record(self):
        selected_rows = self.sheet.get_selected_rows()
        if selected_rows:
            # Get the first selected row
            selected_row = next(iter(selected_rows))
            row_data = self.sheet.get_row_data(selected_row)
            uid_value = row_data[0]  # Assuming 'UID' is at index 0

            # Create a new window for editing child record data
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Editar Registro de Seguimiento")

            # Add input fields for child record data
            ocfstate_entry = ctk.CTkEntry(edit_window, placeholder_text="Estado de Seguimiento")
            ocfstate_entry.insert(0, row_data[11])  # Pre-fill with existing data
            comments_entry = ctk.CTkTextbox(edit_window, height=50, width=200)
            comments_entry.insert("0.0", row_data[12])  # Pre-fill with existing data
            comments_entry.configure(border_color='blue', border_width=0.5)

            # Grid view
            ocfstate_label = ctk.CTkLabel(edit_window, text="Estado de Seguimiento:")
            ocfstate_label.grid(row=0, column=0, padx=5, pady=5)
            ocfstate_entry.grid(row=0, column=1, padx=5, pady=5)

            comments_label = ctk.CTkLabel(edit_window, text="Comentarios:")
            comments_label.grid(row=1, column=0, padx=5, pady=5)
            comments_entry.grid(row=1, column=1, padx=5, pady=5)

            def save_edited_child_record():
                ocfstate = ocfstate_entry.get()
                comments = comments_entry.get("0.0", "end")

                try:
                    # Update the child record in the database using parameterized query
                    conn_str = (
                        f"DRIVER={os.getenv('DB1_DRIVER')};"
                        f"SERVER={os.getenv('DB1_SERVER')};"
                        f"DATABASE={os.getenv('DB1_DATABASE')};"
                        f"UID={os.getenv('DB1_UID')};"
                        f"PWD={os.getenv('DB1_PWD')}"
                    )
                    conn = pyodbc.connect(conn_str)
                    cursor = conn.cursor()

                    update_query = """
                        UPDATE CON_SEG_OC
                        SET OCFSTATE = ?, COMMENTS = ?
                        WHERE UID = ?
                    """
                    params = (ocfstate, comments, uid_value)
                    cursor.execute(update_query, params)
                    conn.commit()

                except pyodbc.Error as e:
                    print(f"An error occurred while updating child record: {str(e)}", file=sys.stderr)
                finally:
                    # Close the database connection and cursor
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()

                edit_window.destroy()
                self.reload_data()

            save_button = ctk.CTkButton(edit_window, text="Guardar Cambios", command=save_edited_child_record)
            save_button.grid(row=2, column=0, columnspan=2, pady=10)
        else:
            messagebox.showinfo("Sin seleccion", "Porfavor eliga una fila para editar un registro")


    def reload_data(self):
        # Clear existing data
        self.sheet.set_sheet_data([])

        # Load updated data from the database
        self.load_data()

# AD settings
AD_SERVER = os.getenv('AD_SERVER')
AD_DOMAIN = os.getenv('AD_DOMAIN')
AD_USER = os.getenv('AD_USER')
AD_PASSWORD = os.getenv('AD_PASSWORD')
ALLOWED_GROUPS = os.getenv('ALLOWED_GROUPS')
ALLOWED_USERS = os.getenv('ALLOWED_USERS')

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        self.login_button = ctk.CTkButton(self, text="Login", command=self.authenticate)
        self.login_button.pack(pady=10)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if authenticate_user(username, password):
            messagebox.showinfo("Login Successful", "Welcome!")
            self.master.show_app_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or access denied.")

def authenticate_user(username, password):
    server = Server(os.getenv('AD_SERVER'), get_info=ALL)
    user = f'{os.getenv("AD_DOMAIN")}\\{username}'
    
    try:
        conn = Connection(server, user=user, password=password, authentication='NTLM', auto_bind=True)
        logging.info(f"LDAP bind successful for {username}.")

        # Check if user is in allowed users
        allowed_users = os.getenv('ALLOWED_USERS').split(',')
        if username in allowed_users:
            return True
        
        # Search base is set to the root of the domain
        search_base = f'DC={AD_DOMAIN.replace(".", ",DC=")}'
        
        conn.search(
            search_base,
            f'(sAMAccountName={username})',
            attributes=['memberOf'],
            search_scope=SUBTREE
        )
        
        if not conn.entries:
            logging.warning(f"User {username} not found in LDAP search.")
            return False

        user_groups = [entry.memberOf.values if isinstance(entry.memberOf, list) else [entry.memberOf] for entry in conn.entries]
        user_groups = [item for sublist in user_groups for item in sublist]

        allowed_groups = os.getenv('ALLOWED_GROUPS').split(',')

        for group in allowed_groups:
            if any(group in str(user_group) for user_group in user_groups):
                return True

    except Exception as e:
        logging.error(f"LDAP error for {username}: {e}")

    logging.warning(f"Access denied for {username}.")
    return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x400")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.login_frame = LoginFrame(master=self)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def show_app_frame(self):
        self.login_frame.destroy()
        self.geometry("1000x600")
        self.my_frame = MyFrame(master=self)
        self.my_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

app = App()
app.title("SIIAPP SEGUIMIENTO OC")
app.mainloop()