"""class for test sets."""

import os
from typing import Dict, Iterator, Optional, Set, Tuple

from problem_ocp import parametric_QP_Problem
from solver_settings_ocp import SolverSettings

from utils import read_problem_size_from_dir

class TestSet():
    """
    Test set of OCP problems.
    """

    @property
    def description(self) -> str:
        return "Randomly generated model predictive control problems"

    @property
    def title(self) -> str:
        return "Model predictive control test set in OCP structure"

    def __init__(self, 
                 designated_solvers: list[str] = SolverSettings.IMPLEMENTED_SOLVERS, 
                 designated_problem_sets: list[str] = None):
        """Initialize test set."""

        candidate_solvers = set(
            solver 
            for solver in SolverSettings.IMPLEMENTED_SOLVERS 
            if solver in designated_solvers) 
        solvers = set(
            solver
            for solver in candidate_solvers
            if SolverSettings.is_complied(solver)
        )
        for solver in candidate_solvers - solvers:
            print(f"Solver '{solver}' is not complied, skipped ")

        self.solvers = solvers
        self.solver_settings = SolverSettings.SOLVER_SETTINGS

        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "data")
        self.data_dir = data_dir
        self.subdirs = [subdir for subdir in os.listdir(self.data_dir)
                        if designated_problem_sets is None or subdir in designated_problem_sets]

    def iter(self, ocp_template: parametric_QP_Problem, subdir) -> Iterator[parametric_QP_Problem]:
        """populate parameter manager one by one."""
        for fname in os.listdir(os.path.join(self.data_dir, subdir)):
            if fname.endswith('.json'):
                ocp_template.ocp.name = subdir + "_" + fname.replace('.json','')
                ocp_template.populate_manager(os.path.join(self.data_dir, subdir, fname))
                yield ocp_template

    def create_OCP_template(self, subdir: str, solver: str = None, settings: str = None) -> parametric_QP_Problem:
        N, nx, nu = read_problem_size_from_dir(subdir)
        ocp_template = parametric_QP_Problem(
            N=N,
            nx=nx,
            nu=nu,
            solver=solver,
            settings=settings,
        )
        return ocp_template

    def count_problems(self) -> int:
        """Count the number of problems in the test set."""
        N_problems = 0
        for subdir in self.subdirs:
            json_files = [f for f in os.listdir(os.path.join(self.data_dir, subdir)) if f.endswith('.json')]
            N_problems += len(json_files)
        return N_problems