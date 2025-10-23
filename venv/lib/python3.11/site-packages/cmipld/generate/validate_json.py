#!/usr/bin/env python3
"""
DEPRECATED: This module has been moved to cmipld.utils.validate_json

This file is kept for backward compatibility.
"""

import warnings
from ..utils.validate_json import *

warnings.warn(
    "cmipld.generate.validate_json is deprecated. Use cmipld.utils.validate_json instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, ensure main() is available
if __name__ == "__main__":
    main()
