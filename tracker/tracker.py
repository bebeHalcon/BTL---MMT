import socket
import os
import pickle
import threading
import time
from tracker_GUI import Tracker_GUI
import tkinter as tk
from collections import defaultdict

# Helper functions for reliable socket communication
def recv_full_message(socket, chunk_size=1024):
    try:
        length_data = socket.recv(4)  # Receive message length (4 bytes)
        if not length_data:
            return None
        msg_length = int.from_bytes(length_data, byteorder='big')
        chunks = []
        bytes_received = 0
        while bytes_received < msg_length:
            chunk = socket.recv(min(chunk_size, msg_length - bytes_received))
            if not chunk:
                return None
            chunks.append(chunk)
            bytes_received += len(chunk)
        return pickle.loads(b''.join(chunks))
    except Exception as e:
        print(f"recv_full_message error: {e}")
        return None

def send_full_message(socket, message):
    try:
        data = pickle.dumps(message)
        msg_length = len(data)
        socket.send(msg_length.to_bytes(4, byteorder='big'))  # Send message length
        socket.send(data)
    except Exception as e:
        print(f"send_full_message error: {e}")
        raise

class Tracker:
    def __init__(self) -> None:
        self.peers = {}
        self.block_dict = defaultdict(list)

    def peer_handler(self, peer_socket: socket.socket, peer_addr, tracker_gui: Tracker_GUI):
        while True:
            try:
                msg = recv_full_message(peer_socket)
                if msg is None:
                    print(f"Connection lost with peer {peer_addr}")
                    break
                msg_type = msg['type']
                msg_data = msg['data']
                if msg_type == "update_result":
                    self.peers[peer_addr]['peer_files'] = msg_data
                    self.peers[peer_addr]['peer_history'].append(msg_data.copy())
                    files = [file_name for file_name, _, _ in msg_data]
                    tracker_gui.print_message(f"Updated files on {peer_addr}: {files}\n\n")
                elif msg_type == "fetch":
                    file_name = msg_data
                    file_hash = None
                    for i in range(len(self.peers[peer_addr]['peer_files'])):
                        if self.peers[peer_addr]['peer_files'][i][0] == file_name:
                            file_hash = self.peers[peer_addr]['peer_files'][i][2]
                            break
                    peers_has_file = []
                    peer_addr_tuple = peer_addr.split(':')
                    peer_addr_tuple = (peer_addr_tuple[0], int(peer_addr_tuple[1]))
                    for peer in self.peers:
                        if peer_addr_tuple in self.block_dict[peer]:
                            continue
                        if any(file_name == file[0] and file_hash != file[2] for file in self.peers[peer]['peer_files']):
                            peers_has_file.append(self.peers[peer]['peer_address'])
                    send_full_message(peer_socket, {
                        'type': 'fetch_result',
                        'data': peers_has_file,
                    })
                elif msg_type == "list":
                    peer_list = []
                    for peer in self.peers:
                        peer_list.append(self.peers[peer]['peer_address'])
                    send_full_message(peer_socket, {
                        'type': 'list_result',
                        'data': peer_list,
                    })
                elif msg_type == "publish":
                    status = True
                    self.peers[peer_addr]['peer_files'] = msg_data
                    self.peers[peer_addr]['peer_history'].append(self.peers[peer_addr]['peer_files'].copy())
                    send_full_message(peer_socket, {
                        'type': 'publish_result',
                        'data': status,
                    })
                elif msg_type == "history":
                    file_name = msg_data
                    file_history = []
                    for history in self.peers[peer_addr]['peer_history']:
                        for i in range(len(history)):
                            if history[i][0] == file_name:
                                file_history.append(history[i])
                    send_full_message(peer_socket, {
                        'type': 'history_result',
                        'data': file_history,
                    })
                elif msg_type == "reset":
                    file_name = msg_data[0]
                    file_version = int(msg_data[1])
                    file_data_encoded = None
                    temp = self.peers[peer_addr]['peer_history'][file_version]
                    for i in range(len(temp)):
                        if temp[i][0] == file_name:
                            file_data_encoded = temp[i][2]
                    send_full_message(peer_socket, {
                        'type': 'reset_result',
                        'data': (file_name, file_data_encoded),
                    })
                elif msg_type == "block":
                    peer_ip = msg_data[0]
                    peer_port = msg_data[1]
                    status = None
                    if f"{peer_ip}:{peer_port}" in self.peers:
                        self.block_dict[peer_addr].append((peer_ip, peer_port))
                        status = (peer_ip, peer_port)
                    send_full_message(peer_socket, {
                        'type': 'block_result',
                        'data': status,
                    })
                elif msg_type == "unblock":
                    peer_ip = msg_data[0]
                    peer_port = msg_data[1]
                    status = None
                    if f"{peer_ip}:{peer_port}" in self.peers and \
                        (peer_ip, peer_port) in self.block_dict[peer_addr]:
                        self.block_dict[peer_addr].remove((peer_ip, peer_port))
                        status = (peer_ip, peer_port)
                    send_full_message(peer_socket, {
                        'type': 'unblock_result',
                        'data': status,
                    })
                elif msg_type == "quit":
                    self.peers.pop(peer_addr)
                    peer_socket.close()
                    break
                else:
                    continue
            except Exception as e:
                print(f"peer_handler stop for {peer_addr}: {e}")
                break
        if peer_addr in self.peers:
            self.peers.pop(peer_addr)
        try:
            peer_socket.close()
        except Exception:
            pass

    def command_handler(self, tracker_socket: socket.socket, tracker_gui: Tracker_GUI):
        def quit_command():
            tracker_gui.print_message("Closing tracker socket!\n")
            for peer in list(self.peers.keys()):
                try:
                    send_full_message(self.peers[peer]['peer_socket_object'], {
                        'type': 'quit',
                        'data': None,
                    })
                    self.peers[peer]['peer_socket_object'].close()
                except Exception:
                    pass
            tracker_socket.close()
            tracker_gui.quit()

        def update_command(peer_addr):
            peer_socket = self.peers[peer_addr]['peer_socket_object']
            tracker_gui.print_message(f"Updating {peer_addr}...\n")
            try:
                send_full_message(peer_socket, {
                    'type': 'update',
                    'data': None,
                })
            except Exception as e:
                tracker_gui.print_message(f"Error updating {peer_addr}: {e}\n\n")

        command = tracker_gui.get_command()
        args_list = command.split()
        print_str = ""
        if args_list[0] == "list":
            if len(args_list) == 1:
                i = 1
                if len(self.peers) > 0:
                    for peer in self.peers:
                        files = []
                        for file_name, _, _ in self.peers[peer]['peer_files']:
                            files.append(file_name)
                        print_str += f"{i}. {peer}: {files}\n"
                        i += 1
                else:
                    print_str = "There is no peer."
                tracker_gui.print_message(f"{print_str}\n")
            else:
                tracker_gui.print_message("Not a valid command!\nlist requires no arguments\n")
        elif args_list[0] == "update":
            if len(self.peers) == 0:
                tracker_gui.print_message("No peers to update.\n\n")
            else:
                for peer_addr in list(self.peers.keys()):
                    update_command(peer_addr)
        elif args_list[0] == "quit":
            quit_command()
            return "break"
        else:
            tracker_gui.print_message("Not a valid command!\n\n")
        return "break"

    def peer_listener(self, tracker_socket: socket.socket, tracker_gui: Tracker_GUI):
        while True:
            try:
                peer_socket, peer_addr = tracker_socket.accept()
                msg = recv_full_message(peer_socket)
                if msg is None:
                    peer_socket.close()
                    continue
                msg_type = msg['type']
                msg_data = msg['data']
                if msg_type == 'connect':
                    send_full_message(peer_socket, {
                        'type': 'connect_result',
                        'data': peer_addr,
                    })
                    files = []
                    for file_name, _, _ in msg_data:
                        files.append(file_name)
                    tracker_gui.print_message(f"Accepted connection from {peer_addr[0]}:{peer_addr[1]} with these files: {files}\n\n")
                    peer_key = f"{peer_addr[0]}:{peer_addr[1]}"
                    self.peers[peer_key] = {
                        "peer_socket_object": peer_socket,
                        "peer_address": peer_addr,
                        "peer_files": msg_data,
                        "peer_history": [msg_data.copy()],
                    }
                    threading.Thread(target=self.peer_handler, args=[peer_socket, peer_key, tracker_gui]).start()
            except Exception as e:
                tracker_gui.print_message(f"peer_listener stop: {e}\n\n")
                return

    def main(self):
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_ip = "localhost"
        tracker_port = 65434
        tracker_socket.bind((tracker_ip, tracker_port))
        tracker_socket.listen(5)

        tracker_gui = Tracker_GUI()
        tracker_gui.title("Tracker terminal")
        tracker_gui.bind(
            "<Return>",
            lambda event, tracker_socket=tracker_socket, tracker_gui=tracker_gui: self.command_handler(tracker_socket, tracker_gui),
        )
        tracker_gui.print_message(f"Listening on {tracker_ip}:{tracker_port}\n\n")
        threading.Thread(target=self.peer_listener, args=[tracker_socket, tracker_gui]).start()
        tracker_gui.mainloop()

        try:
            tracker_socket.close()
        except Exception:
            pass

if __name__ == "__main__":
    (Tracker()).main()