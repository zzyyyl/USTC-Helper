from typing import Tuple, Optional

def assertOfType(param, T: type, paramName: str):
    if type(param) != T:
        raise ValueError(f"`{paramName}` is of type `{type(param)}`, but should be `{T}`.")

def seperateParams(params: str) -> Tuple[str, Optional[str]]:
    assertOfType(params, str, "params")
    paramList = params.strip().split(' ', 1)
    if len(paramList) == 1:
        return paramList[0], None
    else:
        return paramList[0], paramList[1]
