# 捕获websocket数据并解析雀魂"动作"语义为Json
import json
from struct import unpack
import base64
from enum import Enum
from typing import List, Dict
from google.protobuf.json_format import MessageToDict
from proto import liqi_pb2, basic_pb2


class MsgType(Enum):
    Notify = 1
    Req = 2
    Res = 3


class LiqiProto:
    def __init__(self):
        # 解析一局的WS消息队列
        self.tot = 0  # 当前总共解析的包数量
        # (method_name:str,pb.MethodObj) for 256 sliding windows; req->res
        self.res_type = {}  # int -> (method_name,pb2obj)
        self.jsonProto = json.load(open('./proto/liqi.json', 'r'))

    def parse(self, flow_msg):
        # parse一帧WS flow msg，要求按顺序parse
        buf = flow_msg.content
        from_client = flow_msg.from_client
        result = {}
        msg_block = basic_pb2.BaseMessage()
        msg_type = MsgType(buf[0])  # 通信报文类型
        if msg_type == MsgType.Notify:
            msg_block.ParseFromString(buf[1:])      # 解析剩余报文结构
            method_name = msg_block.method_name
            _, lq, message_name = method_name.split('.')
            liqi_pb2_notify = getattr(liqi_pb2, message_name)
            proto_obj = liqi_pb2_notify.FromString(msg_block.data)
            dict_obj = MessageToDict(
                proto_obj, preserving_proto_field_name=True, including_default_value_fields=True)
            if 'data' in dict_obj:
                B = base64.b64decode(dict_obj['data'])
                action_proto_obj = getattr(
                    liqi_pb2, dict_obj['name']).FromString(decode(B))
                action_dict_obj = MessageToDict(
                    action_proto_obj, preserving_proto_field_name=True, including_default_value_fields=True)
                dict_obj['data'] = action_dict_obj
            msg_id = self.tot
        else:
            msg_id = unpack('<H', buf[1:3])[0]   # 小端序解析报文编号(0~255)
            msg_block.ParseFromString(buf[3:])
            if msg_type == MsgType.Req:
                assert (msg_id < 1 << 16)
                # assert(len(msg_block) == 2)
                assert (msg_id not in self.res_type)
                method_name = msg_block.method_name
                _, lq, service, rpc = method_name.split('.')
                proto_domain = self.jsonProto['nested'][lq]['nested'][service]['methods'][rpc]
                liqi_pb2_req = getattr(liqi_pb2, proto_domain['requestType'])
                proto_obj = liqi_pb2_req.FromString(msg_block.data)
                dict_obj = MessageToDict(
                    proto_obj, preserving_proto_field_name=True, including_default_value_fields=True)
                self.res_type[msg_id] = (method_name, getattr(
                    liqi_pb2, proto_domain['responseType']))  # wait response
            elif msg_type == MsgType.Res:
                assert (len(msg_block.method_name) == 0)
                assert (msg_id in self.res_type)
                method_name, liqi_pb2_res = self.res_type.pop(msg_id)
                proto_obj = liqi_pb2_res.FromString(msg_block.data)
                dict_obj = MessageToDict(
                    proto_obj, preserving_proto_field_name=True, including_default_value_fields=True)
        result = {'id': msg_id, 'type': msg_type,
                  'method': method_name, 'data': dict_obj}
        self.tot += 1
        return result


def fromProtobuf(buf) -> List[Dict]:
    """
    dump the struct of protobuf,观察报文结构
    buf: protobuf bytes
    """
    p = 0
    result = []
    while (p < len(buf)):
        block_begin = p
        block_type = (buf[p] & 7)
        block_id = buf[p] >> 3
        p += 1
        if block_type == 0:
            # varint
            block_type = 'varint'
            data, p = parseVarint(buf, p)
        elif block_type == 2:
            # string
            block_type = 'string'
            s_len, p = parseVarint(buf, p)
            data = buf[p:p+s_len]
            p += s_len
        else:
            raise Exception('unknow type:', block_type, ' at', p)
        result.append({'id': block_id, 'type': block_type,
                       'data': data, 'begin': block_begin})
    return result


def toVarint(x: int) -> bytes:
    data = 0
    base = 0
    length = 0
    if x == 0:
        return b'\x00'
    while (x > 0):
        length += 1
        data += (x & 127) << base
        x >>= 7
        if x > 0:
            data += 1 << (base+7)
        base += 8
    return data.to_bytes(length, 'little')


def toProtobuf(data: List[Dict]) -> bytes:
    """
    Inverse operation of 'fromProtobuf'
    """
    result = b''
    for d in data:
        if d['type'] == 'varint':
            result += ((d['id'] << 3)+0).to_bytes(length=1, byteorder='little')
            result += toVarint(d['data'])
        elif d['type'] == 'string':
            result += ((d['id'] << 3)+2).to_bytes(length=1, byteorder='little')
            result += toVarint(len(d['data']))
            result += d['data']
        else:
            raise NotImplementedError
    return result


def parseVarint(buf, p):
    # parse a varint from protobuf
    data = 0
    base = 0
    while (p < len(buf)):
        data += (buf[p] & 127) << base
        base += 7
        p += 1
        if buf[p-1] >> 7 == 0:
            break
    return (data, p)


def decode(data: bytes):
    keys = [0x84, 0x5e, 0x4e, 0x42, 0x39, 0xa2, 0x1f, 0x60, 0x1c]
    data = bytearray(data)
    k = len(keys)
    d = len(data)
    for i, j in enumerate(data):
        u = (23 ^ d) + 5 * i + keys[i % k] & 255
        data[i] ^= u
    return bytes(data)
