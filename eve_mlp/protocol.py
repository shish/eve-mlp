#!/usr/bin/env python

"""
I have no idea how any of this works; the parser is built on
guesswork, much of it may be wrong. I just want to get the
build ID of the server, and for that, it seems good enough.
"""

import struct


def get_struct(fmt, stream):
    fmt_len = struct.calcsize(fmt)
    stream = stream.read(struct.calcsize(fmt))
    return struct.unpack(fmt, stream)


def get_thing(stream):
    (item_type, ) = get_struct("<B", stream)
    if item_type == 0x04:
        return get_struct("<I", stream)[0]
    elif item_type == 0x05:
        return get_struct("<H", stream)[0]
    elif item_type == 0x06:
        return get_struct("<B", stream)[0]
    elif item_type == 0x0A:
        return get_struct("<d", stream)[0]
    elif item_type == 0x13:
        (str_len, ) = get_struct("<b", stream)
        return get_struct("%ds" % str_len, stream)[0]
    else:
        raise Exception("Unknown item type: 0x%02X" % item_type)


def get_packet(stream):
    """
    Read a packet from a stream
    """
    (pkt_len, pkt_type) = get_struct("<ii", stream)
    pkt = {}

    if pkt_type == 126:
        pkt["type"] = "hello"
        pkt["unknown-1"] = get_struct("<3b", stream)
        pkt["unknown-2"] = get_thing(stream)
        pkt["proto"] = get_thing(stream)
        pkt["online"] = get_thing(stream)
        pkt["version"] = get_thing(stream)
        pkt["build"] = get_thing(stream)
        pkt["name"] = get_thing(stream)

    else:
        raise Exception("Unknown packet type: %s" % pkt_type)

    return pkt
