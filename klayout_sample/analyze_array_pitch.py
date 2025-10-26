# analyze_array_pitch.py
# Analyze layout Stack array pitch from CSV
import sys
import json
import os
import csv
from math import inf
from collections import defaultdict

LAYER_MAP = {
    "100.0": "VIA1",
    "200.0": "M1",
    "300.0": "M2",
}

DEFAULT_TOL = 1e-6


def parse_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                rows.append({
                    "cell_name": row.get("cell_name", "").strip(),
                    "layer": row.get("layer", "").strip(),
                    "x1": float(row.get("bbox_x1", 0)),
                    "y1": float(row.get("bbox_y1", 0)),
                    "x2": float(row.get("bbox_x2", 0)),
                    "y2": float(row.get("bbox_y2", 0)),
                })
            except Exception:
                continue
    return rows


def bbox_equal(a, b, tol=DEFAULT_TOL):
    return (
        abs(a["x1"] - b["x1"]) <= tol and
        abs(a["y1"] - b["y1"]) <= tol and
        abs(a["x2"] - b["x2"]) <= tol and
        abs(a["y2"] - b["y2"]) <= tol
    )


def bbox_center(bbox):
    return ((bbox["x1"] + bbox["x2"]) / 2.0, (bbox["y1"] + bbox["y2"]) / 2.0)


def overlaps(a, b):
    return not (a["x2"] <= b["x1"] or a["x1"] >= b["x2"] or a["y2"] <= b["y1"] or a["y1"] >= b["y2"])


def find_stacks(rows, target_cell=None):
    grouped = defaultdict(list)
    for row in rows:
        if target_cell and row["cell_name"] != target_cell:
            continue
        grouped[row["layer"]].append(row)

    via_list = grouped.get("100.0", [])
    m1_list = grouped.get("200.0", [])
    m2_list = grouped.get("300.0", [])

    stacks = []
    for via in via_list:
        via_bbox = {k: via[k] for k in ("x1", "y1", "x2", "y2")}
        overlaps_m1 = [m for m in m1_list if overlaps(via, m)]
        overlaps_m2 = [m for m in m2_list if overlaps(via, m)]

        def best_match(candidates):
            best = None
            best_area = -inf
            for c in candidates:
                overlap_x1 = max(via["x1"], c["x1"])
                overlap_y1 = max(via["y1"], c["y1"])
                overlap_x2 = min(via["x2"], c["x2"])
                overlap_y2 = min(via["y2"], c["y2"])
                if overlap_x2 <= overlap_x1 or overlap_y2 <= overlap_y1:
                    continue
                area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
                if area > best_area:
                    best_area = area
                    best = c
            return best

        m1 = best_match(overlaps_m1)
        m2 = best_match(overlaps_m2)
        if m1 and m2:
            stacks.append({
                "via": via,
                "m1": m1,
                "m2": m2,
                "center": bbox_center(via_bbox),
            })
    return stacks


def compute_pitch(stacks):
    if len(stacks) < 2:
        return None, None
    centers = [s["center"] for s in stacks]
    centers.sort()
    xs = sorted(set(c[0] for c in centers))
    ys = sorted(set(c[1] for c in centers))

    def min_spacing(values):
        if len(values) < 2:
            return None
        min_gap = inf
        for i in range(1, len(values)):
            gap = values[i] - values[i - 1]
            if gap > 0 and gap < min_gap:
                min_gap = gap
        return None if min_gap == inf else min_gap

    pitch_x = min_spacing(xs)
    pitch_y = min_spacing(ys)
    return pitch_x, pitch_y


def main(payload):
    csv_path = payload.get("input_csv", "layout_from_csv_with_top_shapes.csv")
    cell_name = payload.get("cell_name", "top")
    if not os.path.exists(csv_path):
        return {"ok": False, "error": f"Input CSV not found: {csv_path}"}

    rows = parse_rows(csv_path)
    stacks = find_stacks(rows, target_cell=cell_name)
    pitch_x, pitch_y = compute_pitch(stacks)

    result = {
        "ok": True,
        "result": {
            "input_csv": csv_path,
            "cell_name": cell_name,
            "stack_count": len(stacks),
            "array_pitch_x": pitch_x,
            "array_pitch_y": pitch_y,
        }
    }
    if pitch_x is None or pitch_y is None:
        result["result"]["warning"] = "Insufficient matching stacks to determine pitch"
    return result


if __name__ == "__main__":
    raw = sys.stdin.read().strip()
    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_csv": vals[0] if len(vals) > 0 and vals[0] else "layout_from_csv_with_top_shapes.csv",
            "cell_name": vals[1] if len(vals) > 1 and vals[1] else "top",
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
