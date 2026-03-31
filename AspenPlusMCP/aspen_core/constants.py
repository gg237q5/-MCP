# -*- coding: utf-8 -*-
"""
Centralized constants for Aspen Plus COM interface.
All COM-related constants should be defined here for easy management.
"""


# ============================================================
# Export Type Constants (HAPEXPType)
# Used by: Export method in core.py
# ============================================================
class ExportType:
    """Export file type constants for Aspen Plus Export method."""
    BACKUP = 1           # Backup file (.bkp)
    REPORT = 2           # Report file (.rep)
    SUMMARY = 3          # Summary file (.sum)
    INPUT = 4            # Input file (.inp) - without graphics
    INPUT_GRAPHICS = 5   # Input file with graphics (.inp)

    # Mapping from string to integer for MCP tool
    STRING_MAP = {
        "bkp": BACKUP,
        "rep": REPORT,
        "sum": SUMMARY,
        "inp": INPUT,
        "inp_graphics": INPUT_GRAPHICS
    }

    # Descriptions for each export type
    DESCRIPTIONS = {
        BACKUP: "Backup file (.bkp) - Complete model backup",
        REPORT: "Report file (.rep) - Simulation results report",
        SUMMARY: "Summary file (.sum) - Simulation summary",
        INPUT: "Input file (.inp) without graphics - Flowsheet auto-arranges on reopen",
        INPUT_GRAPHICS: "Input file (.inp) with graphics - Preserves flowsheet layout"
    }

    @classmethod
    def get_value(cls, type_str: str) -> int:
        """Convert string type to integer constant."""
        if type_str not in cls.STRING_MAP:
            raise ValueError(f"Invalid export type: {type_str}. Valid types: {list(cls.STRING_MAP.keys())}")
        return cls.STRING_MAP[type_str]

    @classmethod
    def get_description(cls, type_val: int) -> str:
        """Get description for export type."""
        return cls.DESCRIPTIONS.get(type_val, "Unknown export type")


# ============================================================
# Run Status Constants
# Used by: RunStatus method in core.py
# ============================================================
class RunStatus:
    """Run status constants for Aspen Plus simulation results."""
    AVAILABLE = 1    # Simulation completed successfully
    WARNING = 4      # Simulation completed with warnings
    ERROR = 32       # Simulation completed with errors


# ============================================================
# Block Port Types (for future use)
# ============================================================
class PortDirection:
    """Port direction constants."""
    IN = "IN"
    OUT = "OUT"


# ============================================================
# Stream Types
# ============================================================
class StreamType:
    """Stream type constants."""
    MATERIAL = "MATERIAL"
    HEAT = "HEAT"
    WORK = "WORK"
