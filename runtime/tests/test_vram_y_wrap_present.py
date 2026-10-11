#!/usr/bin/env python3
"""Guard GPU-direct present from clamped vertical VRAM wrap rectangles."""

from pathlib import Path


source = (Path(__file__).resolve().parents[1] / "src" / "main.cpp").read_text(
    encoding="utf-8"
)

assert "const bool vram_y_wrap = psx_display_vram_y_wrap(di.display_y, h) != 0;" in source
assert "g_gl_fbo_present && !di.depth24 && !vram_y_wrap" in source
assert "else if (vram_y_wrap)" in source
assert "vk_renderer_sync_cpu();" in source
assert "vk_renderer_present_cpu(sdl_pixel_buf" in source

print("PASS: wrapped vertical VRAM scanout bypasses clamped GPU-direct rectangles.")
