"""Matrix-vector representation of a quadratic program."""

import numpy as np
import casadi as ca
from acados_template import AcadosOcp, AcadosParamManager, AcadosParam
from utils import read_matrix_list

class parametric_QP_Problem():
    """
    Quadratic program with OCP structure.
    Q and R as cost matrices,
    A and B as dynamics matrices.
    """

    def __init__(
        self,
        N: int,
        nx: int,
        nu: int,
        solver: str,
        settings: str,
    ):
        '''
        Formulate an OCP problem for acados from QP_Problem.
        '''
        ocp = AcadosOcp()
        # params
        A_param = AcadosParam("A", np.zeros((nx, nx)))
        B_param = AcadosParam("B", np.zeros((nx, nu)))
        Q_param = AcadosParam("Q", np.zeros((nx, nx)))
        R_param = AcadosParam("R", np.zeros((nu, nu)))

        param_manager = AcadosParamManager([A_param, B_param, Q_param, R_param])
        param_manager.N_horizon = N

        ocp.model.name = 'parametric_QP_OCP'

        # set up model
        x = ca.SX.sym("x", nx)
        u = ca.SX.sym("u", nu)
        ocp.model.x = x
        ocp.model.u = u
        ocp.model.p = param_manager.get_p_stagewise_expression()

        # dynamics
        A_expr = param_manager.get_expression("A")
        B_expr = param_manager.get_expression("B")
        f_expl = ca.mtimes(A_expr, x) + ca.mtimes(B_expr, u)
        ocp.model.disc_dyn_expr = f_expl

        # get matrices
        Q = param_manager.get_expression("Q")
        R = param_manager.get_expression("R")

        # set up cost
        x_res = ocp.model.x
        u_res = ocp.model.u
        ocp.cost.cost_type = "EXTERNAL"
        ocp.model.cost_expr_ext_cost = 0.5 * (x_res.T @ Q @ x_res + u_res.T @ R @ u_res)
        ocp.cost.cost_type_e = "EXTERNAL"
        ocp.model.cost_expr_ext_cost_e = 0.5 * (x_res.T @ Q @ x_res)

        ocp.parameter_values = param_manager.get_p_stagewise_values(stage=0)
        # set options
        ocp.solver_options.tf = 1.0*N
        ocp.solver_options.N_horizon = N
        ocp.solver_options.qp_solver = solver if solver is not None else 'PARTIAL_CONDENSING_HPIPM'
        ocp.solver_options.hessian_approx = 'EXACT'
        ocp.solver_options.integrator_type = 'DISCRETE'
        if settings == 'default':
            pass

        self.ocp = ocp
        self.param_manager = param_manager

    def populate_manager(self, file: str):
        """Load problem from file.
        Args:
            file: Path to the file to read.
        """
        Q_list = read_matrix_list(file, "Q")
        R_list = read_matrix_list(file, "R")
        A_list = read_matrix_list(file, "A")
        B_list = read_matrix_list(file, "B")
        for i in range(self.ocp.solver_options.N_horizon):
            self.param_manager.set_value(name="A", value=A_list[i], stage=i)
            self.param_manager.set_value(name="B", value=B_list[i], stage=i)
            self.param_manager.set_value(name="Q", value=Q_list[i], stage=i)
            self.param_manager.set_value(name="R", value=R_list[i], stage=i)
        self.param_manager.set_value(name="Q", value=Q_list[-1], stage=self.ocp.solver_options.N_horizon)