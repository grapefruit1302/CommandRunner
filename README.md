# CommandRunner
Ця програма дозволяє виконувати команди на мережевих комутаторах через протоколи SSH та Telnet. Вона має інтерактивний інтерфейс, створений за допомогою бібліотеки PyQt5, що дозволяє вводити необхідні параметри для підключення та виконання команд, а також консольну версію.

Запустіть програму, виконавши скрипт Python: python3 main.py.

Введіть необхідні параметри для підключення до SSH-сервера:

SSH-хост: IP-адреса або доменне ім'я сервера SSH.
SSH-порт: порт для SSH-з'єднання.
Ім'я користувача SSH.
Пароль SSH.

Введіть необхідні команди для виконання на комутаторах у вікно вводу команд. Кожна команда повинна бути в окремому рядку.

Натисніть кнопку "Пуск" для виконання команд на всіх комутаторах.

Програма виконає команди на кожному комутаторі та виведе результати в журналі. Результати включають інформацію про те, чи було виконано команди успішно, та час виконання.

Також, важливо враховувати, що цей код передбачає наявність файлу "CommandRun.ui", який містить графічний інтерфейс програми, створений за допомогою Qt Designer.

Під час використання цієї програми впевніться, що всі необхідні бібліотеки, включаючи PyQt5 і paramiko, встановлені на вашому комп'ютері.

