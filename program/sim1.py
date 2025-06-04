import argparse, random
from traveling_network import *
from conf_interval import *

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
def run_once(S: float, k_b: float, k_g: float, k_r: float, alpha: float, dL: float, seed, burn_step, sample_steps):
    net = TravelingNetwork(S=S, k_b=k_b, k_g=k_g, k_r=k_r, alpha=alpha, dL=dL, seed=seed)
    # 定常状態になるまで、放置
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
    ap.add_argument("--S", type=float, default=800.0)
    ap.add_argument("--kb", type=float, default=0.1)
    ap.add_argument("--kg", type=float, default=0.01)
    ap.add_argument("--kr", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, default=1.0472,  # = π/3
                    help="branch angle (radian)")
    ap.add_argument("--dL", type=float, default=1.0, help="unit edge length")
    args = ap.parse_args()
    nf = []
    nr = []
    l_bar = []
    n1 = solve_N1_scaled(args.S, args.kb, args.kg)#N_1 theoryの近似値を計算
    t_r = (n1 / (2 * args.kb))#論文のτ_rに相当
    burn_step = max(int(10 * t_r),  2000)#定常状態になるまでに必要なステップ数
    sample_steps = max(int(40 * t_r), 50000) #大規模 S や小さな k_b で τ_r が伸びた場合は sampling_steps を「少なくとも 20 τ_r 以上」に再設定するのが目安
    print(f"S:{args.S}, k_b:{args.kb}, k_g:{args.kg}, burn_step:{burn_step}, sample_steps:{sample_steps}")
    for i in range(50):
        seed = random.randint(0,10000)
        print(f"seed: {seed}")
        result = run_once(S=args.S, k_b=args.kb, k_g=args.kg, k_r=args.kr,alpha=args.alpha, dL=args.dL, seed=seed, burn_step=burn_step, sample_steps=sample_steps)
        if result["NR"] == 1 and result["NF"] == 0.0: 
            print("collapse")
        else:
            nf.append(result["NF"])
            nr.append(result["NR"])
            l_bar.append(result["L_bar"])
    print(nf)
    print(nr)
    print("----- Simulation result -----")
    print(f"S: {args.S}, k_b: {args.kb}, k_g: {args.kg}")
    nfmean, nfCI_lower, nfCI_upper = compute_95_ci(nf)
    print(f"NF: 平均値: {nfmean:.3f} 95%信頼区間: {(nfmean - nfCI_lower):.3f}")
    nrmean, nrCI_lower, nrCI_upper = compute_95_ci(nr)
    print(f"NR: 平均値: {nrmean:.3f} 95%信頼区間: {(nrmean - nrCI_lower):.3f}")
    l_barmean, l_barCI_lower, l_barCI_upper = compute_95_ci(l_bar)
    print(f"l_bar: 平均値: {l_barmean:.3f} 95%信頼区間: {(l_barmean - l_barCI_lower):.3f}")
    print(f"N1: {nfmean + nrmean}, S/L_bar: {args.S/l_barmean}")

if __name__ == "__main__":
    main()
