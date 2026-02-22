"""
ConversionError — raised when strict-mode conversion encounters unsupported content.
"""


class ConversionError(Exception):
    """Raised by ConversionContext.warn() when strict=True and a UCIS feature
    cannot be represented by the target format.

    Args:
        message: Description of the unsupported feature.
    """
