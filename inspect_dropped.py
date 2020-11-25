from config import Config
from lm_virtuoso import logger
from collections import Counter


def time_difference(sorted_upd):
    """
    Check if time difference between updates is greater than seconds
    :param sorted_upd:
    :return:
    """
    keys = []
    values = []
    for i in range(len(sorted_upd) - 1):
        difference = sorted_upd[i + 1]['timestamp'] - sorted_upd[i]['timestamp']
        if difference > float(Config.BOUNDARY):
            keys.append((sorted_upd[i]['timestamp'], sorted_upd[i + 1]['timestamp']))
            values.append(difference)
    time_diff = dict(zip(keys, values))
    Config.ANALYSIS.write(f"regular time greater than {Config.BOUNDARY}s: {time_diff}\n\n")
    return time_diff


def missing_reg_interval(keys, values, time_before, time_after, hour):
    """
    Calculates the number of missing regulars in interval [time_before, time_after]
    :param keys:
    :param values:
    :param time_before:
    :param time_after:
    :param hour:
    :return:
    """
    if is_dropped(time_after, time_before):
        keys.append((time_before, time_after))
        values.append((time_after - time_before, hour))
        Config.ANALYSIS.write(f"{(time_before, time_after)}: {(time_after - time_before, hour)}, "
                              f"{round((time_after - time_before) / float(Config.BOUNDARY) - 0.5)} "
                              f"possible missing regulars\n")


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


class Dropped:
    def __init__(self, data_file):
        self.data_file = data_file

    def data_upd_type(self, upd_type):
        """
        Return sorted array of given update type
        :param upd_type:
        :return:
        """
        sorted_upd = []
        for data_pt in self.data_file.sorted_data:
            if data_pt['type'] == upd_type:
                sorted_upd.append(data_pt)
            else:
                pass
        return sorted_upd

    def upd_type_count(self, upd_type, ct_type):
        """
        Count the update type per hour
        :param upd_type:
        :param ct_type:
        :return:
        """
        for hour in self.data_file.buckets:
            ct_type[hour] = Counter(pt['type'] for pt in self.data_file.buckets[hour])[upd_type]
        return ct_type

    def reg_upd_count(self):
        """
        Regular data count per hour
        :return: list of slow data count per hour
        """
        return self.upd_type_count("regular", [0] * 24)

    def slow_upd_count(self):
        """
        Slow data count per hour
        :return :list of slow data count per hour
        """
        return self.upd_type_count("slow", [0] * 24)

    def slow_update_duration(self):
        """
        Write time difference of reg-slow and slow-reg to analysis file for each slow update
        :return:
        """
        for i in range(len(self.data_file.sorted_data)):
            if self.data_file.sorted_data[i]['type'] == 'slow':
                slow_upd = self.data_file.sorted_data[i]['timestamp']
                Config.ANALYSIS.write(f"slow at: {slow_upd}\n")
                if i == 0:
                    after_slow = self.data_file.sorted_data[i + 1]['timestamp']
                    Config.ANALYSIS.write(f"after slow: ({slow_upd}, {after_slow}) "
                                          f"= {after_slow - slow_upd}\n\n")
                elif i == len(self.data_file.sorted_data) - 1:
                    before_slow = self.data_file.sorted_data[i - 1]['timestamp']
                    Config.ANALYSIS.write(f"before slow: ({before_slow}, {slow_upd}) "
                                          f"= {slow_upd - before_slow}\n\n")
                else:
                    before_slow = self.data_file.sorted_data[i - 1]['timestamp']
                    after_slow = self.data_file.sorted_data[i + 1]['timestamp']
                    Config.ANALYSIS.write(f"before slow: ({before_slow}, {slow_upd}) "
                                          f"= {slow_upd - before_slow}\n")
                    Config.ANALYSIS.write(f"after slow: ({slow_upd}, {after_slow}) "
                                          f"= {after_slow - slow_upd}\n\n")
        Config.ANALYSIS.write("\n\n")

    def missing_reg(self):
        """
        Write the estimated number of possible missing regular updates to analysis file
        :return: dictionary, consecutive reg upd tuple as keys and time diff-hour tuple as values
        """
        keys = []
        values = []
        count = [0] * 24

        for hour in self.data_file.buckets:
            for i in range(len(self.data_file.buckets[hour])):
                data_pt = self.data_file.buckets[hour][i]
                if data_pt['type'] == 'slow':
                    time_before = self.data_file.buckets[hour][i - 1]['timestamp']
                    time_slow = self.data_file.buckets[hour][i]['timestamp']
                    if i != len(self.data_file.buckets[hour]) - 1:
                        time_after = self.data_file.buckets[hour][i + 1]['timestamp']
                        missing_reg_interval(keys, values, time_before, time_after, hour)
                    else:
                        missing_reg_interval(keys, values, time_before, time_slow, hour)
                    if (time_slow - time_before) / float(Config.BOUNDARY) > 1:
                        count[hour] += round((time_slow - time_before) / float(Config.BOUNDARY))
        missing_regular = dict(zip(keys, values))

        logger.info(f"missing regular due to slow updates per hour: {count}")
        logger.info(f"missing regular due to slow updates: {missing_regular}")
        logger.info(f"total missing regular due to slow updates: {sum(count)}")
        Config.ANALYSIS.write("\n")
        return missing_regular

    def avg_upd_dropped(self):
        """
        Calculates average time difference of dropped updates
        :return:
        """
        sum_upd = 0
        count = 0
        for hour in self.data_file.buckets:
            for i in range(len(self.data_file.buckets[hour]) - 1):
                if is_dropped(self.data_file.buckets[hour][i + 1]['timestamp'],
                              self.data_file.buckets[hour][i]['timestamp']):
                    sum_upd += self.data_file.buckets[hour][i + 1]['timestamp'] \
                               - self.data_file.buckets[hour][i]['timestamp']
                    count += 1
        if count == 0:
            logger.info("no dropped updates")
            return 1
        average = round(sum_upd / count, 2)
        logger.info(f"average update duration if dropped: {average}s")
        return round(sum_upd / count, 2)

    def run(self):
        time_difference(self.data_upd_type('regular'))
        self.reg_upd_count()
        self.slow_upd_count()
        self.missing_reg()
        self.slow_update_duration()
        self.avg_upd_dropped()
