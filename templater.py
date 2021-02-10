#!/usr/bin/env python3
import logging
import os.path
import sys

import edn_format
import jinja2

import serialize

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

TEMPLATE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG = logging.getLogger(__name__)


def render_template(template_filename, data):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        block_start_string=r"\code{",
        block_end_string="}",
        variable_start_string=r"\jvar{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%!!",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
    )
    return env.get_template(template_filename).render(data)


def ingest_data(fo):
    data = {}
    for obj in serialize.deserialize(fo.read()):
        for k, v in obj.items():
            if k not in data.keys():
                if isinstance(v, edn_format.ImmutableList):
                    data[k] = list(v)
                elif isinstance(v, edn_format.ImmutableDict):
                    data[k] = dict(v)
                else:
                    data[k] = v
            else:
                if isinstance(v, edn_format.ImmutableList):
                    data[k].extend(v)
                elif isinstance(v, edn_format.ImmutableDict):
                    data[k].update(v)
                else:
                    raise TypeError(f"Key {k} has an unsupported value type {type(v)}")
    return data


if __name__ == "__main__":
    data = ingest_data(sys.stdin)
    print(render_template(sys.argv[1], data))
