# TravelingNetworkSim
## 概要
- Traveling Network のシミュレーションプログラムです。<br>
- sim1.py: fig.2-b,c,dに相当。k_b, k_gによるそれぞれの葉の数の感度分析

## fixme!
コマンドラインから実行できるようにする。
## 実装のメモ
まずは、初期状態の木を作成する。<br>
当初は、適当なサイズの木を人手で作り(ex. ノード数10,...)、それを成長させるというのを想定していたが、定常状態まで時間を経過させてから、それを初期状態とするほうがいいと判断したので、そっちに変更。<br>
rootが retract 状態になった場合は、 "collapse" と出力し、結果には含めないように変更。<br>

## 参考文献一覧
[1] NJ Cira, ML Paull, S Sinha, F Zanini, EY Ma, IH Riedel-Kruse. "Structure, motion, and multiscale search of traveling networks"<br>

## 更新履歴
2025-06-04 fig2-b,c,d実装完了<br>

This material benefited from the assistance of ChatGPT.

Kazuma Aoyama(kazuma-a@lsnl.jp)
