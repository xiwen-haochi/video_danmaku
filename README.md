# Video Danmaku

一个简单的视频弹幕处理工具，支持将弹幕文件叠加到视频上。

## 功能特点

- 支持多种弹幕文件格式（JSON、ASS、SSA）
- 支持弹幕颜色和透明度设置
- 平滑的弹幕滚动效果
- 命令行界面，使用简单

## 安装

### 环境要求

- Python 3.10 或更高版本

### 安装步骤

使用 pip 安装：

```bash
pip install video_danmaku
```

## 使用方法

### 命令行使用

```bash
video-danmaku 输入视频路径 输出视频路径 弹幕文件路径
```

### 参数说明

- `输入视频路径`: 要处理的视频文件路径
- `输出视频路径`: 处理后的视频保存路径
- `弹幕文件路径`: 弹幕文件路径（支持 .json、.ass、.ssa 格式）

### 示例

```bash
# 使用 JSON 格式弹幕
video-danmaku input.mp4 output.mp4 danmaku.json

# 使用 ASS 格式弹幕
video-danmaku input.mp4 output.mp4 danmaku.ass
```

## 弹幕文件格式

### JSON 格式

```json
[
    {
        "text": "弹幕文本",
        "time_stamp": 1.0,
        "color": [255, 255, 255],
        "alpha": 255
    }
]
```

- `text`: 弹幕文本
- `time_stamp`: 出现时间（秒）
- `color`: RGB颜色值
- `alpha`: 透明度（0-255）

### ASS/SSA 格式

```plaintext
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:05.00,Default,,0,0,0,,弹幕文本
```


## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- OpenCV - 视频处理
- Pillow - 图像处理
- Typer - 命令行界面
```



