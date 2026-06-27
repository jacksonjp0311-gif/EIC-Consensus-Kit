"""Operator crypto helpers for EIC attestations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyPair:
    public_key: str
    private_key: str


def keygen() -> KeyPair:
    """Generate an Ed25519 keypair as raw hex strings."""

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
    except Exception as exc:
        raise RuntimeError("key generation requires the optional 'cryptography' package; install .[crypto] or .[dev]") from exc

    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    return KeyPair(
        public_key=public.public_bytes(Encoding.Raw, PublicFormat.Raw).hex(),
        private_key=private.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex(),
    )


def sign_root(private_key_hex: str, root: str, node_id: str) -> str:
    """Sign ``node_id:root`` with a raw Ed25519 private key."""

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except Exception as exc:
        raise RuntimeError("root signing requires the optional 'cryptography' package; install .[crypto] or .[dev]") from exc

    private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    return private.sign(f"{node_id}:{root}".encode("utf-8")).hex()

