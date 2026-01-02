import numpy as np
import os

def generate_problems():
    num_problems = 10
    horizon = 20
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {num_problems} QP problems in {output_dir}...")

    for i in range(num_problems):
        # Random dimensions
        nx = np.random.randint(2, 21) # [2, 20]
        nu = np.random.randint(1, 11) # [1, 10]
        
        # Simple Dynamics: x_{k+1} = A x_k + B u_k
        # Generating LTI system for simplicity
        A = np.random.randn(nx, nx)
        # Normalize spectral radius to be around 1 for stability
        # This prevents the states from exploding over the horizon
        spectral_radius = np.max(np.abs(np.linalg.eigvals(A)))
        if spectral_radius > 0:
            A = A / spectral_radius
        
        B = np.random.randn(nx, nu)
        
        # Cost function: sum(0.5 * x_k^T Q x_k + 0.5 * u_k^T R u_k) + 0.5 * x_N^T Q_N x_N
        # Q >= 0, R > 0
        # Generate random positive semidefinite Q
        Q_temp = np.random.randn(nx, nx)
        Q = Q_temp.T @ Q_temp
        Q = Q / np.linalg.norm(Q) # Normalize
        
        # Generate random positive definite R
        R_temp = np.random.randn(nu, nu)
        R = R_temp.T @ R_temp + 1e-2 * np.eye(nu) # Add regularization
        R = R / np.linalg.norm(R) # Normalize

        # Terminal cost Q_N (often same as Q or solution to ARE, here just random PSD)
        Q_e_temp = np.random.randn(nx, nx)
        Q_e = Q_e_temp.T @ Q_e_temp
        Q_e = Q_e / np.linalg.norm(Q_e)

        # Store matrices
        # We store the LTI matrices. If time-varying is needed, these can be replicated.
        filename = os.path.join(output_dir, f'prob_{i}.npz')
        np.savez(
            filename,
            A=A,
            B=B,
            Q=Q,
            R=R,
            Q_e=Q_e,
            N=horizon,
        )
        print(f"Generated {filename}: nx={nx}, nu={nu}, N={horizon}")

if __name__ == "__main__":
    np.random.seed(42) # For reproducibility
    generate_problems()
