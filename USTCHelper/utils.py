from typing import Tuple, Optional

def assertOfType(param, T: type, paramName: str):
    if type(param) != T:
        raise ValueError(f"`{paramName}` is of type `{type(param)}`, but should be `{T}`.")

def seParams(params: Optional[str]) -> Tuple[str, Optional[str]]:
    # seParams = separate params
    if params == None:
        return None, None
    assertOfType(params, str, "params")
    paramList = params.strip().split(' ', 1)
    if len(paramList) == 1:
        return paramList[0], None
    else:
        return paramList[0], paramList[1]
