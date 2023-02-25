import re
from typing import Iterable
from pytube import YouTube
from pytube import Playlist
from pytube import StreamQuery
from pytube import Stream
import os
import subprocess

from Enumeration import SaveData
from save import Save

WELCOME_STR: str = """ __   __  _______    ______   _______  _     _  __    _ 
    |  | |  ||       |  |      | |       || | _ | ||  |  | |
    |  |_|  ||_     _|  |  _    ||   _   || || || ||   |_| |
    |       |  |   |    | | |   ||  | |  ||       ||       |
    |_     _|  |   |    | |_|   ||  |_|  ||       ||  _    |
      |   |    |   |    |       ||       ||   _   || | |   |
      |___|    |___|    |______| |_______||__| |__||__|_|  |__|
        """


class YTDown:
    def __init__(self,save:Save):
        self.save = save
        self.output_path: str = ""

    def _banner(self):
        print(WELCOME_STR)
        for i, choice in enumerate(self.save.OPTIONS_CHOICE_STR):
            print(f"{i + 1}): {choice}")

    def validate_url(self, link: str) -> str:
        pattern = re.compile(
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?|^(https?://)?(www\.)?youtu\.be/[\w-]+$')
        if pattern.match(link):
            return link
        else:
            raise ValueError(self.save.get_message('INVALID_LINK_MSG'))

    def norm_file_name(self, name: str) -> str:
        new: str = ""
        for c in name:
            if c.isalnum() or c in {"_", ".", "-"}:
                new += c
            else:
                new += "_"
        return new

    def after_download_audio(self, video_file: str, audio_file: str, output_file: str):
        os.remove(video_file)
        os.remove(audio_file)
        file_name = os.path.basename(output_file)
        new_name = file_name.replace(self.save.get_data(SaveData.FILE_PREFIX), "")
        new_path = os.path.join(os.path.dirname(output_file), new_name)
        os.rename(output_file, new_path)

    def download_audio_file(self, yt: YouTube, video_file: str, file_extension: str):
        try:
            audio = yt.streams.get_audio_only()
            yt.register_on_progress_callback(self.on_progress)
            print(f"{self.save.get_message('START_DOWNLOAD_MSG')}: {yt.title}-(Audio)")
            audio_file = audio.download(
                output_path=self.output_path, filename=f"{self.norm_file_name(yt.title)}.mp3"
            )
            if self.save.get_data(SaveData.DEBUG):
                print(f" yt{yt} , video-path: {video_file}, audio_path: {audio_file}")
            if audio_file:
                name_file = f"{video_file}.{file_extension}"
                output_file = os.path.join(self.output_path,
                                           f"{self.save.get_data(SaveData.FILE_PREFIX)}{os.path.basename(name_file)}")
                cmd = f'ffmpeg -y -i "{video_file}" -i "{audio_file}" -c copy "{output_file}"'
                subprocess.call(cmd, shell=True)
                self.after_download_audio(video_file, audio_file, output_file)
        except Exception as e:
            print(f"{self.save.get_message('SORRY_ERROR_MSG')}:{str(e)}")

    def download(self, youtube: YouTube, video_choice: Stream):
        print(f"{self.save.get_message('START_DOWNLOAD_MSG')}:-{youtube.title}")
        video_file = video_choice.download(
            output_path=self.output_path,
            filename=self.norm_file_name(f"{youtube.title}_{video_choice.resolution}_{video_choice.fps}")
        )

        if not video_choice.is_progressive:
            self.download_audio_file(youtube, video_file,  f"{video_choice.mime_type.split('/')[-1]}")
        print(f"Video saved at {self.output_path}")

    def print_stream(self, streams: StreamQuery):
        if streams:
            print(self.save.get_message('RESOLUTIONS_MSG') + ":")
            for i, stream in enumerate(streams):
                print(f"{i + 1}) .{stream.mime_type.split('/')[-1]} {stream.resolution}-{stream.fps}fps")
        else:
            print(f"{self.save.get_message('SORRY_ERROR_MSG')} ")

    def filter_streams(self, youtube: YouTube) -> StreamQuery:
        return youtube.streams.filter(file_extension=self.save.get_data(SaveData.FILE_EXTENSION)).order_by(
            'resolution', )

    def choice_and_download(self, youtube: YouTube, streams: StreamQuery, is_playlist: bool = False):
        try:
            choice = input(self.save.get_message('CHOICE_QUALITY_MSG') + ":")
            if not choice:
                video_choice = youtube.streams.get_highest_resolution()
            else:
                choice = int(choice)
                video_choice = streams[choice - 1]
            if not is_playlist:
                youtube.register_on_progress_callback(self.on_progress)
                self.download(youtube, video_choice)
            else:
                return youtube, video_choice

        except Exception as e:
            print(f" {self.save.get_message('SORRY_ERROR_MSG')} : {youtube.title}.{str(e)}")

    def download_video_file(self, youtube: YouTube):
        streams = self.filter_streams(youtube)
        self.print_stream(streams)
        self.choice_and_download(youtube, streams, False)

    def download_videos_file(self, youtube_list: Iterable[YouTube]):
        downloads = []
        length = len(youtube_list)
        for i, youtube in enumerate(youtube_list):
            streams = self.filter_streams(youtube)

            print(f"{i + 1}/{length})-{youtube.title}")

            self.print_stream(streams)

            downloads.append(self.choice_and_download(youtube, streams, True))

        for youtube, video_choice in downloads:
            youtube.register_on_progress_callback(self.on_progress)
            try:
                self.download(youtube, video_choice)
            except Exception as e:
                print(f"{self.save.get_message('SORRY_ERROR_MSG')}: {str(e)}'")

        print(self.save.get_message('END_MESSAGE'))

    def download_single_video(self, link: str):
        youtube = YouTube(link)
        self.download_video_file(youtube)

    def print_title(self, title: str):
        print(f"Title:{title}")

    def download_playlist(self, link: str):
        playlist = Playlist(link)
        self.print_title(playlist.title)
        self.output_path = os.path.join(self.output_path, self.norm_file_name(playlist.title))
        self.download_videos_file(playlist.videos)

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining

        progress = bytes_downloaded / total_size * 100
        print(
            f"\r {self.save.get_message('DOWNLOADING_MSG')} : {progress:.2f}%( {(bytes_downloaded / 1024 / 1024):.2f}Mb/{(total_size / 1024 / 1024):.2f}Mb )",
            end="")

    def launch(self):
        self._banner()
        choice = int(input(self.save.get_message('YOUR_CHOICE_MSG')))
        link = input("Lien de la vidéo ou le Lien de la playliste : ")
        output_path = input("Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
        if not output_path:
            output_path = os.getcwd()
        try:
            link = self.validate_url(link)
            self.output_path = output_path
            if choice == 1:
                self.download_single_video(link)
            else:
                self.download_playlist(link)
        except Exception as e:
            print(f"il semble avoir un souci avec votre lien . Erreur: {str(e)}")


if __name__ == '__main__':
    yt_down = YTDown(Save())
    yt_down.launch()
