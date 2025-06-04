import argparse, random
from traveling_network import *

GAMMA = 0.5772156649      # Euler–Mascheroni 定数

def solve_N1_from_NE(NE, tol = 1e-10, max_iter = 60):
    """
    超越方程式  NE = N1 (2 ln 2N1 + 2r - 3)  をニュートン法で解く。
    """
    # 初期値：NE / ln NE 程度で十分
    x = NE / max(math.log(NE), 1.2)
    for _ in range(max_iter):
        f  = x * (2 * math.log(2 * x) + 2 * GAMMA - 3) - NE
        df = 2 * math.log(2 * x) + 2 * GAMMA - 1
        x_new = x - f / df
        if abs(x_new - x) < tol:
            return x_new
        x = x_new
    raise RuntimeError("solve_N1_from_NE did not converge")


def solve_N1_scaled(S: float, KB: float, KG: float, dL: float = 1.0):
    Lbar = (2 * KB + KG) / (2 * KB) * dL
    NE   = S / Lbar
    N1   = solve_N1_from_NE(NE)
    return N1

# ───────────────────────────────────────────
# 1 回シミュレーションして平均値を返す関数
# ───────────────────────────────────────────
def run_once(S: float, k_b: float, k_g: float, k_r: float, alpha: float, dL: float, seed: int, sample_steps: int):
    net = TravelingNetwork(S=S, k_b=k_b, k_g=k_g, k_r=k_r, alpha=alpha, dL=dL, seed=seed)
    # 定常状態になるまで、放置
    n1 = solve_N1_scaled(S, k_b, k_g)#N_1 theoryの近似値を計算
    burn_step = 10 * (n1 / (2 * k_b))#定常状態になるまでに必要なステップ数
    print(f"S:{S}, k_b:{k_b}, k_g:{k_g}, burn_step:{burn_step}")
    for i in range(int(burn_step)):
        net.step()

    # ② 計測区間
    accum = []
    for i in range(sample_steps):
        net.step()
        accum.append(net.snapshot())

    # ③ 平均を計算
    mean = {
        key: sum(rec[key] for rec in accum) / sample_steps
        for key in accum[0]
    }
    return mean

def main():
    ap = argparse.ArgumentParser(
        description="Run a single TravelingNetwork simulation."
    )
    ap.add_argument("--S", type=float, default=200.0)
    ap.add_argument("--kb", type=float, default=0.05)
    ap.add_argument("--kg", type=float, default=0.25)
    ap.add_argument("--kr", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, default=1.0472,  # = π/3
                    help="branch angle (radian)")
    ap.add_argument("--dL", type=float, default=1.0, help="unit edge length")
    ap.add_argument("--seed", type=int, default=random.randint(0,10000))
    ap.add_argument("--sample", type=int, default=20_000, help="sampling steps")
    args = ap.parse_args()
    print(f"seed: {args.seed}")
    result = run_once(S=args.S, k_b=args.kb, k_g=args.kg, k_r=args.kr,alpha=args.alpha, dL=args.dL, seed=args.seed, sample_steps=args.sample)

    print("----- Simulation result -----")
    for k, v in result.items():
        print(f"{k:>8}: {v}")

if __name__ == "__main__":
    main()
