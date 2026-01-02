"""Solver settings."""

from typing import Any, Dict, Iterator, Set

import numpy as np


class SolverSettings:
    """Settings for multiple solvers."""

    IMPLEMENTED_SOLVERS: Set[str] = set(
        [
        'PARTIAL_CONDENSING_HPIPM', 
        'FULL_CONDENSING_QPOASES', 
        'FULL_CONDENSING_HPIPM', 
        'PARTIAL_CONDENSING_QPDUNES',
        'PARTIAL_CONDENSING_OSQP', 
        'PARTIAL_CONDENSING_CLARABEL', 
        'FULL_CONDENSING_DAQP'
        ]
    )

    SOLVER_SETTINGS: Set[str] = set(
        [
        'default',
        ]
    )

    @staticmethod
    def is_complied(solver: str) -> bool:
        # TODO: check solver compliance
        return True