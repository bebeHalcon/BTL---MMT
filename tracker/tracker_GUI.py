import tkinter as tk
from tkinter import scrolledtext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GUI_redirector import GUI_Redirector

class Tracker_GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Transfer Tracker")
        self.geometry("600x400")

        label_app = tk.Label(self, text="File-sharing application", font=("Arial", 16, "bold"), fg="blue", bg="#F0F0F0")
        label_app.pack(side=tk.TOP, pady=10)
        label_side = tk.Label(self, text="Tracker side", font=("Arial", 16, "bold"), fg="blue", bg="#F0F0F0")
        label_side.pack(side=tk.TOP)

        button_frame = tk.Frame(self, bg="#D0D0D0")
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # Configure columns to have equal weight for justified alignment
        for i in range(5):  # 5 buttons: Help, List, Update, Clear, Quit
            button_frame.grid_columnconfigure(i, weight=1)

        button_help = tk.Button(button_frame, text="Help", command=self.button_help_action, bg="#90EE90")
        button_help.grid(row=0, column=0, padx=5, pady=5)

        button_list = tk.Button(button_frame, text="List", command=self.button_list_action, bg="#90EE90")
        button_list.grid(row=0, column=1, padx=5, pady=5)

        button_update = tk.Button(button_frame, text="Update", command=self.button_update_action, bg="#FFD700")
        button_update.grid(row=0, column=2, padx=5, pady=5)

        button_clear = tk.Button(button_frame, text="Clear", command=self.clear_console, bg="#87CEEB")
        button_clear.grid(row=0, column=3, padx=5, pady=5)

        button_quit = tk.Button(button_frame, text="Quit", command=self.quit_action, bg="#FF6347")
        button_quit.grid(row=0, column=4, padx=5, pady=5)

        console_frame = tk.Frame(self, bg="#F0F0F0")
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=("Arial", 12), bg="#F0F0F0", fg="#333333")
        self.console_text.pack(fill=tk.BOTH, expand=True)

        self.console_text.insert(tk.END, ''' Welcome to file transferring application! 
 This is the TRACKER side!
''')

        sys.stdout = GUI_Redirector(self.console_text)

        self.console_text.tag_configure("red", foreground="red")
        self.console_text.tag_configure("blue", foreground="blue")
        self.console_text.tag_configure("black", foreground="black")
        self.console_text.config(state=tk.DISABLED)

    def button_help_action(self):
        self.print_message("Help\n", "blue")
        self.print_message('''list - List all peer with files
update - Update files in local repository of all peers
quit - Shut down tracker socket, use this command before closing the terminal\n
''', "black")
        self.console_text.mark_set('insert', tk.END)
        
    def button_list_action(self):
        self.print_message("list\n", "blue")
        self.call_action()

    def button_update_action(self):
        self.print_message("update\n", "blue")
        self.call_action()

    def quit_action(self):
        self.print_message("quit\n", "blue")
        self.call_action()

    def print_message(self, msg: str, color="black"):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, msg, color)
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

    def call_action(self):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.event_generate("<Return>")
        self.console_text.config(state=tk.DISABLED)
        self.console_text.mark_set('insert', tk.END)

    def get_command(self):
        return self.console_text.get("end-2l", "end-1c")
    
    def clear_console(self):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state=tk.DISABLED)

    def update_file_list(self, peers):
        self.print_message("Updated peer file list:\n", "blue")
        i = 1
        for peer in peers:
            files = [file_info[0] for file_info in peers[peer]['peer_files']]
            self.print_message(f"{i}. {peer}: {files}\n", "black")
            i += 1
        self.console_text.mark_set('insert', tk.END)