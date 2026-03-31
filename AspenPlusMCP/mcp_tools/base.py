from typing import Any, Optional

class BaseHandler:
    """
    Base handler mixin class.
    Expected to be mixed into the main AspenMCPServer class.
    """
    aspen_instance: Any
