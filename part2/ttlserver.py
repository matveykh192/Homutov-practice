import time  # Импортируем модуль для работы с временем
import socket

class RedisServer:
    def __init__(self, host="localhost", port=6379):
        self.host = host
        self.port = port
        self.data_store = {}
        self.ttl_store = {}  # Хранит ключи и их срок истечения (timestamp)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ... (остальные методы остаются без изменений)

    def execute_command(self, command_parts):
        if not command_parts:
            return "-ERR empty command\r\n"

        cmd = command_parts[0].upper()

        # Проверяем, не истёк ли срок действия ключа
        if cmd != "EXPIRE" and len(command_parts) > 1:
            key = command_parts[1]
            if self.check_ttl(key):
                del self.data_store[key]
                del self.ttl_store[key]
                return ":-2\r\n"  # Код "ключ не существует" для TTL

        if cmd == "SET":
            if len(command_parts) < 3:
                return "-ERR wrong number of arguments for 'SET'\r\n"
            key, value = command_parts[1], command_parts[2]
            self.data_store[key] = value
            return "+OK\r\n"

        elif cmd == "EXPIRE":
            if len(command_parts) != 3:
                return "-ERR wrong number of arguments for 'EXPIRE'\r\n"
            key = command_parts[1]
            try:
                ttl_seconds = int(command_parts[2])
            except ValueError:
                return "-ERR invalid TTL value\r\n"
            
            if key not in self.data_store:
                return ":0\r\n"  # Ключ не существует
                
            self.ttl_store[key] = time.time() + ttl_seconds
            return ":1\r\n"  # Успешно установлен TTL

        elif cmd == "TTL":
            if len(command_parts) != 2:
                return "-ERR wrong number of arguments for 'TTL'\r\n"
            key = command_parts[1]
            
            if key not in self.data_store:
                return ":-2\r\n"  # Ключ не существует
            
            if key not in self.ttl_store:
                return ":-1\r\n"  # TTL не установлен
            
            remaining = int(self.ttl_store[key] - time.time())
            return f":{remaining}\r\n"

        # ... (остальные команды: GET, DEL, EXISTS, KEYS остаются без изменений)

    def check_ttl(self, key):
        """Проверяет, истёк ли срок действия ключа. Если истёк — удаляет его."""
        if key in self.ttl_store and self.ttl_store[key] <= time.time():
            del self.data_store[key]
            del self.ttl_store[key]
            return True
        return False