
SUPER_DECOLATOR = "(super)"
TRACE_END_DECOLATOR = " (trace end)"
ASYNC_DECOLATOR = " (async)"
INHERITED_DECOLATOR = "(inherited)"
SIGNAL_DECOLATOR = "(signal)"
DECOLATOR_DECOLATOR = "(decorator)"
RECURSION_DECOLATOR = "(recursion)"
TIMESTAMP_DECOLATOR = " [added on {}]"

DECOLATORS = [
    SUPER_DECOLATOR,
    TRACE_END_DECOLATOR,
    ASYNC_DECOLATOR,
    INHERITED_DECOLATOR,
    SIGNAL_DECOLATOR,
    DECOLATOR_DECOLATOR
]

REDIS_KEY_OPERATION_HISTORY = "operation_history"

LIMIT_SAVE_HISTORY = 3

MSG_NOT_REGISTERED_INHERIT = "The class is not registered as a subclass."

MSG_REACHED_DEPTH_LIMIT = "... (depth limit reached)"

MSG_DUPLICATION="... (Omitted due to duplication)"