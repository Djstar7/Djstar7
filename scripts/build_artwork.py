#!/usr/bin/env python3
"""Rebuild the DJSTAR7 cover, products, stack and method artwork."""
try:
    from .artwork import main
except ImportError:
    from artwork import main

if __name__ == "__main__":
    main()
