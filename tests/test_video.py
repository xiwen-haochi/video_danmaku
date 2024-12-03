import pytest
from video_danmaku.core import VideoProcessor


def test_video_processor():
    processor = VideoProcessor(
        "tests/assets/1.mp4", "tests/assets/output.mp4", "tests/assets/dm.json"
    )
    processor.process()
