import argparse
from unittest.mock import patch, mock_open

import pytest
import json
from datetime import date
from log_analyzer import AverageReportProcessor, LogAnalyzer, print_dicts_as_table, parse_date


@pytest.fixture
def sample_logs():
    return [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/users", "response_time": 0.1},
        {"@timestamp": "2025-06-22T14:00:00+00:00", "url": "/api/users", "response_time": 0.2},
        {"@timestamp": "2025-06-23T12:00:00+00:00", "url": "/api/posts", "response_time": 0.3},
    ]


@pytest.fixture
def log_file(tmp_path, sample_logs):
    file = tmp_path / "test.log"
    with open(file, "w") as f:
        for log in sample_logs:
            f.write(json.dumps(log) + "\n")
    return file


def test_average_report_processor(sample_logs):
    processor = AverageReportProcessor()
    result = processor.process_logs(sample_logs)

    expected = [
        {"": 0, "handler": "/api/users", "total": 2, "avg_response_time": "0.150"},
        {"": 1, "handler": "/api/posts", "total": 1, "avg_response_time": "0.300"}
    ]

    assert len(result) == len(expected)
    for item in expected:
        assert item in result


def test_log_analyzer_with_date_filter(tmp_path, sample_logs):
    file = tmp_path / "test.log"
    with open(file, "w") as f:
        for log in sample_logs:
            f.write(json.dumps(log) + "\n")

    analyzer = LogAnalyzer()
    report_data = analyzer.generate_report(
        "average",
        [file],
        date_filter=date(2025, 6, 22))

    assert len(report_data) == 1
    assert report_data[0]["handler"] == "/api/users"
    assert report_data[0]["total"] == 2


def test_log_analyzer_without_date_filter(tmp_path, sample_logs):
    file = tmp_path / "test.log"
    with open(file, "w") as f:
        for log in sample_logs:
            f.write(json.dumps(log) + "\n")

    analyzer = LogAnalyzer()
    report_data = analyzer.generate_report("average", [file])

    assert len(report_data) == 2


def test_print_dicts_as_table(capsys):
    test_data = [
        {"": 0, "handler": "/api/users", "total": 10, "avg_response_time": "0.150"},
        {"": 1, "handler": "/api/posts", "total": 5, "avg_response_time": "0.200"}
    ]

    expected_output = ('    handler      total   avg_response_time\n'
                     '-   ----------   -----   -----------------\n'
                     '0   /api/users   10      0.150            \n'
                     '1   /api/posts   5       0.200            \n')

    print_dicts_as_table(test_data)
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_print_empty_list(capsys):
    print_dicts_as_table([])
    captured = capsys.readouterr()
    assert captured.out == "Список пуст\n"


def test_log_analyzer_with_multiple_files(tmp_path, sample_logs):
    file1 = tmp_path / "test1.log"
    file2 = tmp_path / "test2.log"

    with open(file1, "w") as f:
        json.dump(sample_logs[0], f)
        f.write("\n")

    with open(file2, "w") as f:
        json.dump(sample_logs[1], f)
        f.write("\n")
        json.dump(sample_logs[2], f)
        f.write("\n")

    analyzer = LogAnalyzer()
    report_data = analyzer.generate_report("average", [file1, file2])

    assert len(report_data) == 2
    assert report_data[0]["handler"] == "/api/users"
    assert report_data[1]["handler"] == "/api/posts"


# Test main function
@patch("sys.argv", ["script.py", "--file", "test.log", "--report", "average"])
@patch("builtins.open", new_callable=mock_open, read_data='{"url": "/api/test", "response_time": 1.0, "@timestamp": "2023-01-01T00:00:00"}\n')
@patch("log_analyzer.print_dicts_as_table")
def test_main_success(mock_print, mock_file):
    from log_analyzer import main
    assert main() == 0

@patch("sys.argv", ["script.py", "--file", "test.log", "--report", "average"])
@patch("builtins.open", new_callable=mock_open, read_data='{}')
def test_main_error(mock_file):
    from log_analyzer import main
    assert main() == 1


# Test parse_date
def test_parse_date_valid():
    result = parse_date("2023-01-01")
    assert result == date(2023, 1, 1)

def test_parse_date_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_date("invalid-date")