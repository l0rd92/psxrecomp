#!/usr/bin/env python3
"""Guard the presentation-only blank on a 15-bit to 24-bit mode edge."""

from pathlib import Path
import re


SOURCE = Path(__file__).resolve().parents[1] / "src" / "main.cpp"


def function_body(source: str, name: str) -> str:
    match = re.search(rf"\bstatic\s+void\s+{name}\s*\([^;]*?\)\s*\{{", source, re.S)
    if not match:
        raise AssertionError(f"missing function {name}")
    start, depth = match.end(), 1
    for position in range(start, len(source)):
        depth += source[position] == "{"
        depth -= source[position] == "}"
        if depth == 0:
            return source[start:position]
    raise AssertionError(f"unterminated function {name}")


source = SOURCE.read_text(encoding="utf-8")
body = function_body(source, "depth24_cutover_tick")
margin = function_body(source, "depth24_fix_trailing_margin")

edge = body.index("entering_depth24")
mode_blank = body.index("s_d24_cutover_blank = 2;", edge)
mdec_edge = body.index("s_d24_saw_gap && mdec_on", mode_blank)

if not edge < mode_blank < mdec_edge:
    raise AssertionError("mode-entry blank must arm before the later MDEC edge")
if "s_d24_prev_depth = 0;" not in body:
    raise AssertionError("leaving depth24 must re-arm mode-edge detection")
if "s_d24_prev_depth = 1;" not in body:
    raise AssertionError("depth24 mode must latch after its entry edge")
if "s_d24_waiting_for_upload = 1;" not in body[edge:]:
    raise AssertionError("depth24 entry must wait for valid RGB888 upload coverage")
if "s_d24_waiting_for_upload = 0;" not in body[mdec_edge:]:
    raise AssertionError("MDEC activity must release the pre-movie waiting state")

limit = margin.index("gpu_depth24_rgb_limit")
waiting = margin.index("s_d24_waiting_for_upload", limit)
full_blank = margin.index("buf[i] = 0xFF000000u;", waiting)
release = margin.index("s_d24_waiting_for_upload = 0;", full_blank)
settle = margin.index("s_d24_cutover_blank = 2;", release)

if not limit < waiting < full_blank < release < settle:
    raise AssertionError("RGB888 scanout must stay black until upload coverage exists")

print("PASS: depth24 mode entry blanks transitional RGB888 scanout.")
