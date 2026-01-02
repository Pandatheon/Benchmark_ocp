"""class for test sets."""

import os
from typing import Dict, Iterator, Optional, Set, Tuple

from problem_ocp import QP_Problem
from solver_settings_ocp import SolverSettings

import casadi as ca
from acados_template import AcadosOcp, AcadosModel


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

    def __init__(self):
        """Initialize test set."""

        candidate_solvers = SolverSettings.IMPLEMENTED_SOLVERS
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

    def __iter__(self) -> Iterator[QP_Problem]:
        """Yield test-set problems one by one."""
        for fname in os.listdir(self.data_dir):
            if fname.endswith(".npz"):
                yield QP_Problem.load(os.path.join(self.data_dir, fname))

    def count_problems(self) -> int:
        """Count the number of problems in the test set."""
        return sum(1 for _ in self)

    def formulate_OCP_problem(self, problem: QP_Problem, solver: str, settings: str) -> AcadosOcp:
        '''
        Formulate an OCP problem for acados from QP_Problem.
        '''
        N = int(problem.N)
        model = AcadosModel()
        model.name = 'linear_system'

        # set up model
        nx = problem.A.shape[0]
        nu = problem.B.shape[1]

        x = ca.SX.sym("x", nx)
        u = ca.SX.sym("u", nu)
        model.x = x
        model.u = u

        # dynamics
        A = problem.A
        B = problem.B
        f_expl = ca.mtimes(A, x) + ca.mtimes(B, u)
        model.f_expl_expr = f_expl

        ocp = AcadosOcp()
        ocp.model = model

        # get matrices
        Q = problem.Q
        R = problem.R
        Q_e = problem.Q_e

        # set up cost
        x_res = ocp.model.x
        u_res = ocp.model.u
        ocp.cost.cost_type = "EXTERNAL"
        ocp.model.cost_expr_ext_cost = 0.5 * (x_res.T @ Q @ x_res + u_res.T @ R @ u_res)
        ocp.cost.cost_type_e = "EXTERNAL"
        ocp.model.cost_expr_ext_cost_e = 0.5 * (x_res.T @ Q_e @ x_res)

        # set options
        ocp.solver_options.tf = 1.0*N
        ocp.solver_options.N_horizon = N
        ocp.solver_options.qp_solver = solver
        if settings == 'default':
            ocp.solver_options.hessian_approx = 'EXACT'
            pass

        return ocp