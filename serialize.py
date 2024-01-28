#!/usr/bin/env python3
# ✓
import datetime
import json


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for k, v in obj.items():
            if k.endswith("_ts") and isinstance(v, str):
                try:
                    obj[k] = datetime.datetime.fromisoformat(v)
                except ValueError:
                    pass
        return obj


def serialize(data):
    return json.dumps(data, cls=Encoder)


def deserialize(data):
    return json.loads(data, cls=Decoder)
