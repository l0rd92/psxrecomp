#!/usr/bin/env python3
"""Guard GPU-direct present from clamped vertical VRAM wrap rectangles."""

from pathlib import Path


source = (Path(__file__).resolve().parents[1] / "src" / "main.cpp").read_text(
    encoding="utf-8"
)

assert "const bool vram_y_wrap = psx_display_vram_y_wrap(di.display_y, h) != 0;" in source
assert "g_gl_fbo_present && !di.depth24 &&" in source
assert "else if (vram_y_wrap)" in source
assert "vk_renderer_sync_cpu();" in source
assert "vk_renderer_present_cpu(sdl_pixel_buf" in source

gl_source = (Path(__file__).resolve().parents[1] / "src" / "gpu_gl_renderer.c").read_text(
    encoding="utf-8"
)
assert "const int wraps_y = y_slices.second_height != 0u;" in gl_source
assert "glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);" in gl_source
assert "!wraps_y && interp_capture(" in gl_source

print("PASS: OpenGL wraps vertical scanout on-GPU; Vulkan stages it safely.")
