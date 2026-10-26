"""Tool registry - every capability the agent has is listed here.

To give the agent a new job, add a module in this package that defines a
`TOOLS` list of `@beta_tool` functions, then import it below. Nothing else
needs to change: the agent picks up every tool in `ALL_TOOLS`.
"""

from . import support_allowance, utilities

ALL_TOOLS = [
    *support_allowance.TOOLS,
    *utilities.TOOLS,
]
