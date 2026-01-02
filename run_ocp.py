#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Main function of the benchmark."""

from time import perf_counter

from tqdm import tqdm
from test_set_ocp import TestSet
from results_ocp import Results

from acados_template import AcadosOcpSolver

def solve_problem(ocp):
    """Solve the given OCP problem.

    Args:
        ocp_problem: The OCP problem to solve.

    Returns:
        cost: The cost of the OCP solution.
        runtime: The time taken to solve the problem.
    """
    ctx = {}
    ocp_solver = AcadosOcpSolver(ocp, verbose=False)
    start_time = perf_counter()
    ctx['status'] = ocp_solver.solve()
    ctx['runtime'] = perf_counter() - start_time
    ctx['cost'] = ocp_solver.get_cost()
    return ctx

def run(
    test_set: TestSet,
    results: Results,
    designated_solvers: list[str] = None,
    verbose: bool = False,
) -> None:
    """Run a given test set and store results.
    """

    nb_calls = 0
    nb_calls_since_last_save = 0

    filtered_solvers = [
        solver
        for solver in test_set.solvers
        if designated_solvers is None or solver in designated_solvers
    ]

    progress_bar = None
    if verbose:
        nb_problems = test_set.count_problems()
        nb_solvers = len(filtered_solvers)
        nb_settings = len(test_set.solver_settings)
        progress_bar = tqdm(
            total=nb_problems * nb_solvers * nb_settings,
            initial=0,
        )

    for problem in test_set:
        for solver in filtered_solvers:
            for settings in test_set.solver_settings:
                ocp_problem = test_set.formulate_OCP_problem(problem, solver, settings)
                ctx = solve_problem(ocp_problem)
                nb_calls += 1
                nb_calls_since_last_save += 1
                results.update(problem, solver, settings, ctx)
                if progress_bar is not None:
                    progress_bar.update(1)

        # Save results to file after problem has been fully processed
        if nb_calls_since_last_save > 0:
            results.write()
            nb_calls_since_last_save = 0

    if progress_bar is not None:
        progress_bar.close()