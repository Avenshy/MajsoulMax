# liqi_pb2.py

from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool
from google.protobuf import message_factory

pool = descriptor_pool.DescriptorPool()

fds = descriptor_pb2.FileDescriptorSet()

with open("./proto/liqi.desc", "rb") as f:
    fds.ParseFromString(f.read())

for file in fds.file:
    pool.Add(file)

factory = message_factory.MessageFactory(pool)

for file in fds.file:
    for message in file.message_type:
        globals()[message.name] = factory.GetPrototype(
            pool.FindMessageTypeByName(
                f"{file.package}.{message.name}"
            )
        )