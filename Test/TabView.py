import customtkinter as ctk

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # create tabs
        self.add("tab 1")
        self.add("tab 2")
        
        # add widgets on tabs
        self.label1 = ctk.CTkLabel(master=self.tab("tab 1"), text="Tab 1")
        self.label1.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        self.label2 = ctk.CTkLabel(master=self.tab("tab 2"), text="Tab 2")
        self.label2.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        # set command for tab click
        self.command = self.on_tab_change
        
    def on_tab_change(self):
        # get the current tab name
        current_tab = self.get()
        print(f"Current tab: {current_tab}")

        # update label text on each tab
        self.label1.configure(text=f"Tab 1 (Current tab: {current_tab})")
        self.label2.configure(text=f"Tab 2 (Current tab: {current_tab})")

    def get_tab_name(self):
        return self.get()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.tab_view = MyTabView(master=self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    
app = App()
app.mainloop()
