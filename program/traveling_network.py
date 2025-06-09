from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Edge:
    parent: int          # 親ノード ID
    child: int           # 子ノード ID
    length: float        # エッジ長
    angle: float         # 方向（rad）

@dataclass
class Node:
    id: int
    children: List[int] = field(default_factory=list)
    parent: int | None = None
    is_leaf: bool = True
    state: str = "free"  # "free" または "retract"
    edge_from_parent: int | None = None  # Edge ID
    x: float = 0.0
    y: float = 0.0

class TravelingNetwork:
    """Traveling Network 木構造シミュレーションクラス
    - 葉イベントを Gillespie 法で逐次実行
    - 総エッジ長 S を保持
    """

    def __init__(self, S: float = 200.0, k_b: float = 0.05, k_g: float = 0.25,
                 k_r: float = 1.0, alpha: float = math.pi/3, dL: float = 1.0,
                 seed: int | None = None):
        self.S_target = S
        self.k_b, self.k_g, self.k_r = k_b, k_g, k_r
        self.k_s = k_b  # サイズ保存条件
        self.alpha = alpha
        self.dL = dL
        self.del_node = []
        self.add_node = []
        random.seed(seed)

        # ノード・エッジのストレージ
        self.nodes: Dict[int, Node] = {}
        self.edges: Dict[int, Edge] = {}
        self.next_node_id = 0
        self.next_edge_id = 0
        # ルート生成
        root = self._new_node()
        leaf = self._new_node(parent=root, length=dL, angle=0.0)
        self.nodes[root].is_leaf = False            # 追加
        self.nodes[root].state   = "internal"       # 追加（状態区別用）
        self.time = 0.0
        self.total_length = sum(e.length for e in self.edges.values())


    # ───────────────── private helpers ─────────────────
    def _new_node(self, parent: int | None = None, length: float = 0.0, angle: float = 0.0):
        nid = self.next_node_id
        self.next_node_id += 1

        if parent is None: x, y = 0.0, 0.0
        else:
            parent_node = self.nodes[parent]
            x = parent_node.x + length * math.cos(angle)
            y = parent_node.y + length * math.sin(angle)

        self.nodes[nid] = Node(id=nid, parent=parent, x=x, y=y)

        if parent is not None:
            eid = self.next_edge_id
            self.next_edge_id += 1
            self.edges[eid] = Edge(parent=parent, child=nid, length=length, angle=angle)
            self.add_node.append([nid, parent])
            self.nodes[parent].children.append(nid)
            self.nodes[nid].edge_from_parent = eid
        return nid

    # ───────────────── public API ─────────────────
    def step(self):
        self.add_node.clear()
        self.del_node.clear()
        self.nodes = {i:n for i,n in self.nodes.items() if isinstance(n,Node)}
        # ── ① 今の総エッジ長を計算 ─────────────────────
        self.total_length = sum(e.length for e in self.edges.values())

        
        # ── ② 目標 S と比べて switch レートを補正 ───────
        if self.total_length > self.S_target + self.dL:
            k_s_eff = self.k_s * 1.2        # 長すぎ → 縮めを強める
        elif self.total_length < self.S_target - self.dL:
            k_s_eff = self.k_s * 0.8        # 短すぎ → 伸ばしを許す
        else:
            k_s_eff = self.k_s              # ほぼ目標 → そのまま
        k_b_eff = self.k_b                  # 分岐率は固定で OK
        free_leaves = [
    n for n in self.nodes.values()
    if isinstance(n, Node)                  # Ellipsis ガード
    and n.is_leaf and n.state == "free"]
        retract_leaves = [
    n for n in self.nodes.values()
    if isinstance(n, Node)
    and n.is_leaf and n.state == "retract"]

        lam = (k_b_eff + self.k_g + k_s_eff)*len(free_leaves) + self.k_r*len(retract_leaves)
        if lam == 0:
            return
        dt = random.expovariate(lam)
        self.time += dt
        r  = random.random()*lam
        cum = 0.0
        for ev, rate in (("branch", k_b_eff), ("grow", self.k_g), ("switch", k_s_eff)):
            span = rate*len(free_leaves)
            if r < cum + span:
                self._do_free_event(random.choice(free_leaves), ev)
                return
            cum += span
        idx = int((r-cum)/self.k_r)
        self._do_retract_event(retract_leaves[idx])
    # ───────────────── event handlers ─────────────────
    def _do_free_event(self, node: Node, ev_type: str):
        if ev_type == "grow":
            self._grow(node)
        elif ev_type == "branch":
            self._branch(node)
        elif ev_type == "switch":
            node.state = "retract"

    def _grow(self, node: Node):
        eid = node.edge_from_parent
        if eid is None: return
        self.edges[eid].length += self.dL
        parent = self.nodes[self.edges[eid].parent]
        node.x = parent.x + self.edges[eid].length * math.cos(self.edges[eid].angle)
        node.y = parent.y + self.edges[eid].length * math.sin(self.edges[eid].angle)
        self.total_length = sum(e.length for e in self.edges.values())


    def _branch(self, node: Node):
        angle_base = self.edges[node.edge_from_parent].angle if node.edge_from_parent is not None else 0.0
        for sign in (-0.5, 0.5):
            self._new_node(parent=node.id, length=self.dL, angle=angle_base + sign * self.alpha)
        node.is_leaf = False  # 分岐後は内部ノード
        self.total_length = sum(e.length for e in self.edges.values())


    def _do_retract_event(self, node: Node):
        # ルートノードなら retract させない
        if node.parent is None:
            node.state = "free"   # ルートは縮まない
            return
        """retract 状態の葉を dL だけ縮め，長さ 0 で葉を削除"""
        eid = node.edge_from_parent
        if eid is None:
            return            # root が retract の時は何もしない

        # 1. エッジを縮める
        self.edges[eid].length -= self.dL

        # 2. 長さが 0 以下なら葉ノードとエッジを削除
        if self.edges[eid].length <= 0:
            self.del_node.append([node.id, self.edges[eid].child])
            parent_id = self.edges[eid].parent

            # データ構造更新
            self.nodes[parent_id].children.remove(node.id)
            del self.edges[eid]
            del self.nodes[node.id]
            
            # 3. 親が子を失って “孤立” した場合の扱い
            if len(self.nodes[parent_id].children) == 0:
                # 親を retract‐leaf に変換して
                # 次のステップでさらに上へ縮むようにする
                self.nodes[parent_id].is_leaf = True
                self.nodes[parent_id].state   = "retract"
                # edge_from_parent は既存のまま  → 上位エッジが縮む 
        self.total_length = sum(e.length for e in self.edges.values())

    # ───────────────── stats ─────────────────
    def snapshot(self):
        ne = len(self.edges)
        nf = sum(1 for n in self.nodes.values() if n.is_leaf and n.state == "free")
        nr = sum(1 for n in self.nodes.values() if n.is_leaf and n.state == "retract")
        l_bar = (sum(e.length for e in self.edges.values()) / ne) if ne else 0.0
        return dict(time=self.time, L_bar=l_bar, NE=ne, NF=nf, NR=nr, add = self.add_node, de =self.del_node)