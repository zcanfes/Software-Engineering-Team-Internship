import pytest
import json


@pytest.fixture
def read_data():
    result = []
    with open('tests/sample_input.jsonl', 'r') as json_file:
        json_list = list(json_file)

    for json_str in json_list:
        result.append(json.loads(json_str))

    sorted_data = sorted(result,   key=lambda x:  x['timestamp'])
    return sorted_data
