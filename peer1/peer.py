import socket
import os
import pickle
import threading
import shutil
from peer_GUI import Peer_GUI
import re
import base64

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

class Peer:
    def __init__(self) -> None:
        self.local_dir = 'local'
        os.makedirs(self.local_dir, exist_ok=True)
        self.my_addr = []
        self.is_choosing = False
        self.tracker_socket = None
        self.socket_for_upload = None
        self.other_peer = []
        self.blocked_peer = []
        self.is_running = True  # Added shutdown flag

    def get_files_name(self):
        return os.listdir(self.local_dir)

    def get_encode_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
        encoded_data = base64.b64encode(file_data).decode('utf-8')
        return encoded_data

    def get_files_information(self):
        files_name = self.get_files_name()
        files_info = []
        for f in files_name:
            full_path = os.path.join(self.local_dir, f)
            if os.path.isfile(full_path):
                file_size = os.path.getsize(full_path)
                file_hash = self.get_encode_file(full_path)
                files_info.append((f, file_size, file_hash))
        return files_info

    def command_handler(self, peer_gui: Peer_GUI):
        try:
            command = peer_gui.get_command()
            if self.is_choosing:
                try:
                    num_choice = re.search(r'\d+', command).group()
                    choice = self.other_peer[int(num_choice) - 1]
                    fetch_ip, fetch_port = (choice[0], choice[1]+1)
                    fetch_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    fetch_socket.connect((fetch_ip, fetch_port))
                    send_full_message(fetch_socket, {
                        'type': 'fetch_peer',
                        'data': self.file_name,
                    })
                    file_path = os.path.join(self.local_dir, self.file_name)
                    print(f"Saving fetched file to: {file_path}")
                    with open(file_path, 'wb') as file:
                        while True:
                            chunk = fetch_socket.recv(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                            fetch_socket.send('data received.'.encode('utf-8'))
                    fetch_socket.close()
                except Exception as e:
                    peer_gui.print_message(f'Error while fetching: {e}\n\n')
                self.is_choosing = False
                peer_gui.print_message('Fetching completed!!\n')
                files = self.get_files_information()
                send_full_message(self.tracker_socket, {
                    'type': 'publish',
                    'data': files,
                })
            else:
                args_list = command.split()
                if args_list[0] == 'fetch':
                    self.file_name = args_list[1]
                    send_full_message(self.tracker_socket, {
                        'type': 'fetch',
                        'data': self.file_name,
                    })
                elif args_list[0] == 'list':
                    send_full_message(self.tracker_socket, {
                        'type': 'list',
                        'data': None,
                    })
                elif args_list[0] == 'publish':
                    files = self.get_files_information()
                    send_full_message(self.tracker_socket, {
                        'type': 'publish',
                        'data': files,
                    })
                elif args_list[0] == 'history':
                    file_name = args_list[1]
                    send_full_message(self.tracker_socket, {
                        'type': 'history',
                        'data': file_name,
                    })
                elif args_list[0] == 'reset':
                    file_name = args_list[1]
                    version = args_list[2]
                    send_full_message(self.tracker_socket, {
                        'type': 'reset',
                        'data': (file_name, version),
                    })
                elif args_list[0] == 'block':
                    peer_ip = args_list[1]
                    peer_port = int(args_list[2])
                    send_full_message(self.tracker_socket, {
                        'type': 'block',
                        'data': (peer_ip, peer_port),
                    })
                elif args_list[0] == 'unblock':
                    peer_ip = args_list[1]
                    peer_port = int(args_list[2])
                    send_full_message(self.tracker_socket, {
                        'type': 'unblock',
                        'data': (peer_ip, peer_port),
                    })
                elif args_list[0] == 'quit':
                    peer_gui.print_message('Closing peer socket!\n')
                    self.is_running = False  # Signal threads to stop
                    time.sleep(1)  # Allow threads to exit
                    try:
                        send_full_message(self.tracker_socket, {
                            'type': 'quit',
                            'data': None,
                        })
                    except Exception:
                        pass
                    if self.socket_for_upload:
                        self.socket_for_upload.close()
                    self.tracker_socket.close()
                    peer_gui.quit()
                    return 'break'
                else:
                    peer_gui.print_message('Not a valid command!\n')
        except Exception as e:
            peer_gui.print_message(f'command_handler stop: {e}\n')
            return 'break'

    def tracker_handler(self, peer_gui: Peer_GUI):
        host = "localhost"
        port = 65434
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.tracker_socket.connect((host, port))
            send_full_message(self.tracker_socket, {
                'type': 'connect',
                'data': self.get_files_information(),
            })
            msg = recv_full_message(self.tracker_socket)
            if msg is None:
                peer_gui.print_message('Failed to connect to tracker\n')
                return
            msg_type = msg['type']
            msg_data = msg['data']
            if msg_type == 'connect_result':
                self.my_addr = msg_data
                peer_gui.print_message(f'Tracker successfully registered you at {self.my_addr[0]}:{self.my_addr[1]}\n\n')
                while self.is_running:
                    msg = recv_full_message(self.tracker_socket)
                    if msg is None:
                        peer_gui.print_message('Connection to tracker lost\n')
                        return
                    msg_type = msg['type']
                    msg_data = msg['data']
                    if msg_type == 'update':
                        send_full_message(self.tracker_socket, {
                            'type': 'update_result',
                            'data': self.get_files_information(),
                        })
                    elif msg_type == 'list_result':
                        print_str = f'Number of peers: {len(msg_data)}\n'
                        for i in range(len(msg_data)):
                            if msg_data[i] == tuple(self.my_addr):
                                print_str += f'Peer {i+1} (you): {msg_data[i]}\n'
                            elif msg_data[i] in self.blocked_peer:
                                print_str += f'Peer {i+1} (blocked): {msg_data[i]}\n'
                            else:
                                print_str += f'Peer {i+1}: {msg_data[i]}\n'
                        peer_gui.print_message(f'{print_str}\n')
                    elif msg_type == 'fetch_result':
                        if len(msg_data) == 0:
                            peer_gui.print_message('File not found!!\n\n')
                            continue
                        print_str = ''
                        for i in range(len(msg_data)):
                            print_str += f'{i + 1}: {msg_data[i]}\n'
                        peer_gui.print_message(f'\n{print_str}')
                        self.is_choosing = True
                        self.other_peer = msg_data
                        peer_gui.fetch_options(len(msg_data))
                    elif msg_type == 'history_result':
                        if len(msg_data) == 0:
                            peer_gui.print_message('File not found!!\n\n')
                            continue
                        print_str = ''
                        for i in range(len(msg_data)):
                            print_str += f'Version {i}: {msg_data[i]}\n'
                        peer_gui.print_message(f'{print_str}\n')
                    elif msg_type == 'reset_result':
                        file_name = msg_data[0]
                        file_data_encoded = msg_data[1]
                        if file_data_encoded is None:
                            peer_gui.print_message('File not found!!\n\n')
                            continue
                        file_data = base64.b64decode(file_data_encoded)
                        file_path = os.path.join(self.local_dir, file_name)
                        print(f"Saving reset file to: {file_path}")
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        peer_gui.print_message('File is reset\n\n!')
                    elif msg_type == 'block_result':
                        if msg_data is not None:
                            self.blocked_peer.append(msg_data)
                    elif msg_type == 'unblock_result':
                        if msg_data is not None:
                            self.blocked_peer.remove(msg_data)
                    elif msg_type == 'publish_result':
                        if msg_data is True:
                            peer_gui.print_message('Publishing completed!!\n\n')
                    elif msg_type == 'quit':
                        peer_gui.print_message('\nTracker is down!!\n', 'red')
                        return
        except Exception as e:
            peer_gui.print_message(f'tracker_handler stop: {e}\n\n')
        finally:
            try:
                self.tracker_socket.close()
            except Exception:
                pass

    def req_listener(self, peer_gui: Peer_GUI):
        self.socket_for_upload = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_for_upload.bind((self.my_addr[0], self.my_addr[1]+1))
            self.socket_for_upload.listen(5)
            peer_gui.print_message(f'Listening on {self.my_addr[0]}:{self.my_addr[1]+1}\n\n')

            def req_handler(req_socket: socket.socket):
                msg = recv_full_message(req_socket)
                if msg is None:
                    req_socket.close()
                    return
                msg_type = msg['type']
                msg_data = msg['data']
                if msg_type == 'fetch_peer':
                    file_path = os.path.join(self.local_dir, msg_data)
                    try:
                        with open(file_path, 'rb') as file:
                            while True:
                                chunk = file.read(1024)
                                if not chunk:
                                    break
                                req_socket.send(chunk)
                                msg = req_socket.recv(1024).decode('utf-8')
                    except Exception as e:
                        print(f"Error sending file: {e}")
                    finally:
                        req_socket.close()

            while self.is_running:
                self.socket_for_upload.settimeout(1.0)
                try:
                    req_socket, req_addr = self.socket_for_upload.accept()
                    peer_gui.print_message(f'Accepted connection from {req_addr[0]}:{req_addr[1]}\n\n')
                    threading.Thread(target=req_handler, args=[req_socket]).start()
                except socket.timeout:
                    continue
        except Exception as e:
            peer_gui.print_message(f'req_listener stop: {e}\n\n')
        finally:
            try:
                self.socket_for_upload.close()
            except Exception:
                pass

    def main(self):
        peer_gui = Peer_GUI()
        peer_gui.title("Peer terminal")
        peer_gui.bind("<Return>", lambda event, peer_gui=peer_gui: self.command_handler(peer_gui))
        threading.Thread(target=self.tracker_handler, args=[peer_gui]).start()
        while len(self.my_addr) == 0:
            continue
        threading.Thread(target=self.req_listener, args=[peer_gui]).start()
        peer_gui.mainloop()

if __name__ == "__main__":
    (Peer()).main()