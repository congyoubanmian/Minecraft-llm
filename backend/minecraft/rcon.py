from __future__ import annotations

import socket
import struct
from dataclasses import dataclass


SERVERDATA_AUTH = 3
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0


@dataclass(frozen=True)
class RconConfig:
    host: str
    port: int
    password: str
    timeout: float = 5.0


class MinecraftRcon:
    """
    Minimal Minecraft RCON client.

    Kept dependency-free because the MVP only needs occasional control commands.
    FAWE paste itself is handled by Mineflayer to preserve player context.
    """

    def __init__(self, config: RconConfig):
        self.config = config

    def command(self, command: str) -> str:
        with socket.create_connection((self.config.host, self.config.port), self.config.timeout) as sock:
            sock.settimeout(self.config.timeout)
            self._send(sock, 1, SERVERDATA_AUTH, self.config.password)
            auth_id, _, _ = self._recv(sock)
            if auth_id == -1:
                raise PermissionError("RCON authentication failed")

            self._send(sock, 2, SERVERDATA_EXECCOMMAND, command.lstrip("/"))
            _, packet_type, body = self._recv(sock)
            if packet_type not in (SERVERDATA_RESPONSE_VALUE, SERVERDATA_EXECCOMMAND):
                raise RuntimeError(f"unexpected RCON packet type: {packet_type}")
            return body

    @staticmethod
    def _send(sock: socket.socket, request_id: int, packet_type: int, body: str) -> None:
        payload = struct.pack("<ii", request_id, packet_type) + body.encode("utf-8") + b"\x00\x00"
        sock.sendall(struct.pack("<i", len(payload)) + payload)

    @staticmethod
    def _recv(sock: socket.socket) -> tuple[int, int, str]:
        raw_length = _read_exact(sock, 4)
        (length,) = struct.unpack("<i", raw_length)
        payload = _read_exact(sock, length)
        request_id, packet_type = struct.unpack("<ii", payload[:8])
        body = payload[8:-2].decode("utf-8", errors="replace")
        return request_id, packet_type, body


def _read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError("RCON socket closed")
        chunks.extend(chunk)
    return bytes(chunks)
