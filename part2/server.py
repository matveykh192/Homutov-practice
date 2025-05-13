import socket
import threading

class RedisServer:
    def __init__(self, host="localhost", port=6379):
        self.host = host
        self.port = port
        self.data_store = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Сервер Redis запущен на {self.host}:{self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Подключён клиент: {addr}")
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,),
                daemon=True
            )
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                request = client_socket.recv(1024).decode().strip()
                if not request:
                    break

                command_parts = self.parse_resp(request)
                response = self.execute_command(command_parts)
                client_socket.send(response.encode())
        except ConnectionResetError:
            print("Клиент отключился")
        finally:
            client_socket.close()

    def parse_resp(self, request):
        parts = request.split("\r\n")
        if not parts:
            return []

        # Пример парсинга: *3\r\n$3\r\nSET\r\n$4\r\nname\r\n$5\r\nAlice\r\n
        command_parts = []
        i = 0
        while i < len(parts):
            if parts[i].startswith("*"):
                num_args = int(parts[i][1:])
                i += 1
                for _ in range(num_args):
                    if parts[i].startswith("$"):
                        arg_len = int(parts[i][1:])
                        i += 1
                        command_parts.append(parts[i][:arg_len])
                        i += 1
            else:
                i += 1
        return command_parts

    def execute_command(self, command_parts):
        if not command_parts:
            return "-ERR empty command\r\n"

        cmd = command_parts[0].upper()
        if cmd == "SET":
            if len(command_parts) != 3:
                return "-ERR wrong number of arguments for 'SET'\r\n"
            key, value = command_parts[1], command_parts[2]
            self.data_store[key] = value
            return "+OK\r\n"

        elif cmd == "GET":
            if len(command_parts) != 2:
                return "-ERR wrong number of arguments for 'GET'\r\n"
            key = command_parts[1]
            value = self.data_store.get(key, "")
            return f"${len(value)}\r\n{value}\r\n"

        elif cmd == "DEL":
            if len(command_parts) != 2:
                return "-ERR wrong number of arguments for 'DEL'\r\n"
            key = command_parts[1]
            if key in self.data_store:
                del self.data_store[key]
                return ":1\r\n"
            else:
                return ":0\r\n"

        elif cmd == "EXISTS":
            if len(command_parts) != 2:
                return "-ERR wrong number of arguments for 'EXISTS'\r\n"
            key = command_parts[1]
            return f":{1 if key in self.data_store else 0}\r\n"

        elif cmd == "KEYS":
            if len(command_parts) != 1:
                return "-ERR wrong number of arguments for 'KEYS'\r\n"
            keys = list(self.data_store.keys())
            resp = f"*{len(keys)}\r\n"
            for key in keys:
                resp += f"${len(key)}\r\n{key}\r\n"
            return resp

        else:
            return f"-ERR unknown command '{cmd}'\r\n"

if __name__ == "__main__":
    server = RedisServer()
    server.run()