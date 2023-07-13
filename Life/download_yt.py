import click
from pytube import YouTube


VIDEO_SAVE_DIRECTORY = "./videos"
AUDIO_SAVE_DIRECTORY = "./audio"


def download(video_url):
    video = YouTube(video_url)
    try:
        video = video.streams.get_highest_resolution()
    except:
        pass

    try:
        video.download(VIDEO_SAVE_DIRECTORY)
    except:
        print("Failed to download video")

    print("video was downloaded successfully")


def download_audio(video_url):
    video = YouTube(video_url)
    audio = video.streams.filter(only_audio=True).first()

    try:
        audio.download(AUDIO_SAVE_DIRECTORY)
    except:
        print("Failed to download audio")

    print("audio was downloaded successfully")


@click.command()
@click.option("--video_url", required=True, help="Video URL")
@click.option(
    "--audio_only",
    is_flag=True,
    default=False,
    help="If download audio only",
)
def main(video_url, audio_only: bool):
    if audio_only:
        download_audio(video_url=video_url)
    else:
        download(video_url=video_url)


if __name__ == "__main__":
    main()
