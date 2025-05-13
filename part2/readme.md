Запуск сервера
Требования
Python 3.7+

Утилита telnet (для тестирования)

1. Установка
Клонируйте репозиторий:


//git clone https://github.com/matveykh192/Homutov-practice/blob/master/part2/ttlserver.py
//cd simple-redis

2. Запуск сервера

//python redis_server.py

Сервер запустится на localhost:6379.

3. Подключение клиента
Откройте новый терминал и подключитесь через telnet:


//telnet localhost 6379

5. Остановка сервера
Нажмите Ctrl+C в терминале с сервером.

6. Пример сессии

SET user_name "John Doe"
+OK

GET user_name
$8
John Doe

EXPIRE user_name 30  # Установит TTL 30 секунд
:1

TTL user_name
:27  # Осталось 27 секунд

KEYS *
*1
$9
user_name