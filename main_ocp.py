"""Main script for running OCP benchmarks."""

from results_ocp import Results
from run_ocp import run
from test_set_ocp import TestSet
from plot_metric_ocp import plot_metric

def main():
    """
    Main function of the script.
    """
    test_set = TestSet()
    result_path = f"results/qpbenchmark_results.csv"
    results = Results(file_path=result_path, test_set=test_set)

    run(
        test_set,
        results,
        designated_solvers=['PARTIAL_CONDENSING_HPIPM',
                            'FULL_CONDENSING_QPOASES',
                            'FULL_CONDENSING_HPIPM',],
        verbose=True,
    )

    plot_metric(
        metric="runtime",
        df=results.df,
        settings="default",
        test_set=test_set,
        solvers=[
            'PARTIAL_CONDENSING_HPIPM',
            'FULL_CONDENSING_QPOASES',
            'FULL_CONDENSING_HPIPM',
        ],
        linewidth=2.0,
        savefig="results/qpbenchmark_runtime.png",
    )


if __name__ == "__main__":
    main()
