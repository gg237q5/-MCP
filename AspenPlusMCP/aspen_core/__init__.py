# -*- coding: utf-8 -*-
"""
Aspen Plus COM Interface - Modular Package

This package provides a modular structure for interacting with Aspen Plus
through COM interface. The main AP class combines all mixin functionalities.

Module structure aligned with mcp_tools/:
- core.py        -> mcp_tools/core/
- blocks.py      -> mcp_tools/blocks/
- streams.py     -> mcp_tools/streams/
- components.py  -> mcp_tools/components/
- properties.py  -> mcp_tools/properties/
- simulation.py  -> mcp_tools/simulation/
- convergence.py -> mcp_tools/convergence/
- reactions.py   -> mcp_tools/reactions/
- utils.py       -> mcp_tools/utils/
"""

from .base import APBase
from .core import CoreMixin
from .blocks import BlocksMixin
from .streams import StreamsMixin
from .components import ComponentsMixin
from .properties import PropertiesMixin
from .simulation import SimulationMixin
from .convergence import ConvergenceMixin
from .reactions import ReactionsMixin
from .utils import UtilsMixin, check_name


class AP(
    CoreMixin,
    BlocksMixin,
    StreamsMixin,
    ComponentsMixin,
    PropertiesMixin,
    SimulationMixin,
    ConvergenceMixin,
    ReactionsMixin,
    UtilsMixin,
    APBase
):
    """
    Main Aspen Plus interface class.
    
    Combines all mixin classes to provide complete functionality:
    - APBase: Core instance management
    - CoreMixin: Connection + file operations (mcp_tools/core)
    - BlocksMixin: Block operations (mcp_tools/blocks)
    - StreamsMixin: Stream operations (mcp_tools/streams)
    - ComponentsMixin: Component operations (mcp_tools/components)
    - PropertiesMixin: Property specifications (mcp_tools/properties)
    - SimulationMixin: Simulation + model checking (mcp_tools/simulation)
    - ConvergenceMixin: Convergence settings (mcp_tools/convergence)
    - ReactionsMixin: Reaction operations (mcp_tools/reactions)
    - UtilsMixin: Unit utilities + decorators (mcp_tools/utils)
    """
    
    def __init__(self):
        """Initialize the AP class."""
        super().__init__()


__all__ = ['AP', 'check_name']
