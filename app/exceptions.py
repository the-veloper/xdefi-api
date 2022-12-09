class UniswapAPIError(Exception):
    pass


class UniswapAPIConnectionError(UniswapAPIError):
    pass


class UnexpectedAPIResponseError(Exception):
    pass


class UserInterrupt(Exception):
    pass
