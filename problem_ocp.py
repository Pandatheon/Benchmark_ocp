"""Matrix-vector representation of a quadratic program."""

import os

import numpy as np


class QP_Problem():
    """
    Quadratic program with OCP structure.
    Q and R as cost matrices,
    A and B as dynamics matrices.
    """
    def __init__(
        self,
        N: int,
        Q: np.ndarray,
        R: np.ndarray,
        Q_e: np.ndarray,
        A: np.ndarray,
        B: np.ndarray,
        name: str,
    ):
        """Quadratic program in qpsolvers format."""
        self.N = N
        self.Q = Q
        self.R = R
        self.Q_e = Q_e
        self.A = A
        self.B = B
        self.name = name

    @staticmethod
    def load(file: str):
        """Load problem from file.

        Args:
            file: Path to the file to read.
        """
        name = os.path.splitext(os.path.basename(file))[0]
        loaded = np.load(file)
        return QP_Problem(
            int(loaded["N"]),
            loaded["Q"],
            loaded["R"],
            loaded["Q_e"],
            loaded["A"],
            loaded["B"],
            name,
        )