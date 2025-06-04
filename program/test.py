import math

def solve_N1(S, tol = 1e-8, max_iter = 50):
    r = 0.5772156649
    x = S / max(math.log(S), 1.1)
    for _ in range(max_iter):
        f   = x * (2*math.log(2*x) + 2*r - 3) - S
        df  = 2*math.log(2*x) + 2*r - 1       
        x_n = x - f/df
        if abs(x_n - x) < tol:
            return x_n
        x = x_n
    raise RuntimeError("N1 solver did not converge")

print(solve_N1(200))