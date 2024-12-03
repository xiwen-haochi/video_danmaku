import typer
from pathlib import Path
from . import VideoProcessor

app = typer.Typer()


@app.command()
def main(
    input_video: Path = typer.Argument(
        ...,
        help="Input video file path",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_video: Path = typer.Argument(
        ..., help="Output video file path", dir_okay=False, resolve_path=True
    ),
    danmaku_file: Path = typer.Argument(
        ...,
        help="Danmaku file path (supports .ass, .ssa, .json)",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
):
    """
    Process video with danmaku overlay.
    Supports ASS, SSA, and JSON format danmaku files.
    """
    try:
        if not str(danmaku_file).lower().endswith((".ass", ".ssa", ".json")):
            typer.echo("Error: Unsupported danmaku file format", err=True)
            raise typer.Exit(1)

        typer.echo(f"🎬 Processing video: {input_video}")
        typer.echo(f"📝 Using danmaku file: {danmaku_file}")

        processor = VideoProcessor(
            str(input_video), str(output_video), str(danmaku_file)
        )
        processor.process()
        typer.echo(f"✅ Output saved to: {output_video}")

    except Exception as e:
        import traceback

        traceback.print_exc()
        typer.echo(f"❌ Error: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
