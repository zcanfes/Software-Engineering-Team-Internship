import json
import glob
import inspect_dropped
import inspect_data
from lm_virtuoso import logger
from sentry_sdk import capture_exception
from config import Config


def read_data(filename):
    """
    Read data in the file
    :param filename:
    :return: list of data sorted by timestamp
    """
    result = []
    with open(filename, 'r') as json_file:
        json_list = list(json_file)

    for json_str in json_list:
        try:
            result.append(json.loads(json_str))
        except ValueError:
            logger.error(f"Invalid json string in {filename}: {json_str}")
            raise ValueError

    sorted_data = sorted(result, key=lambda x: x['timestamp'])
    return sorted_data


def initialize_buckets(sorted_data):
    """
    Divide data into buckets per hour
    :param sorted_data:
    :return: list of lists, data points for each hour
    """
    i = 0
    buckets = {0: []}
    initial = sorted_data[0]['timestamp']
    for data_pt in sorted_data:
        if data_pt['timestamp'] < initial + 3600:
            buckets[i].append(data_pt)
        else:
            i += 1
            buckets[i] = [data_pt]
            initial = data_pt['timestamp']
    return buckets


def main():
    try:
        for file_path in glob.glob(f"{Config.DIRECTORY}/*.jsonl"):
            Config.ANALYSIS.write(file_path + "\n\n")
            logger.info(f"filename: {file_path}")
            sort_data = read_data(file_path)
            hours_bucket = initialize_buckets(sort_data)
            data_file = DataFile(file_path, sort_data, hours_bucket)
            if Config.INSPECT_DROPPED:
                drop = inspect_dropped.Dropped(data_file)
                drop.run()
            if Config.INSPECT_DATA:
                inspect = inspect_data.Data(data_file)
                inspect.run()
            logger.success(f"file {str(file_path)} completed\n")
    except Exception:
        capture_exception()
        logger.exception("Could not finish reading files")


class DataFile:
    def __init__(self, file, sorted_data, buckets):
        self.file = file
        self.sorted_data = sorted_data
        self.buckets = buckets


if __name__ == '__main__':
    main()
