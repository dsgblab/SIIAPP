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
