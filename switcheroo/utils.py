def format_md5_fingerprint(public_key):
    """
    Get the MD5 fingerprint of a public key.

    :param public_key:
    :return: an MD5 fingerprint string
    :rtype: str
    """
    return public_key.get_fingerprint(hash_name="md5")[4:]


def format_sha2_fingerprint(public_key):
    """
    Get the SHA2 fingerprint of a public key.

    :param public_key:
    :return: a SHA2 fingerprint string
    :rtype: str
    """
    return public_key.get_fingerprint(hash_name="sha256")[7:]
