# -*- coding:utf-8 -*-
import cv2
import json
import re
import numpy as np
import typer
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional
import time
from pathlib import Path


class Danmaku:
    """单条弹幕类"""

    def __init__(
        self,
        text: str,
        time_stamp: float,
        font_size: int = 25,
        color: Tuple[int, int, int] = (255, 255, 255),
        alpha: int = 255,
    ):
        self.text = text
        self.time_stamp = time_stamp  # 弹幕出现的时间戳
        self.font_size = font_size
        self.color = color
        self.alpha = alpha
        self.x = None  # 横坐标
        self.y = None  # 纵坐标
        self.width = None  # 文字宽度
        self.speed = None  # 移动速度


class DanmakuManager:
    """弹幕管理器"""

    def __init__(
        self, video_width: int, video_height: int, font_path: str = "msyh.ttc"
    ):
        self.video_width = video_width
        self.video_height = video_height
        self.font_path = font_path
        self.danmakus: List[Danmaku] = []
        self.active_danmakus: List[Danmaku] = []  # 当前帧活跃的弹幕
        self.track_heights = []  # 弹幕轨道高度列表
        self._init_tracks()

    def _init_tracks(self):
        """初始化弹幕轨道"""
        track_height = 30  # 每个轨道的高度
        num_tracks = self.video_height // track_height
        self.track_heights = [i * track_height for i in range(num_tracks)]

    def add_danmaku(
        self,
        text: str,
        time_stamp: float,
        color: Tuple[int, int, int] = (255, 255, 255),
        alpha: int = 255,
    ):
        """添加一条弹幕"""
        danmaku = Danmaku(text, time_stamp, color=color, alpha=alpha)
        self.danmakus.append(danmaku)

    def render_frame(self, frame: np.ndarray, current_time: float) -> np.ndarray:
        """渲染当前帧的弹幕"""
        # 转换为PIL图像以便绘制文字
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype(self.font_path, size=25)

        # 创建透明图层
        overlay = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 更新活跃弹幕
        self._update_active_danmakus(current_time)

        # 绘制所有活跃弹幕
        for danmaku in self.active_danmakus:
            if danmaku.x is None:
                # 初始化弹幕位置
                danmaku.x = self.video_width
                danmaku.y = self._get_available_track()
                text_width = draw.textlength(danmaku.text, font=font)
                danmaku.width = text_width
                danmaku.speed = (
                    self.video_width + text_width
                ) / 8  # 降低速度，8秒穿过屏幕

            # 更新位置
            danmaku.x -= danmaku.speed / 30  # 假设30fps

            # 使用RGBA颜色
            color_with_alpha = (*danmaku.color, danmaku.alpha)
            draw.text(
                (danmaku.x, danmaku.y), danmaku.text, font=font, fill=color_with_alpha
            )

        # 合并图层
        pil_image = Image.alpha_composite(pil_image.convert("RGBA"), overlay)

        # 转换回OpenCV格式
        return cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)

    def _update_active_danmakus(self, current_time: float):
        """更新活跃弹幕列表"""
        # 移除已经移出屏幕的弹幕
        self.active_danmakus = [d for d in self.active_danmakus if d.x > -d.width]

        # 添加新的弹幕
        new_danmakus = [
            d
            for d in self.danmakus
            if d.time_stamp <= current_time and d not in self.active_danmakus
        ]
        self.active_danmakus.extend(new_danmakus)

    def _get_available_track(self) -> int:
        """获取可用的弹幕轨道"""
        if not self.track_heights:
            return 0
        # 简单起见，这里随机选择一个轨道
        return self.track_heights[int(time.time() * 1000) % len(self.track_heights)]


class VideoProcessor:
    """视频处理器类"""

    def __init__(self, input_video: str, output_video: str, danmaku_file: str):
        self.input_video = input_video
        self.output_video = output_video
        self.danmaku_file = danmaku_file
        self.danmaku_list = self.parse_danmaku_file(danmaku_file)
        self.cap = None
        self.out = None
        self.manager = None
        self.width = None
        self.height = None
        self.fps = None
        self.total_frames = None

    def parse_danmaku_file(
        self, file_path: str
    ) -> List[Tuple[str, float, Tuple[int, int, int], int]]:
        """解析弹幕文件，支持ASS、SSA和JSON格式"""
        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    (
                        item["text"],
                        float(item["time_stamp"]),
                        tuple(item["color"]),
                        item["alpha"],
                    )
                    for item in data
                ]
        elif file_path.endswith(".ass") or file_path.endswith(".ssa"):
            danmakus = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Dialogue:"):
                        parts = line.split(",")
                        start_time = self.parse_ass_time(parts[1])
                        text = parts[-1].strip()
                        color = (255, 255, 255)  # 默认白色
                        alpha = 255  # 默认不透明
                        danmakus.append((text, start_time, color, alpha))
            return danmakus
        else:
            raise ValueError("Unsupported file format")

    def parse_ass_time(self, time_str: str) -> float:
        """解析ASS/SSA时间格式"""
        h, m, s, cs = map(float, re.split("[:.]", time_str))
        return h * 3600 + m * 60 + s + cs / 100

    def _initialize(self):
        """初始化视频处理器"""
        self.cap = cv2.VideoCapture(self.input_video)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = cv2.VideoWriter(
            self.output_video, fourcc, self.fps, (self.width, self.height)
        )

        # 初始化弹幕管理器
        self.manager = DanmakuManager(self.width, self.height)
        for item in self.danmaku_list:
            if len(item) == 2:  # 只有文本和时间戳
                self.manager.add_danmaku(*item)
            elif len(item) == 3:  # 包含颜色
                self.manager.add_danmaku(*item)
            elif len(item) == 4:  # 包含颜色和透明度
                self.manager.add_danmaku(*item)

    def process(self):
        """处理视频"""
        try:
            self._initialize()

            with typer.progressbar(
                range(self.total_frames), label="Processing video"
            ) as progress:
                for _ in progress:
                    ret, frame = self.cap.read()
                    if not ret:
                        break

                    current_time = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.fps
                    frame_with_danmaku = self.manager.render_frame(frame, current_time)
                    self.out.write(frame_with_danmaku)

            typer.echo("✨ Processing completed successfully!")

        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()
