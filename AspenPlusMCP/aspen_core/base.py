# -*- coding: utf-8 -*-
"""
Base class for Aspen Plus COM interface.
Contains the core instance management.
"""


class APBase:
    """Base class for Aspen Plus COM interface."""
    
    def __init__(self):
        """Initialize the AP class."""
        self.aspen = None

    def __del__(self):
        """Close the AspenFile when AP class is destroyed."""
        try:
            if self.aspen is not None:
                self.aspen.Close()
                print("\nClosing AspenFile...")
        except Exception:
            pass
