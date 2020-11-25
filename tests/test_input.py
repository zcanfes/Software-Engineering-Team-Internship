import application
from inspect_data import Data
from inspect_dropped import Dropped
from application import DataFile


def test_sorted_data(read_data):
    assert type(read_data) == list
    for pt in read_data:
        assert pt['device_id'] is not None
        assert type(pt['timestamp']) == float


def test_buckets(read_data):
    buckets = application.initialize_buckets(read_data)
    assert type(buckets) == dict
    assert len(buckets) > 0


def test_inspect_data(read_data):
    data = Data(DataFile("Filename", read_data, application.initialize_buckets(read_data)))
    ver = data.latest_ver()
    dr_ver = data.latest_ver()
    assert type(ver) == list
    assert len(ver) == 24
    assert type(dr_ver) == list
    assert len(dr_ver) == 24
    if type(data.avg_upd_not_dropped()) != str:
        assert type(data.avg_upd_not_dropped()) == float


def test_inspect_dropped(read_data):
    dropped = Dropped(DataFile("Filename", read_data, application.initialize_buckets(read_data)))
    assert type(dropped.data_upd_type('slow')) == type(read_data)
    assert type(dropped.data_upd_type('regular')) == type(read_data)

    reg_ct = dropped.reg_upd_count()
    for i in reg_ct:
        assert type(i) == int
    slow_ct = dropped.slow_upd_count()
    for i in slow_ct:
        assert type(i) == int

    if type(dropped.avg_upd_dropped()) != str:
        assert type(dropped.avg_upd_dropped()) == float
