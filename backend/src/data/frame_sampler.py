from __future__ import annotations


def sample_every_n_frames(frame_index: int, sample_rate: int) -> bool:
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    return frame_index % sample_rate == 0
