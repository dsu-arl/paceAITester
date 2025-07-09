#!/usr/bin/exec-suid --real -- /usr/bin/python -I

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FunctionCall:
    variable: str
    function: str
    args: List[str]
    kwargs: Dict[str, any]

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'FunctionCall':
        return cls(
            variable=data['variable'],
            function=data['function'],
            args=data['args'],
            kwargs=data['kwargs']
        )
