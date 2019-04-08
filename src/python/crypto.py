import os
import hmac
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from binascii import unhexlify

from pprint import pprint
import json

import sys;

#print('Xbox-Debug Python POC');
#print('input: '+ sys.argv[1])

_backend = default_backend()

CURVE_MAP = {
    0x00: ec.SECP256R1,
    0x01: ec.SECP384R1,
    0x02: ec.SECP521R1
}

PUBLIC_KEY_TYPE_MAP = {v: k for k, v in CURVE_MAP.items()}

def cryptoSign(foreign_public_key, privkey=None, pubkey=None):
    if not isinstance(foreign_public_key, ec.EllipticCurvePublicKey):
        raise ValueError("Unsupported public key format, \
            expected EllipticCurvePublicKey")

    if privkey and not isinstance(privkey, ec.EllipticCurvePrivateKey):
        raise ValueError("Unsupported private key format, \
            expected EllipticCurvePrivateKey")
    elif not privkey:
        privkey = ec.generate_private_key(
            foreign_public_key.curve, _backend
        )

    if pubkey and not isinstance(pubkey, ec.EllipticCurvePublicKey):
        raise ValueError("Unsupported public key format, \
            expected EllipticCurvePublicKey")
    elif not pubkey:
        _pubkey = privkey.public_key()
    else:
        _pubkey = pubkey

    secret = privkey.exchange(ec.ECDH(), foreign_public_key)
    salted_secret = secret
    #for salt in _kdf_salts:
    #    salted_secret = salt.apply(salted_secret)
    salted_secret = unhexlify('D637F1AAE2F0418C')+salted_secret+unhexlify('A8F81A574E228AB7')

    _expanded_secret = hashlib.sha512(salted_secret).digest()
    _encrypt_key = _expanded_secret[:16]
    _iv_key = _expanded_secret[16:32]
    _hash_key = _expanded_secret[32:]

    _pubkey_type = PUBLIC_KEY_TYPE_MAP[type(_pubkey.curve)]
    _pubkey_bytes = _pubkey.public_numbers().encode_point()[1:]
    _foreign_pubkey = foreign_public_key

    return {
        "public_key": str(_pubkey_bytes).encode('hex'),
        "secret": str(_expanded_secret).encode('hex')
    }

def loadPublicKey(foreign_public_key, public_key_type=None):
    """
    Initialize Crypto context with foreign public key in
    bytes / hexstring format.

    Args:
        foreign_public_key (bytes): Console's public key
        public_key_type (:obj:`.PublicKeyType`): Public Key Type

    Returns:
        :obj:`.Crypto`: Instance
    """

    if not isinstance(foreign_public_key, bytes):
        raise ValueError("Unsupported foreign public key format, \
            expected bytes")

    if public_key_type is None:
        keylen = len(foreign_public_key)
        if keylen == 0x41:
            public_key_type = ec.SECP256R1
        elif keylen == 0x61:
            public_key_type = ec.SECP384R1
        elif keylen == 0x85:
            public_key_type = ec.SECP521R1
        else:
            raise ValueError("Invalid public keylength")

    curve = public_key_type
    nums = ec.EllipticCurvePublicNumbers.from_encoded_point(
        curve(), foreign_public_key
    )
    foreign_public_key = nums.public_key(_backend)
    return foreign_public_key

public_key = sys.argv[1].decode("hex")

print(json.dumps(cryptoSign(loadPublicKey(public_key))))