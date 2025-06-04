import numpy as np
import scipy.stats as stats

def compute_95_ci(data):
    """
    与えられたデータの95%信頼区間を計算する関数
    :param data: 数値のリストまたはNumPy配列
    :return: 平均値, 95%信頼区間の下限, 95%信頼区間の上限
    """
    data = np.array(data)
    n = len(data)
    mean_x = np.mean(data)
    s = np.std(data, ddof=1)  # 不偏標準偏差
    SE = s / np.sqrt(n)  # 標準誤差
    t_value = stats.t.ppf(0.975, df=n-1)  # 95%信頼区間の t 値
    CI_lower = mean_x - t_value * SE
    CI_upper = mean_x + t_value * SE
    
    return mean_x, CI_lower, CI_upper

if __name__ == "__main__":
  # 入力例
  data = list(map(float, input("データをスペース区切りで入力してください: ").split()))
  mean, CI_lower, CI_upper = compute_95_ci(data)

  # 結果を表示
  print(f"平均値: {mean:.3f}")
  print(f"95%信頼区間: ({CI_lower:.3f}, {CI_upper:.3f})")