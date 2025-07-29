import argparse
import json
from datetime import datetime
from collections import defaultdict


class LogProcessor:
    """Базовый класс для анализа логов."""

    def process_logs(self, logs):
        """Парсинг и возврат анализа данных."""
        raise NotImplementedError


class AverageReportProcessor(LogProcessor):
    """Класс для создания отчёта о среднем времени ответа апи."""

    def process_logs(self, logs):
        """Парсинг и возврат анализа данных по разным апи."""
        endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

        for log in logs:
            url = log["url"]
            endpoint_stats[url]["count"] += 1
            endpoint_stats[url]["total_time"] += log["response_time"]

        report_data = []
        counter = 0
        for url, stats in endpoint_stats.items():
            avg_time = stats["total_time"] / stats["count"]
            report_data.append({
                "": counter,
                "handler": url,
                "total": stats["count"],
                "avg_response_time": f"{avg_time:.3f}"
            })
            counter += 1

        return report_data


class LogAnalyzer:
    """Основной класс анализа данных."""

    def __init__(self):
        self.processors = {
            "average": AverageReportProcessor()
        }

    def load_logs(self, file_paths, date_filter=None):
        """Загрузка и фильтрация логов."""
        logs = []
        for file_path in file_paths:
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        if date_filter:
                            log_date = datetime.fromisoformat(log["@timestamp"]).date()
                            if log_date != date_filter:
                                continue
                        logs.append(log)
                    except json.JSONDecodeError:
                        continue
        return logs

    def generate_report(self, report_name, file_paths, date_filter=None):
        """Генерация отчёта."""
        if report_name not in self.processors:
            raise ValueError(f"Недопустимый тип отчёта: {report_name}")

        logs = self.load_logs(file_paths, date_filter)
        processor = self.processors[report_name]
        return processor.process_logs(logs)


def parse_date(date_str):
    """Преобразование строки времени в формат datetime.date."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def setup_arg_parser():
    """Установка аргументов команды."""
    parser = argparse.ArgumentParser(description="Log file analyzer")
    parser.add_argument(
        "--file",
        dest="files",
        nargs='+',  # Принимает один или несколько аргументов
        required=True,
        help="Log files to process (space-separated)"
    )
    parser.add_argument(
        "--report",
        choices=["average"],
        required=True,
        help="Type of report to generate"
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        help="Filter logs by date (format: YYYY-MM-DD)"
    )
    return parser


def print_dicts_as_table(list_of_dicts: list):
    if not list_of_dicts:
        print("Список пуст")
        return

    # Получаем все ключи из первого словаря (предполагаем, что у всех одинаковые ключи)
    headers = list_of_dicts[0].keys()
    # Определяем ширину столбцов
    col_widths = {
        header: max(
            len(str(header)),  # Ширина заголовка
            max(len(str(d.get(header, ""))) for d in list_of_dicts)  # Макс. ширина данных в столбце
        )
        for header in headers
    }

    # Создаем строку формата для выравнивания
    row_format = "   ".join([f"{{:<{col_widths[header]}}}" for header in headers])

    # Печатаем заголовки
    print(row_format.format(*headers))
    # Печатаем разделительную строку
    print("   ".join(["-" * col_widths[header] for header in headers]))

    # Печатаем строки данных
    for row in list_of_dicts:
        print(row_format.format(*[row.get(header, "") for header in headers]))


def main():
    """Main entry point."""
    parser = setup_arg_parser()
    args = parser.parse_args()

    analyzer = LogAnalyzer()

    try:
        report_data = analyzer.generate_report(args.report, args.files, args.date)
        print_dicts_as_table(report_data)
    except Exception as e:
        print(f"Ошибка при генерации отчёта: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())