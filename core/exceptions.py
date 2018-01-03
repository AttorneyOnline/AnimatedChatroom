class AssetError(Exception):
    """
    Raised when an error occurs during the reading of an asset.
    """
    pass

class BadHashError(AssetError):
    """
    Raised when the hash indicated in the asset info does not match
    the hash of the content.
    """
    pass

class MissingEntryError(AssetError):
    """
    Raised when a entry in a manifest was expected but not found.
    """
    pass