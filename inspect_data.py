import json
import os
import device_detection
from config import Config
from lm_virtuoso import logger


def is_dropped(upd_time, time_before):
    """
    Returns if there is a dropped update in the interval
    :param upd_time:
    :param time_before:
    :return:
    """
    if (upd_time - time_before) / float(Config.BOUNDARY) >= 1.5:
        return True
    return False


class Data:
    def __init__(self, data_file):
        self.data_file = data_file

    def latest_ver(self):
        """
        Latest version per hour
        :return: lise of versions per hour
        """
        ver = [None] * 24
        no_ver = []
        for hour in self.data_file.buckets:
            for pt in self.data_file.buckets[hour]:
                try:
                    pt_data = json.loads(pt['data'])
                    if 'ver' in pt_data:
                        ver[hour] = pt_data['ver']
                except ValueError:
                    logger.error(f"Invalid json string: {pt['data']}")
                    raise ValueError
            if ver[hour] is None:
                no_ver.append(hour)
        if len(no_ver) != 0:
            logger.info(f"no version in hours: {no_ver}")
        logger.info(f"version: {ver}")
        return ver

    def latest_dr_ver(self):
        """
        Latest driver version per hour
        :return: list of driver versions per hour
        """
        dr_ver = [None] * 24
        no_dr_ver = []
        for hour in self.data_file.buckets:
            for pt in self.data_file.buckets[hour]:
                try:
                    pt_data = json.loads(pt['data'])
                    if 'dr_ver' in pt_data:
                        dr_ver[hour] = pt_data['dr_ver']
                except ValueError:
                    logger.error(f"Invalid json string: {pt['data']}")
                    raise ValueError
            if dr_ver[hour] is None:
                no_dr_ver.append(hour)
        if len(no_dr_ver) != 0:
            logger.info(f"no driver version in hours: {no_dr_ver}")
        logger.info(f"driver version: {dr_ver}")
        return dr_ver

    def station_count(self):
        """
        Return data point's stations length
        :return: list of stations size per hour
        """
        stations = [0] * 24
        for hour in self.data_file.buckets:
            for pt in self.data_file.buckets[hour]:
                try:
                    pt_data = json.loads(pt['data'])
                    if 'stations' in pt_data:
                        stations[hour] = len(pt_data['stations'])
                except ValueError:
                    logger.error(f"Invalid json string: {pt['data']}")
                    raise ValueError
        logger.info(f"stations: {stations}")
        return stations

    def neighbor_count(self):
        """
        Return data point's neighbors length
        :return: list of neighbors size per hour
        """
        neighbors = [0] * 24
        prev = 0
        for hour in self.data_file.buckets:
            for pt in self.data_file.buckets[hour]:
                if pt['type'] == "slow":
                    try:
                        pt_data = json.loads(pt['data'])
                        neighbors_count = len(pt_data['neighbors'])
                        neighbors[hour] = neighbors_count
                        prev = neighbors_count
                    except ValueError:
                        logger.error(f"Invalid json string: {pt['data']}")
                        raise ValueError
                    except KeyError:
                        logger.error(f"slow update at {pt['timestamp']} does not have neighbors")
            if neighbors[hour] == 0:
                neighbors[hour] = prev
        logger.info(f"neighbors: {neighbors}")
        return neighbors

    def avg_upd_not_dropped(self):
        """
        Calculates average time difference of updates that are not dropped
        :return:
        """
        sum_upd = 0
        count = 0
        for hour in self.data_file.buckets:
            for i in range(len(self.data_file.buckets[hour]) - 1):
                if not is_dropped(self.data_file.buckets[hour][i + 1]['timestamp'],
                                  self.data_file.buckets[hour][i]['timestamp']):
                    sum_upd += self.data_file.buckets[hour][i + 1]['timestamp'] - \
                               self.data_file.buckets[hour][i]['timestamp']
                    count += 1
        if count == 0:
            logger.error("every update is dropped")
            return 1.0
        average = round(sum_upd / count, 2)
        logger.info(f"average upd duration if not dropped:{average}s")
        return average

    def get_device_type(self):
        """
        Returns the device type for each raw data file
        :return:
        """
        device_id = os.path.basename(self.data_file.file).partition("-")[0].replace('_', ':')
        device_type = {device_id: "Unknown"}
        for pt in self.data_file.sorted_data:
            if pt['type'] == 'slow':
                pt_data = pt['data']
                if device_detection.detect_device_type(device_id, Config.DEVICE_ENV, pt_data) \
                        is not None:
                    device_type[device_id] = \
                        (device_detection.detect_device_type(device_id, Config.DEVICE_ENV, pt_data))
                    logger.info(f"{device_type}")
                    return device_type
        logger.info(f"{device_type}")
        return device_type

    def run(self):
        self.latest_ver()
        self.latest_dr_ver()
        self.neighbor_count()
        self.station_count()
        self.avg_upd_not_dropped()
        self.get_device_type()
