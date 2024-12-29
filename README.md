# Парсер PEP    

Парсинг сайта при помощи Beautiful Soup. Написал три парсера и объединил в одну многофункциональную программу: Первый парсер считывает нововведения продукта; Второй парсер собирает информацию о версиях продукта (номера, статусы, и ссылки на документацию); Третий парсер скачивает архив документов и сохраняет на локальный диск. Сделал возможным запуск парсеров выборочно, при помощи аргументов командной строки, применив модуль argparse. Для отслеживания прогресса парсинга использовал прогресс-бар tqdm. Реализовал два варианта формата вывода результатов парсинга: запись в CSV-файл и вывод в терминал в табличном виде используя библиотеку PrettyTable. Выбор формата вывода так же реализовал посредством аргументов командной строки. А еще написал систему логирования применив python библиотеку logging и всевозможные обработчики ошибок.

## Автор 
- Кобелев Андрей Андреевич  
    - [email](mailto:andrey.pydev@gmail.com)
  
## Технологии  
- [Python 3.9](https://www.python.org/downloads/release/python-390/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/4.9.3/)
- [requests-cache](https://pypi.org/project/requests-cache/1.0.0/)
- [tqdm](https://tqdm.github.io/)

## Как запустить проект: 
  
Клонировать репозиторий и перейти в него в командной строке:  
  
```  
git clone https://github.com/andrey-kobelev/bs4_parser_pep.git
```  
  
```  
cd bs4_parser_pep
```  
  
Cоздать и активировать виртуальное окружение:  
  
```  
python3 -m venv env  
```  
  
```  
source env/bin/activate  
```  
  
Установить зависимости из файла requirements.txt:  
  
```  
python3 -m pip install --upgrade pip  
```  
  
```  
pip install -r requirements.txt  
```

## Команды запуска/Справка

### Справка

```bash
python src/main.py -h
```

```
Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных

```

### Пример выполнения команды

**Команда:**

```bash
python src/main.py pep --output pretty
```

**Результат:**

```
"02.08.2024 19:18:05 - [INFO] - Парсер запущен!"
"02.08.2024 19:18:05 - [INFO] - Аргументы командной строки: Namespace(mode='pep', clear_cache=False, output='pretty')"
100%|█████████████████████████████████████| 1299/1299 [00:46<00:00, 28.06it/s]
"02.08.2024 19:18:52 - [INFO] - НЕСОВПАДЕНИЕ СТАТУСОВ! ['Статус из списка: R; Статус на странице https://peps.python.org/pep-0401/: April Fool!', 'Статус из списка: R; Статус на странице https://peps.python.org/pep-0401/: April Fool!']"
"02.08.2024 19:18:52 - [INFO] - PEP без типа и статуса: ['https://peps.python.org/pep-0801/']"
+------------------+------------+
| Статус           | Количество |
+------------------+------------+
| Active           | 67         |
| Final            | 630        |
| Accepted         | 44         |
| Provisional      | 4          |
| Draft            | 64         |
| Superseded       | 46         |
| Deferred         | 72         |
| Withdrawn        | 122        |
| Rejected         | 248        |
| Общее количество | 1297       |
+------------------+------------+
"02.08.2024 19:18:52 - [INFO] - Парсер завершил работу."

```
