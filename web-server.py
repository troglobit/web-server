"""
Simple web server with a user friendly GUI

Copyright (c) 2024  Joachim Wiberg <troglobit@gmail.com>

Available as Open Source software under the MIT Licenese.
"""
import os
import socket
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import psutil

class ThreadedTCPServer(TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.daemon_threads = True

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Suppress logging to the console

def get_interfaces():
    interfaces = psutil.net_if_addrs()
    interface_list = []
    for interface in interfaces:
        for addr in interfaces[interface]:
            if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                interface_list.append((interface, addr.address))
                break
    return interface_list

def select_default_interface():
    interfaces = get_interfaces()
    ethernet_patterns = ["eth", "en", "local area connection"]

    for interface, ip in interfaces:
        interface_lower = interface.lower()
        if any(pattern in interface_lower for pattern in ethernet_patterns):
            return interface, ip
    return interfaces[0] if interfaces else (None, None)

def start_server(ip, port, directory):
    os.chdir(directory)
    server_address = (ip, port)
    httpd = ThreadedTCPServer(server_address, Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd, server_address

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Web Server")
        self.geometry("340x300")
        self.resizable(False, False)  # Set fixed window size

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.main_frame, text="Web Server",
                                  font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        self.interface_frame = ctk.CTkFrame(self.main_frame)
        self.interface_frame.pack(pady=10)

        self.interface_var = tk.StringVar()
        self.interface_menu = ctk.CTkOptionMenu(self.interface_frame,
                                                variable=self.interface_var,
                                                width=220)
        self.interface_menu.pack(side="left", padx=3)
        self.update_interface_menu()

        self.port_entry = ctk.CTkEntry(self.interface_frame, width=60)
        self.port_entry.pack(side="left", padx=3)
        self.port_entry.insert(0, "8080")

        self.directory_frame = ctk.CTkFrame(self.main_frame)
        self.directory_frame.pack(pady=10)

        self.directory_var = tk.StringVar()
        self.directory_var.set(os.getcwd())
        self.directory_label = ctk.CTkLabel(self.directory_frame,
                                            textvariable=self.directory_var,
                                            anchor="w", width=260)
        self.directory_label.pack(side="left", padx=3)
        self.directory_menu = ctk.CTkButton(self.directory_frame, text="..",
                                            command=self.select_directory,
                                            width=20)
        self.directory_menu.pack(side="left", padx=3)

        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.button_frame, text="Start Server",
                                          command=self.start_server, width=140)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(self.button_frame, text="Stop Server",
                                         command=self.stop_server, width=140,
                                         state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)

        self.status_frame = ctk.CTkFrame(self.main_frame, border_color="grey",
                                         border_width=1, width=260)
        self.status_frame.pack(pady=20, padx=12, fill="x")

        self.status_label = ctk.CTkLabel(self.status_frame,
                                         text="Server not running.",
                                         anchor="w")
        self.status_label.pack(pady=2, padx=3, anchor="w")

        self.server = None
        self.server_address = None

    def update_interface_menu(self):
        interfaces = get_interfaces()
        if interfaces:
            self.interface_menu.configure(values=[f"{name} ({ip})" for name, ip in interfaces])
            default_interface, default_ip = select_default_interface()
            if default_interface:
                self.interface_var.set(f"{default_interface} ({default_ip})")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_var.set(directory)

    def start_server(self):
        selected = self.interface_var.get()
        ip = selected.split('(')[-1].strip(')')
        port = self.port_entry.get()
        if not port.isdigit():
            self.status_label.configure(text="Invalid port number!")
            return
        port = int(port)
        directory = self.directory_var.get()
        if not directory:
            self.status_label.configure(text="No directory selected!")
            return
        self.server, self.server_address = start_server(ip, port, directory)
        self.status_label.configure(text=f"Server running at {self.server_address[0]}:{self.server_address[1]}")
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.status_label.configure(text="Server stopped.")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)

if __name__ == "__main__":
    app = App()
    app.mainloop()
