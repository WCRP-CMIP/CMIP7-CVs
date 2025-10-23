#!/usr/bin/env python3
"""
Command-line interface for CMIP-LD offline server tools.
"""

from .offline_patched import main

if __name__ == "__main__":
    exit(main())
