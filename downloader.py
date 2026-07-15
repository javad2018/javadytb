import os
import yt_dlp

from config import COOKIES

COOKIE_FILE = "cookies.txt"


def create_cookie_file():

    if not COOKIES:
        return None

    with open(COOKIE_FILE, "w", encoding="utf8") as f:
        f.write(COOKIES)

    return COOKIE_FILE

from config import MAX_FILE_SIZE, DOWNLOAD_DIR


os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class Downloader:

    @staticmethod
    def video_info(url: str):

        cookie = create_cookie_file()
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        if cookie:
            opts["cookiefile"] = cookie

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    @staticmethod
    def qualities(info):

        result = {}

        for f in info.get("formats", []):

            if f.get("vcodec") == "none":
                continue

            h = f.get("height")

            if not h:
                continue

            if h > 1080:
                continue

            if h not in result:
                result[h] = True

        return sorted(result.keys())

    @staticmethod
    def download_video(url, quality):

        out = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        fmt = (
            f"bestvideo[height<={quality}]"
            f"+bestaudio/"
            f"best[height<={quality}]"
        )

        opts = {
            "format": fmt,
            "merge_output_format": "mp4",
            "outtmpl": out,
            "quiet": True,
        }

        cookie = create_cookie_file()

if cookie:
    opts["cookiefile"] = cookie

        
        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            filename = os.path.splitext(filename)[0] + ".mp4"

            if not os.path.exists(filename):
                for f in os.listdir(DOWNLOAD_DIR):
                    if f.endswith(".mp4"):
                        filename = os.path.join(DOWNLOAD_DIR, f)
                        break

            size = os.path.getsize(filename)

            if size > MAX_FILE_SIZE:
                os.remove(filename)
                raise Exception("File larger than Telegram limit")

            return filename, info

    @staticmethod
    def download_audio(url):

        out = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        opts = {
            "format": "bestaudio/best",
            "outtmpl": out,
            "quiet": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        cookie = create_cookie_file()

if cookie:
    opts["cookiefile"] = cookie

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(url, download=True)

            mp3 = None

            for f in os.listdir(DOWNLOAD_DIR):

                if f.endswith(".mp3"):
                    mp3 = os.path.join(DOWNLOAD_DIR, f)
                    break

            if mp3 is None:
                raise Exception("Audio not generated")

            size = os.path.getsize(mp3)

            if size > MAX_FILE_SIZE:
                os.remove(mp3)
                raise Exception("File larger than Telegram limit")

            return mp3, info

    @staticmethod
    def cleanup(path):

        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
            if os.path.exists("cookies.txt"):
    os.remove("cookies.txt")
