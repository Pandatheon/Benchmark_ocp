import json
import numpy as np

def read_problem_size_from_dir(subdir: str) -> tuple[int, int]:
    """
    Read problem size (nx, nu) from the directory name.
    Assumes the directory name is in the format 'N_<N>_nx_<nx>_nu_<nu>'.
    """
    import re

    # e.g. 20_5*2_Problem_set -> N=20, nx=5, nu=2
    match = re.match(r"(\d+)_(\d+)\*(\d+)_Problem_set", subdir)
    if match:
        N = int(match.group(1))
        nx = int(match.group(2))
        nu = int(match.group(3))
        return N, nx, nu
    else:
        raise ValueError(f"Cannot parse problem size from directory name: {subdir}")
    
def read_matrix_list(json_path, mat_str):
    """
    Reads a list of stage-varying matrices from a dictionary where keys are of the form
    'mat_str' and returns a list of matrices.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    matrix_list = []
    for key in data.keys():
        if key.startswith(mat_str):
            matrix_list.append(np.array(data[key]))
    f.close()
    return matrix_list
    
