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
        random.seed(seed)

        # ノード・エッジのストレージ
        self.nodes: Dict[int, Node] = {}
        self.edges: Dict[int, Edge] = {}
        self.next_node_id = 0
        self.next_edge_id = 0
        # ルート生成
        root = self._new_node()
        leaf = self._new_node(parent=root, length=dL, angle=0.0)
        self.time = 0.0

    # ───────────────── private helpers ─────────────────
    def _new_node(self, parent: int | None = None, length: float = 0.0,
                  angle: float = 0.0) -> int:
        nid = self.next_node_id; self.next_node_id += 1
        self.nodes[nid] = Node(id=nid, parent=parent)
        if parent is not None:
            eid = self.next_edge_id; self.next_edge_id += 1
            self.edges[eid] = Edge(parent=parent, child=nid,
                                   length=length, angle=angle)
            self.nodes[parent].children.append(nid)
            self.nodes[nid].edge_from_parent = eid
        return nid

    # ───────────────── public API ─────────────────
    def step(self):
        """Gillespie 1 ステップ実行"""
        free_leaves = [n for n in self.nodes.values() if n.is_leaf and n.state == "free"]
        retract_leaves = [n for n in self.nodes.values() if n.is_leaf and n.state == "retract"]
        # 総レート
        lam = (self.k_b + self.k_g + self.k_s) * len(free_leaves) + self.k_r * len(retract_leaves)
        if lam == 0:
            return  # 動きがない
        # 時間更新
        dt = random.expovariate(lam)
        self.time += dt
        # ルーレット選択
        r = random.random() * lam
        cumulative = 0.0
        # 自由葉イベント
        for ev, rate in (("branch", self.k_b), ("grow", self.k_g), ("switch", self.k_s)):
            span = rate * len(free_leaves)
            if r < cumulative + span:
                self._do_free_event(random.choice(free_leaves), ev)
                return
            cumulative += span
        # 収縮葉
        idx = int((r - cumulative) / self.k_r)
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
        if eid is None:
            return
        self.edges[eid].length += self.dL

    def _branch(self, node: Node):
        angle_base = self.edges[node.edge_from_parent].angle if node.edge_from_parent is not None else 0.0
        for sign in (-0.5, 0.5):
            self._new_node(parent=node.id, length=self.dL, angle=angle_base + sign * self.alpha)
        node.is_leaf = False  # 分岐後は内部ノード

    def _do_retract_event(self, node: Node):
        eid = node.edge_from_parent
        if eid is None:
            return
        self.edges[eid].length -= self.dL
        if self.edges[eid].length <= 0:
            # エッジ・ノード削除
            parent = self.edges[eid].parent
            self.nodes[parent].children.remove(node.id)
            del self.edges[eid]
            del self.nodes[node.id]
            # 親ノードの次数更新
            if len(self.nodes[parent].children) == 0:
                self.nodes[parent].is_leaf = True
                self.nodes[parent].state = "free"

    # ───────────────── stats ─────────────────
    def snapshot(self):
        ne = len(self.edges)
        nf = sum(1 for n in self.nodes.values() if n.is_leaf and n.state == "free")
        nr = sum(1 for n in self.nodes.values() if n.is_leaf and n.state == "retract")
        l_bar = (sum(e.length for e in self.edges.values()) / ne) if ne else 0.0
        return dict(time=self.time, L_bar=l_bar, NE=ne, NF=nf, NR=nr)