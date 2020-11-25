import json
import re
from collections import namedtuple


class DetectionRule:

    IF_MACS_REGEX = re.compile(r'\\"if_macs\\":(\{.*?\})')
    NUM_STREAMS_REGEX = re.compile(r'num_streams_5\":\"(\d+)x\d+\"')

    def __init__(
        self,
        device_name,
        device_type,
        env=None,
        mac_prefix=None,
        interfaces=None,
        num_streams_5=None,
    ):
        self.device_name = device_name
        self.device_type = device_type
        self.env = env
        self.mac_prefix = mac_prefix
        self.interfaces = interfaces
        self.num_streams_5 = num_streams_5

    def match(self, device_id, env, data):
        if (
            self.match_environment(env, device_id, data)
            and self.match_mac_prefix(env, device_id, data)
            and self.match_interfaces(env, device_id, data)
            and self.match_num_streams_5(env, device_id, data)
        ):
            return True
        return False

    def match_environment(self, env, device_id, data):
        if self.env and env not in self.env:
            return False
        return True

    def match_mac_prefix(self, env, device_id, data):
        if not self.mac_prefix:
            return True

        for mac_prefix in self.mac_prefix:
            if device_id.upper().startswith(mac_prefix):
                return True

        return False

    def match_interfaces(self, env, device_id, data):
        if not self.interfaces:
            return True

        match = DetectionRule.IF_MACS_REGEX.search(data)
        if match:
            try:
                without_escapes = match[1].replace("\\", "")
                if_macs_json = json.loads(without_escapes)
                for interface in self.interfaces:
                    if interface not in if_macs_json:
                        return False
                return True
            except Exception:
                pass
        return False

    def match_num_streams_5(self, env, device_id, data):
        if self.num_streams_5 is None:
            return True

        match = DetectionRule.NUM_STREAMS_REGEX.search(data)
        if match and match[1].isnumeric():
            stream_count = int(match[1])
            if stream_count == self.num_streams_5:
                return True

        return False


DETECTION_RULES = [
    DetectionRule(
        device_name="air4920",
        device_type=6,
        mac_prefix=["88:41:FC", "F4:17:B8"],
        num_streams_5=3,
    ),
    DetectionRule(
        device_name="air4930",
        device_type=18,
        mac_prefix=["88:41:FC", "F4:17:B8"],
        num_streams_5=4,
    ),
    DetectionRule(
        device_name="genexis7840",
        device_type=22,
        mac_prefix=["00:0F:94", "34:E3:80"],
        interfaces=["br-lan_4001"],
    ),
    DetectionRule(
        device_name="genexis6840",
        device_type=21,
        mac_prefix=["00:0F:94", "34:E3:80"],
        interfaces=["br-lan"],
    ),
    DetectionRule(
        device_name="fmg3542-d10a",
        device_type=16,
        env="tafjord",
        interfaces=["wlan0", "ath0"],
    ),
    DetectionRule(
        device_name="emg5924-d10a",
        device_type=27,
        env="tafjord",
        interfaces=["ra0", "ath0"],
    ),
    DetectionRule(
        device_name="vmg8825-b50b",
        device_type=12,
        env="tafjord",
        interfaces=["wl0", "wl1"],
    ),
    DetectionRule(
        device_name="vmg8825-t50k",
        device_type=13,
        env="online",
        interfaces=["ra0", "rai0"],
    ),
]

DeviceMetadata = namedtuple("DeviceMetadata", ["name", "device_type", "is_gateway"])

DEVICE_TYPE_METADATA = {
    rule.device_type: DeviceMetadata(
        rule.device_name, rule.device_type, rule.device_type not in [6, 18]
    )
    for rule in DETECTION_RULES
}


def get_device_type_metadata(device_type):
    return DEVICE_TYPE_METADATA.get(device_type, None)


def detect_device_type(device_id, env, data):
    for rule in DETECTION_RULES:
        if rule.match(device_id, env, data):
            return rule.device_type
    return None
