import os
import yt_dlp

from config import DOWNLOAD_DIR, MAX_FILE_SIZE

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIE_FILE = "cookies.txt"


def create_cookie_file():

    cookies = os.getenv("YT_COOKIES")

    if not cookies:
        return None

    if os.path.exists(COOKIE_FILE):
        return COOKIE_FILE

    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookies)

    return COOKIE_FILE


class Downloader:

    @staticmethod
    def video_info(url):

        cookie = create_cookie_file()

        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web"
                    ]
                }
            }
        }

        if cookie:
            opts["cookiefile"] = cookie

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(
                url,
                download=False
            )

    @staticmethod
    def qualities(info):

        q = {}

        for f in info.get("formats", []):

            if f.get("vcodec") == "none":
                continue

            h = f.get("height")

            if not h:
                continue

            if h > 1080:
                continue

            q[h] = True

        return sorted(q.keys())

    @staticmethod
    def download_video(url, quality):

        cookie = create_cookie_file()

        output = os.path.join(
            DOWNLOAD_DIR,
            "%(title)s.%(ext)s"
        )

        fmt = (
            f"bestvideo[height<={quality}]"
            "+bestaudio/"
            f"best[height<={quality}]"
        )

        opts = {

            "format": fmt,

            "merge_output_format": "mp4",

            "outtmpl": output,

            "quiet": True,

            "noplaylist": True,

            "retries": 5,

            "fragment_retries": 5,

            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web"
                    ]
                }
            }

        }

        if cookie:
            opts["cookiefile"] = cookie

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            filename = os.path.splitext(filename)[0] + ".mp4"

            if not os.path.exists(filename):

                for f in os.listdir(DOWNLOAD_DIR):

                    if f.endswith(".mp4"):

                        filename = os.path.join(
                            DOWNLOAD_DIR,
                            f
                        )

                        break

            if not os.path.exists(filename):
                raise Exception("Video file not found")

            size = os.path.getsize(filename)

            if size > MAX_FILE_SIZE:
                os.remove(filename)
                raise Exception(
                    "فایل از 50 مگابایت بزرگ‌تر است."
                )

            return filename, info

    @staticmethod
    def download_audio(url):

        cookie = create_cookie_file()

        output = os.path.join(
            DOWNLOAD_DIR,
            "%(title)s.%(ext)s"
        )

        opts = {

            "format": "bestaudio/best",

            "outtmpl": output,

            "quiet": True,

            "noplaylist": True,

            "retries": 5,

            "fragment_retries": 5,

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],

            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web"
                    ]
                }
            }

        }

        if cookie:
            opts["cookiefile"] = cookie

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        mp3 = None

        for f in os.listdir(DOWNLOAD_DIR):

            if f.endswith(".mp3"):

                mp3 = os.path.join(
                    DOWNLOAD_DIR,
                    f
                )

                break

        if mp3 is None:
            raise Exception("MP3 file not found")

        size = os.path.getsize(mp3)

        if size > MAX_FILE_SIZE:

            os.remove(mp3)

            raise Exception(
                "فایل از 50 مگابایت بزرگ‌تر است."
            )

        return mp3, info

    @staticmethod
    def cleanup(path):

        try:

            if path and os.path.exists(path):
                os.remove(path)

        except Exception:
            pass
