import tkinter as tk
from tkinter import scrolledtext, filedialog
import sys
import os
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GUI_redirector import GUI_Redirector

class Peer_GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Transfer Peer")
        self.geometry("600x400")

        label_app = tk.Label(self, text="File-sharing application", font=("Arial", 16, "bold"), fg="blue", bg="#F0F0F0")
        label_app.pack(side=tk.TOP, pady=10)
        label_side = tk.Label(self, text="Peer side", font=("Arial", 16, "bold"), fg="blue", bg="#F0F0F0")
        label_side.pack(side=tk.TOP, pady=10)

        self.button_frame = tk.Frame(self, bg="#D0D0D0")
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # First row: Use a nested Frame with pack for justified alignment
        first_row_frame = tk.Frame(self.button_frame, bg="#D0D0D0")
        first_row_frame.grid(row=0, column=0, columnspan=6, sticky="ew")

        button_help = tk.Button(first_row_frame, text="Help", command=self.button_help_action, bg="#90EE90")
        button_help.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)

        button_list = tk.Button(first_row_frame, text="List", command=self.button_list_action, bg="#90EE90")
        button_list.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)

        button_publish = tk.Button(first_row_frame, text="Publish", command=self.button_publish_action, bg="#FFD700")
        button_publish.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)

        button_upload = tk.Button(first_row_frame, text="Upload", command=self.button_upload_action, bg="#FFA500")
        button_upload.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)
        
        button_clear = tk.Button(first_row_frame, text="Clear", command=self.clear_console, bg="#87CEEB")
        button_clear.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)

        button_quit = tk.Button(first_row_frame, text="Quit", command=self.quit_action, bg="#FF6347")
        button_quit.pack(side=tk.LEFT, expand=True, fill=tk.NONE, padx=5, pady=5)

        # Fetch row: 1 button + 1 entry field (unchanged)
        self.button_frame.grid_columnconfigure(0, weight=1)  # Button column
        self.button_frame.grid_columnconfigure(1, weight=5)  # Entry field column
        button_fetch = tk.Button(self.button_frame, text="Fetch", command=self.button_fetch_action, bg="#FFD700")
        button_fetch.grid(row=1, column=0, padx=5, pady=5)
        self.entry_fetch = tk.Entry(self.button_frame)
        self.entry_fetch.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # History row: 1 button + 1 entry field (unchanged)
        self.button_frame.grid_columnconfigure(0, weight=1)  # Button column
        self.button_frame.grid_columnconfigure(1, weight=5)  # Entry field column
        button_history = tk.Button(self.button_frame, text="History", command=self.button_history_action, bg="#FFD700")
        button_history.grid(row=2, column=0, padx=5, pady=5)
        self.entry_history = tk.Entry(self.button_frame)
        self.entry_history.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Reset row: 1 button + 2 entry fields (unchanged)
        self.button_frame.grid_columnconfigure(0, weight=1)  # Button column
        self.button_frame.grid_columnconfigure(1, weight=3)  # First entry field column
        self.button_frame.grid_columnconfigure(2, weight=2)  # Second entry field column
        button_reset = tk.Button(self.button_frame, text="Reset", command=self.button_reset_action, bg="#FFD700")
        button_reset.grid(row=3, column=0, padx=5, pady=5)
        self.entry_reset_file = tk.Entry(self.button_frame)
        self.entry_reset_file.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.entry_reset_version = tk.Entry(self.button_frame)
        self.entry_reset_version.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        # Block/Unblock row: 2 buttons + 2 entry fields (unchanged)
        button_block = tk.Button(self.button_frame, text="Block", command=self.button_block_action, bg="#FFD700")
        button_block.grid(row=4, column=0, padx=5, pady=5)
        button_unblock = tk.Button(self.button_frame, text="Unblock", command=self.button_unblock_action, bg="#FFD700")
        button_unblock.grid(row=4, column=1, padx=5, pady=5)
        self.entry_block_ip = tk.Entry(self.button_frame)
        self.entry_block_ip.grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="ew")
        self.entry_block_port = tk.Entry(self.button_frame)
        self.entry_block_port.grid(row=4, column=4, columnspan=2, padx=5, pady=5, sticky="ew")

        console_frame = tk.Frame(self, bg="#F0F0F0")
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=("Arial", 12), bg="#F0F0F0", fg="#333333")
        self.console_text.pack(fill=tk.BOTH, expand=True)

        self.console_text.insert(tk.END, ''' Welcome to file transferring application! 
 This is the PEER side!
''')

        sys.stdout = GUI_Redirector(self.console_text)

        self.console_text.tag_configure("red", foreground="red")
        self.console_text.tag_configure("blue", foreground="blue")
        self.console_text.tag_configure("black", foreground="black")
        self.console_text.config(state=tk.DISABLED)

        self.option_buttons = []

    def button_help_action(self):
        self.print_message("Help\n", "blue")
        self.print_message('''list - List all peers in the application
publish - Send information of all files to tracker
upload - Upload a file to the local directory
fetch fname - Send a fetch request to tracker to fetch file with name at fname
history fname - Get all the history version of a file
reset fname version - Get the data of a file in a specific version
block/unblock peer - Block/Unblock a peer
quit - Shut down peer socket.\n
''', "black")
        self.console_text.mark_set('insert', tk.END)

    def button_publish_action(self):
        self.print_message("publish\n", "blue")
        self.call_action()

    def button_list_action(self):
        self.print_message("list\n", "blue")
        self.call_action()

    def button_fetch_action(self):
        entry_fetch_text = self.entry_fetch.get()
        if entry_fetch_text == "":
            self.print_message("fetch: Please enter a file name!\n", "red")
            self.console_text.mark_set('insert', tk.END)
        else:
            self.print_message("fetch " + entry_fetch_text + "\n", "blue")
            self.call_action()

    def button_history_action(self):
        entry_history_text = self.entry_history.get()
        if entry_history_text == "":
            self.print_message("fetch: Please enter a file name!\n", "red")
            self.console_text.mark_set('insert', tk.END)
        else:
            self.print_message("history " + entry_history_text + "\n", "blue")
            self.call_action()

    def button_reset_action(self):
        entry_reset_file = self.entry_reset_file.get()
        entry_reset_version = self.entry_reset_version.get()
        if entry_reset_file == "" and entry_reset_version == "":
            self.print_message("fetch: Please enter a file name and a version!\n", "red")
            self.console_text.mark_set('insert', tk.END)
        else:
            self.print_message("reset " + entry_reset_file + " " + entry_reset_version + "\n", "blue")
            self.call_action()

    def button_block_action(self):
        entry_block_ip_text = self.entry_block_ip.get()
        entry_block_port_text = self.entry_block_port.get()
        if entry_block_ip_text == "" and entry_block_port_text == "":
            self.print_message("fetch: Please enter a peer address!\n", "red")
            self.console_text.mark_set('insert', tk.END)
        else:
            self.print_message("block " + entry_block_ip_text + " " + entry_block_port_text + "\n", "blue")
            self.call_action()

    def button_unblock_action(self):
        entry_block_ip_text = self.entry_block_ip.get()
        entry_block_port_text = self.entry_block_port.get()
        if entry_block_ip_text == "" and entry_block_port_text == "":
            self.print_message("fetch: Please enter a peer address!\n", "red")
            self.console_text.mark_set('insert', tk.END)
        else:
            self.print_message("unblock " + entry_block_ip_text + " " + entry_block_port_text + "\n", "blue")
            self.call_action()

    def button_upload_action(self):
        file_path = filedialog.askopenfilename(
            title="Select a file to upload",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            try:
                local_dir = os.path.join(os.path.dirname(__file__), "local")
                os.makedirs(local_dir, exist_ok=True)
                dest_path = os.path.join(local_dir, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                self.print_message(f"File '{os.path.basename(file_path)}' uploaded to local directory.\n", "blue")
                self.button_publish_action()
            except Exception as e:
                self.print_message(f"Error uploading file: {e}\n", "red")
        else:
            self.print_message("No file selected.\n", "black")

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

    def fetch_options(self, num_options):
        self.option_buttons = []
        for i in range(num_options):
            button = tk.Button(
                self.button_frame, text=f"Option {i+1}", 
                command=lambda i=i: self._option_action(i), bg="#ADD8E6"
            )
            button.grid(row=1, column=2 + i, padx=5, pady=5)
            self.option_buttons.append(button)

    def _option_action(self, index):
        self.print_message(f"Option {index+1} selected\n")
        for button in self.option_buttons:
            button.destroy()
        self.option_buttons = []
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, str(index + 1) + "\n")
        self.console_text.config(state=tk.DISABLED)
        self.call_action()