# liqi_pb2.py

from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool
from google.protobuf import message_factory

pool = descriptor_pool.DescriptorPool()

fds = descriptor_pb2.FileDescriptorSet()

with open("./proto/liqi.desc", "rb") as f:
    fds.ParseFromString(f.read())

# Older bundled descriptors predate Unity's server-provided emoji permissions.
# Extend only this known field; updated descriptors already contain it.
for file in fds.file:
    for message in file.message_type:
        if message.name == 'Character' and not any(f.number == 9 for f in message.field):
            message.field.add(name='enabled_emoji', number=9,
                              label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED,
                              type=descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
    pool.Add(file)

factory = message_factory.MessageFactory(pool)

for file in fds.file:
    for message in file.message_type:
        globals()[message.name] = factory.GetPrototype(
            pool.FindMessageTypeByName(
                f"{file.package}.{message.name}"
            )
        )