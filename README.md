# Log Analyzer

Простой инструмент для анализа лог-файлов с вычислением среднего времени ответа API.

## Возможности

- Чтение лог-файлов в формате JSON
- Фильтрация логов по дате
- Генерация отчёта о среднем времени ответа для каждого API-эндпоинта
- Вывод результатов в виде форматированной таблицы

## Требования

- Python 3.7+
- Зависимости указаны в requirements.txt

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/log-analyzer.git
cd log-analyzer
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование
#### Запуск из командной строки
```bash
python log_analyzer.py --file file1.log [file2.log ...] --report average [--date YYYY-MM-DD]
```
#### Параметры:

--file: Один или несколько лог-файлов для анализа (обязательный)

--report: Тип отчёта (пока доступен только "average") (обязательный)

--date: Фильтр по дате в формате YYYY-MM-DD (опциональный)

## Пример вывода
```
   handler                 total   avg_response_time
   ---------------------   -----   -----------------
0  /api/users             15      0.245
1  /api/products          32      0.178
2  /api/orders            8       0.512
```
#### Формат лог-файла

Лог-файлы должны содержать записи в формате JSON, по одной записи на строку:
```json
{"url": "/api/endpoint", "response_time": 0.123, "@timestamp": "2023-01-01T00:00:00"}
```
**Обязательные поля:**

url: URL эндпоинта API
response_time: Время ответа в секундах (число)
@timestamp: Временная метка в ISO формате

## Запуск тестов
```bash
pytest log_analyzer.py -v
```

## Добавление новых отчётов
- Создайте новый класс процессора в папке processors/, унаследованный от LogProcessor
- Реализуйте метод process_logs()
- Добавьте процессор в словарь self.processors в классе LogAnalyzer

Пример нового процессора:
```python
class NewReportProcessor(LogProcessor):
    def process_logs(self, logs):
        # Ваша логика обработки
        return report_data
```