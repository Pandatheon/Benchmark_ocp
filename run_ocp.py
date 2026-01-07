"""Main function of the benchmark."""

from time import perf_counter

from tqdm import tqdm
from test_set_ocp import TestSet
from results_ocp import Results

from acados_template import AcadosOcpSolver
from problem_ocp import parametric_QP_Problem

def solve_problem(ocp_solver: AcadosOcpSolver, ocp_problem: parametric_QP_Problem) -> dict:
    """Solve the given OCP problem.

    Args:
        OCP_problem: The OCP problem to solve.
    """
    ctx = {}
    for i in range(ocp_problem.ocp.solver_options.N_horizon + 1):
        param_value = ocp_problem.param_manager.get_p_stagewise_values(i)
        ocp_solver.set(i, 'p', param_value)
    start_time = perf_counter()
    ctx['status'] = ocp_solver.solve()
    ctx['runtime'] = perf_counter() - start_time
    ctx['cost'] = ocp_solver.get_cost()
    return ctx

def run(
    test_set: TestSet,
    results: Results,
    verbose: bool = False,
) -> None:
    """Run a given test set and store results.
    """

    progress_bar = None
    if verbose:
        nb_problems = test_set.count_problems()
        nb_solvers = len(test_set.solvers)
        nb_settings = len(test_set.solver_settings)
        progress_bar = tqdm(
            total=nb_problems * nb_solvers * nb_settings,
            initial=0,
        )

    for solver in test_set.solvers:
        for settings in test_set.solver_settings:
            ocp_solver = None
            progress_bar.set_description(f"Solver: {solver}, Setting: {settings}")
            for subdir in test_set.subdirs:
                ocp_template = test_set.create_OCP_template(subdir, solver, settings)
                ocp_solver = AcadosOcpSolver(ocp_template.ocp, verbose=False)
                for ocp_problem in test_set.iter(ocp_template, subdir):
                    ctx = solve_problem(ocp_solver, ocp_problem)
                    results.update(ocp_problem, solver, settings, ctx)
                    if progress_bar is not None:
                        progress_bar.update(1)
        results.write()

    if progress_bar is not None:
        progress_bar.close()
