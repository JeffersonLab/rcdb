
class OverrideConditionTypeError(Exception):
    pass


class NoConditionTypeFound(Exception):
    pass


class OverrideConditionValueError(Exception):
    pass


class NoRunFoundError(Exception):
    pass


class QueryFormatError(Exception):
    def __init__(self, msg='Error in query format', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
    pass


class QueryEvaluationError(Exception):
    def __init__(self, msg='Error during execution of select query', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
    pass

class SqlSchemaVersionError(Exception):
    pass
