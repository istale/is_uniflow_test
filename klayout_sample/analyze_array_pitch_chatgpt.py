#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Axis-aligned array pitch from CSV using VIA1∩M1∩M2 lookup patterns.
Fixes the sub-period issue by:
  1) Estimating pitch_x from X alone (no multiplier trick).
  2) Assigning each VIA1 to a column index by rounding (x - x_ref)/pitch_x.
  3) Computing pitch_y ONLY within the same column (removes cross-array offsets).

CSV columns:
  cell_name,layer,bbox_x1,bbox_y1,bbox_x2,bbox_y2,is_rectangle,polygon_vertices

Layers:
  VIA1=100.0, M1=200.0, M2=300.0  (可用參數覆寫)

Usage:
  python axis_aligned_pitch_lookup_columnwise.py --csv data.csv --via 100 --m1 200 --m2 300
"""
from __future__ import annotations
import argparse, csv, math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import statistics as stats

# ---------------- Geometry ----------------
@dataclass(frozen=True)
class Rect:
    x1: float; y1: float; x2: float; y2: float
    def center(self) -> Tuple[float,float]:
        return ((self.x1+self.x2)*0.5, (self.y1+self.y2)*0.5)

def load_layers(path: Path) -> Dict[float, List[Rect]]:
    L: Dict[float, List[Rect]] = defaultdict(list)
    with path.open(newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            x1=float(r["bbox_x1"]); y1=float(r["bbox_y1"])
            x2=float(r["bbox_x2"]); y2=float(r["bbox_y2"])
            if x2 < x1: x1, x2 = x2, x1
            if y2 < y1: y1, y2 = y2, y1
            L[float(r["layer"])].append(Rect(x1,y1,x2,y2))
    return L

def overlap(a: Rect, b: Rect, eps: float=0.0) -> bool:
    return not (a.x2 < b.x1-eps or b.x2 < a.x1-eps or
                a.y2 < b.y1-eps or b.y2 < a.y1-eps)

# ---------------- Pitch helpers ----------------
def pitch_1d_axis_aligned(values: List[float], max_gap: int=3) -> float:
    """
    Robust 1D pitch estimation WITHOUT multiplier folding (避免子週期)。
    步驟：
      1) unique+sort
      2) 收集相鄰與小跨度差值（僅正向）
      3) 取差值的眾數附近（以 median 作代表，對離群具韌性）
    """
    u = sorted(set(values))
    if len(u) < 3:
        raise RuntimeError("unique 座標太少，無法估計節距")
    diffs: List[float] = []
    n = len(u)
    for i in range(n):
        for j in range(i+1, min(i+1+max_gap, n)):
            diffs.append(u[j]-u[i])
    # 用簡單的自動分箱選峰：bin 寬 = 範圍的 1%（下限保護）
    rng = max(u) - min(u)
    bin_w = max(rng * 0.01, 1e-12)
    bins: Dict[int, List[float]] = defaultdict(list)
    for d in diffs:
        k = round(d/bin_w)
        bins[k].append(d)
    # 取樣本數最多的 bin，並以其中位數作為 pitch 估計
    best_k = max(bins, key=lambda k: len(bins[k]))
    return float(stats.median(bins[best_k]))

def assign_columns(xs: List[float], pitch_x: float, trial_refs: Optional[List[float]]=None, tol_frac: float=0.15) -> Tuple[Dict[int,List[int]], float]:
    """
    依 pitch_x 將點分欄位。為了找最佳 x_ref（相位），用幾個候選 x_ref 嘗試並選擇
    “可整齊分欄且欄內點數變異最小”的那個。
    傳回：{col_index: [point_idx,...]}, best_x_ref
    """
    if trial_refs is None:
        trial_refs = sorted(set(xs))[:6]  # 前幾個 x 當作候選相位
    best_score = None; best_map=None; best_ref=None
    tol = max(pitch_x * tol_frac, 1e-12)
    for x_ref in trial_refs:
        cmap: Dict[int,List[int]] = defaultdict(list)
        for i,x in enumerate(xs):
            n = round((x - x_ref)/pitch_x)
            x_hat = x_ref + n*pitch_x
            if abs(x - x_hat) <= tol:
                cmap[n].append(i)
            else:
                # 若偏離過大，暫不歸欄（可視需求也歸到最接近欄）
                pass
        # 評分：欄位數*平均欄內點數（希望集中且均衡）
        sizes = [len(v) for v in cmap.values() if len(v)>0]
        score = (len(sizes), -stats.pstdev(sizes) if len(sizes)>1 else 0.0)
        if (best_score is None) or (score > best_score):
            best_score, best_map, best_ref = score, cmap, x_ref
    return best_map, best_ref

def pitch_y_by_columns(points: List[Tuple[float,float]], pitch_x: float) -> float:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cols, x_ref = assign_columns(xs, pitch_x)
    dy_all: List[float] = []
    for _, idxs in cols.items():
        if len(idxs) < 2: 
            continue
        col_y = sorted({ys[i] for i in idxs})
        for i in range(len(col_y)-1):
            dy_all.append(col_y[i+1] - col_y[i])
    if not dy_all:
        raise RuntimeError("欄內沒有足夠的 y 差值可估計 pitch_y；請檢查資料或公差。")
    # 以眾數附近 bin 的中位數代表
    rng = max(dy_all) - min(dy_all)
    bin_w = max(rng * 0.05, 1e-12)
    bins: Dict[int, List[float]] = defaultdict(list)
    for d in dy_all:
        k = round(d/bin_w)
        bins[k].append(d)
    best_k = max(bins, key=lambda k: len(bins[k]))
    return float(stats.median(bins[best_k]))

# ---------------- Main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--via", type=float, default=100.0)
    ap.add_argument("--m1", type=float, default=200.0)
    ap.add_argument("--m2", type=float, default=300.0)
    ap.add_argument("--eps", type=float, default=0.0, help="overlap 容差")
    args = ap.parse_args()

    L = load_layers(args.csv)
    via = L.get(args.via, []); m1 = L.get(args.m1, []); m2 = L.get(args.m2, [])
    if not via or not m1 or not m2:
        raise SystemExit("缺 VIA/M1/M2 其中之一的資料")

    # 篩出有效 VIA（同時重疊 M1 與 M2）
    def ov(a,b): return overlap(a,b,eps=args.eps)
    valid: List[Tuple[float,float]] = []
    for v in via:
        hit_m1 = any(ov(v,m) for m in m1)
        hit_m2 = any(ov(v,m) for m in m2)
        if hit_m1 and hit_m2:
            valid.append(v.center())
    if not valid:
        raise SystemExit("沒有 VIA1 同時重疊到 M1 與 M2")

    xs = [p[0] for p in valid]
    ys = [p[1] for p in valid]

    # ① 先以 X 單軸估 pitch_x（不做倍數除法，避免子週期）
    pitch_x = pitch_1d_axis_aligned(xs, max_gap=3)

    # ② 以欄位分組只在欄內估 pitch_y
    pitch_y = pitch_y_by_columns(valid, pitch_x)

    print("[Axis-Aligned Pitch via Lookup Pattern (Column-wise)]")
    print(f"valid VIA1: {len(valid)}")
    print(f"pitch_x: {pitch_x:.9f}")
    print(f"pitch_y: {pitch_y:.9f}")
    print("Note: pitch_y 僅由同欄位的 y 差值估得，不受跨陣列 y-offset 影響。")

if __name__ == "__main__":
    main()