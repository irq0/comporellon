#!/usr/bin/env python3
# ✓
import edn_format


def serialize(data):
    return edn_format.dumps(data)


def deserialize(data):
    return edn_format.loads_all(data)
