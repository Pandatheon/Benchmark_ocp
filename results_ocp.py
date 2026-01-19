"""Test case results."""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas

from problem_ocp import parametric_QP_Problem
from test_set_ocp import TestSet


class Results:
    """Test set results.

    Attributes:
        df: Data frame storing the results.
        file_path: Path to the results CSV file.
        test_set: Test set from which results were produced.
    """

    df: pandas.DataFrame
    file_path: Optional[Path]
    test_set: TestSet

    @staticmethod
    def read_from_file(path: Union[str, Path]) -> Optional[pandas.DataFrame]:
        """Load a pandas dataframe from a CSV or Parquet file.

        Args:
            path: Path to the file to load.

        Returns:
            Loaded dataframe, or None if the file does not exist.
        """
        file_path = Path(path)
        if not file_path.exists():
            return None

        read_func = (
            pandas.read_csv
            if file_path.suffix == ".csv"
            else pandas.read_parquet
        )
        df = read_func(file_path)
        return df

    def __init__(
        self, file_path: Optional[Union[str, Path]], test_set: TestSet
    ):
        """Initialize results.

        Args:
            file_path: Path to the results file (format: CSV or Parquet), or
                `None` if there is no file associated with these results.
            test_set: Test set from which results were produced.
        """
        df = pandas.DataFrame(
            [],
            columns=[
                "problem",
                "solver",
                "settings",
                "cost",
                "iterations",
                "runtime",
                "status",
            ],
        ).astype(
            {
                "problem": str,
                "solver": str,
                "settings": str,
                'cost': float,
                'iterations': int,
                "runtime": float,
                "status": int,
            }
        )

        if file_path is not None:
            df_from_file = Results.read_from_file(file_path)
            if df_from_file is not None:
                df = pandas.concat([df, df_from_file])

        # Filter out problems from the CSV that are in the test set
        for subdir in test_set.subdirs:
            ocp_template = test_set.create_OCP_template(subdir)
            problems = set(ocp_problem.ocp.name for ocp_problem in test_set.iter(ocp_template, subdir))
        test_set_df = df[df["problem"].isin(problems)]
        complementary_df = df[~df["problem"].isin(problems)]

        self.__complementary_df = complementary_df
        self.df = test_set_df
        self.file_path = Path(file_path) if file_path is not None else None
        self.test_set = test_set

    def write(self, path: Optional[Union[str, Path]] = None) -> None:
        """Write results to their CSV file for persistence.

        Args:
            path: Optional path to a separate file to write to.
        """
        path_check = path or self.file_path
        save_path = Path(path_check)
        save_df = pandas.concat([self.df, self.__complementary_df])
        save_df = save_df.sort_values(by=["problem", "solver", "settings"])
        if save_path.suffix == ".csv":
            save_df.to_csv(save_path, index=False)
        elif save_path.suffix == ".parquet":
            save_df.to_parquet(save_path, index=False)

    def update(
        self,
        problem: parametric_QP_Problem,
        solver: str,
        settings: str,
        context: dict,
    ) -> None:
        """Update entry for a given (problem, solver) pair.

        Args:
            problem: Problem solved.
            solver: Solver name.
            settings: Solver settings.
            solution: Solution found by the solver.
            runtime: Duration the solver took, in seconds.
        """
        self.df = self.df.drop(
            self.df.index[
                (self.df["problem"] == problem.ocp.name)
                & (self.df["solver"] == solver)
                & (self.df["settings"] == settings)
            ]
        )
        self.df = pandas.concat(
            [
                self.df,
                pandas.DataFrame(
                    {
                        "problem": [problem.ocp.name],
                        "solver": [solver],
                        "settings": [settings],
                        "cost": [context['cost']],
                        'iterations': [context['iterations']],
                        "runtime": [context['runtime']],
                        "status": [context['status']],
                    }
                ),
            ],
            ignore_index=True,
        )