import json
import os
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

def convert_npz_to_json(npz_file, output_dir):
    """Convert .npz file to JSON format similar to acados_ocp_qp.json"""
    
    # Load the .npz file
    data = np.load(npz_file)
    
    # Extract data
    A = data['A']  # Shape: (nx, nx)
    B = data['B']  # Shape: (nx, nu)
    Q = data['Q']  # Shape: (nx, nx)
    R = data['R']  # Shape: (nu, nu)
    N = int(data['N'])  # Number of time steps
    
    # Create JSON structure
    json_data = {}
    
    # Add A matrices for each time step (0 to N-1)
    for i in range(N):
        json_data[f'A_{i}'] = A.tolist()
    
    # Add B matrices for each time step (0 to N-1)
    for i in range(N):
        json_data[f'B_{i}'] = B.tolist()
    
    # Add Q matrices for each time step (0 to N-1) and terminal Q_e at step N
    for i in range(N+1):
        json_data[f'Q_{i}'] = Q.tolist()
    
    # Add R matrices for each time step (0 to N-1)
    for i in range(N):
        json_data[f'R_{i}'] = R.tolist()
    
    # Determine output filename
    npz_filename = os.path.basename(npz_file)
    json_filename = npz_filename.replace('.npz', '.json')
    output_path = os.path.join(output_dir, json_filename)
    
    # Write JSON file
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=4)
    
    print(f"Converted {npz_filename} -> {json_filename}")
    return output_path
