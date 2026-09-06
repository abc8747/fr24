"""
Helper functions for the gRPC+protobuf protocol.
For more information, see: https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md
"""

from __future__ import annotations
from typing import Type, TypeVar
import struct

from google.protobuf.message import Message
from ..utils import Result, Ok, Err
from typing import Protocol, Union, runtime_checkable


T_co = TypeVar("T_co", bound=Message, covariant=True)


@runtime_checkable
class SupportsToProto(Protocol[T_co]):
    def to_proto(self) -> T_co:
        """Converts the object into a protobuf message."""


T = TypeVar("T", bound=Message)


# similar to impl Into<Proto>
def to_proto(message_like: SupportsToProto[T] | T) -> T:
    return (
        message_like.to_proto()
        if isinstance(message_like, SupportsToProto)
        else message_like
    )


def encode_message(msg: Message) -> bytes:
    """Encode to a length-prefixed message."""
    msg_bytes = msg.SerializeToString()
    return (
        b"\x00"  # u8, no compression
        + struct.pack(
            ">I", len(msg_bytes)
        )  # u64, length of message, big endian
        + msg_bytes  # binary octet
    )


def parse_data(data: bytes, msg_type: Type[T]) -> Result[T, ProtoError]:
    """Decode a DATA frame (optionally, with Trailers) into a protobuf message."""
    if not data:
        return Err(GrpcError("empty DATA frame", data))
    compressed_flag = data[0]  # 1 byte unsigned int
    if compressed_flag == 1:
        return Err(GrpcError("message is compressed, not implemented", data))
    if compressed_flag != 0:
        try:  # parse trailers
            return Err(GrpcError.from_trailers(data))
        except Exception:
            return Err(
                GrpcError(
                    "unknown message, possibly wrong encoding or non-grpc", data
                )
            )
    data_len = int.from_bytes(data[1:5], byteorder="big")  # message length
    if not data_len:
        return Err(GrpcError("empty message payload", data))
    message = data[5 : 5 + data_len]  # message (in protobuf, binary octet)
    try:
        return Ok(msg_type.FromString(message))
    except Exception as e:
        return Err(ProtoParseError(f"failed to parse message: {e}", data))


class GrpcError(Exception):
    """
    When an application or runtime error occurs during an RPC a
    `Status` and `Status-Message` are delivered in `Trailers`.
    """

    def __init__(
        self,
        message: str,
        raw_data: bytes | None = None,
        *,
        status: int | None = None,
        status_message: bytes | None = None,
        status_details: bytes | None = None,
    ):
        super().__init__(message)
        self.raw_data = raw_data
        """Length-prefixed message"""
        self.status = status
        """1*DIGIT ; 0-9"""
        self.status_message = status_message
        """Percent-Encoded"""
        self.status_details = status_details
        """`google.rpc.Status` proto message"""

    @classmethod
    def from_trailers(cls, data: bytes) -> GrpcError:
        trailers = data[5:]  # skip prefix

        lines = trailers.strip().splitlines()

        status = None
        status_message = None
        status_details = None

        for line in lines:
            if line.startswith(b"grpc-status:"):
                try:
                    status = int(line[12:])
                except ValueError:
                    pass
            elif line.startswith(b"grpc-message:"):
                status_message = line[13:]
            elif line.startswith(b"grpc-status-details-bin:"):
                status_details = line[24:]

        return cls(
            "gRPC errored",
            trailers,
            status=status,
            status_message=status_message,
            status_details=status_details,
        )


class ProtoParseError(Exception):
    def __init__(self, message: str, raw_data: bytes | None = None):
        super().__init__(message)
        self.raw_data = raw_data


ProtoError = Union[GrpcError, ProtoParseError]
