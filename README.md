# TravelingNetworkSim
- Traveling Network のシミュレーションプログラムです。<br>
- sim1.py: fig.2-b,c,d,(e)に相当。k_b, k_gによるそれぞれの葉の数の感度分析と○○

## !fixme
ソサイエティの論文の範囲では、座標の概念は不要に見えるが、要相談<br>
コマンドラインから実行できるようにする。
## 実装のメモ
まずは、初期状態の木を作成する。<br>
当初は、適当なサイズの木を人手で作り(ex. ノード数10,...)、それを成長させるというのを想定していたが、定常状態まで時間を経過させてから、それを初期状態とするほうがいいと判断したので、そっちに変更。<br>
rootが retract 状態になった場合は、 "collapse" と出力し、結果には含めないように変更。<br>

2k_b + k_g < 1を満たさないと発散してしまう

## Reference
[1] NJ Cira, ML Paull, S Sinha, F Zanini, EY Ma, IH Riedel-Kruse. "Structure, motion, and multiscale search of traveling networks"<br>
[2] H. Ohsaki, graphtools, https://github.com/h-ohsaki/graph-tools<br>

## 更新履歴
2025-06-04 fig2-b,c,d実装完了<br>
2025-06-04 k_b = k_s を考慮していなかった為、プログラムを修正<br>
2025-06-05 fig2-e実装完了<br>

This material benefited from the assistance of ChatGPT.

Kazuma Aoyama(kazuma-a@lsnl.jp)
