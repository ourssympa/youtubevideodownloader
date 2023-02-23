import re
from typing import Iterable

from tqdm import tqdm
from pytube import YouTube
from pytube import Playlist
from pytube import StreamQuery
from pytube import Stream
import os
import subprocess

WELCOME_STR = """ __   __  _______    ______   _______  _     _  __    _ 
    |  | |  ||       |  |      | |       || | _ | ||  |  | |
    |  |_|  ||_     _|  |  _    ||   _   || || || ||   |_| |
    |       |  |   |    | | |   ||  | |  ||       ||       |
    |_     _|  |   |    | |_|   ||  |_|  ||       ||  _    |
      |   |    |   |    |       ||       ||   _   || | |   |
      |___|    |___|    |______| |_______||__| |__||__|_|  |__|

        1-) Download youtube video
        2-) Download youtube playliste
        
        """
INVALID_LINK_MESSAGE = "Le lien n'est pas valide."
RESOLUTIONS_MESSAGE = "Qualités disponibles "
FILE_EXTENSION = 'mp4'
CHOICE_QUALITY_MESSAGE = "Choisissez une qualité (entrez un nombre ou/ laisser vide pour utiliser la " \
                         "highest_resolution) "
START_DOWNLOAD_MESSAGE = "-----------Début du téléchargement-----------"
END_MESSAGE = "-----------Fin-----------"
DEBUG = False


def _banner():
    print(WELCOME_STR)


def validate_url(link: str) -> str:
    pattern = re.compile(
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?|^(https?://)?(www\.)?youtu\.be/[\w-]+$')
    if pattern.match(link):
        return link
    else:
        raise ValueError(INVALID_LINK_MESSAGE)


def norm_file_name(name: str) -> str:
    new = ""
    for c in name:
        if c.isalnum() or c in {"_", ".", "-"}:
            new += c
        else:
            new += "_"
    return new

def after_download_audio(video_file: str, audio_file: str, output_file: str):
    os.remove(video_file)
    os.remove(audio_file)
    file_path = output_file
    file_name = os.path.basename(file_path)
    new_name = file_name.replace("join-", "")
    new_path = os.path.join(os.path.dirname(file_path), new_name)
    os.rename(file_path, new_path)


def download_audio_file(yt: YouTube, video_file: str, output_path: str, file_extension: str):
    try:
        audio = yt.streams.get_audio_only()
        yt.register_on_progress_callback(on_progress)
        print(f"{START_DOWNLOAD_MESSAGE}: {yt.title}-(Audio)")
        audio_file = audio.download(
            output_path=output_path, filename=f"{norm_file_name(yt.title)}.mp3"
        )
        if DEBUG:
            print(f"yt{yt},video-path{video_file},audio_path{audio_file}")
        if audio_file:
            name_file = f"{video_file}.{file_extension}"
            output_file = os.path.join(output_path, f"join-{os.path.basename(name_file)}")
            cmd = f'ffmpeg -y -i "{video_file}" -i "{audio_file}" -c copy "{output_file}"'
            subprocess.call(cmd, shell=True)
            after_download_audio(video_file, audio_file, output_file)
    except Exception as e:
        print(f"Error:{str(e)}")





def download(youtube: YouTube, video_choice: Stream, output_path: str):
    print(f"{START_DOWNLOAD_MESSAGE}:-{youtube.title}")
    video_file = video_choice.download(
        output_path=output_path,
        filename=norm_file_name(f"{youtube.title}_{video_choice.resolution}_{video_choice.fps}")
    )

    if not video_choice.is_progressive:
        download_audio_file(youtube, video_file, output_path, f"{video_choice.mime_type.split('/')[-1]}")
    print(f"Video enregistrée sous {output_path}")
def print_stream(streams:StreamQuery):
    for i, stream in enumerate(streams):
        print(f"{i + 1}) .{stream.mime_type.split('/')[-1]} {stream.resolution}-{stream.fps}fps")
def download_video_file(youtube: YouTube, output_path: str):
    streams = youtube.streams.filter(file_extension=FILE_EXTENSION).order_by('resolution')
    print(RESOLUTIONS_MESSAGE + ":")
    if streams:
        print_stream(streams)

        try:
            choice = input(CHOICE_QUALITY_MESSAGE + ":")
            if not choice:
                video_choice = youtube.streams.get_highest_resolution()
            else:
                choice = int(choice)
                video_choice = streams[choice - 1]
            youtube.register_on_progress_callback(on_progress)
            download(youtube, video_choice, output_path)

        except Exception as e:
            print(f"Le téléchargement a échoué pour {youtube.title}. Erreur: {str(e)}")
    else:
        print('Aucune qualité vidéo disponible pour la vidéo', youtube.title)


def download_videos_file(youtubes: Iterable[YouTube], output_path: str):
    downloads = []
    length = len(youtubes)
    for i, youtube in enumerate(youtubes):
        streams = youtube.streams.filter(file_extension=FILE_EXTENSION).order_by('resolution')

        print(f"{i + 1}/{length})-{youtube.title}")
        if streams:
            print_stream(streams)
            try:
                choice = input(CHOICE_QUALITY_MESSAGE + ":")
                if not choice:
                    video_choice = youtube.streams.get_highest_resolution()
                else:
                    choice = int(choice)
                    video_choice = streams[choice - 1]
                downloads.append((youtube, video_choice))
            except Exception as e:
                print(f"Le téléchargement a échoué pour {youtube.title}. Erreur: {str(e)}")
        else:
            print('Aucune qualité vidéo disponible pour la vidéo', youtube.title)
    for youtube, video_choice in downloads:
        youtube.register_on_progress_callback(on_progress)
        #print(f"{START_DOWNLOAD_MESSAGE}:{youtube.title}")
        try:
            download(youtube, video_choice, output_path)
        except Exception as e:
            print(f'Erreur: {str(e)}')

    print(END_MESSAGE)





def download_single_video(link: str, output_path: str):
    youtube = YouTube(link)
    #print(youtube.title)
    download_video_file(youtube, output_path)


def download_playlist(link: str, output_path: str):
    playlist = Playlist(link)
    print(f"Title:{playlist.title}")
    output_path = os.path.join(output_path, norm_file_name(playlist.title))

    download_videos_file(playlist.videos, output_path)


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    progress = bytes_downloaded / total_size * 100
    print(
        f"\rTéléchargement en cours: {progress:.2f}%( {(bytes_downloaded / 1024 / 1024):.2f}Mb/{(total_size / 1024 / 1024):.2f}Mb )",
        end="")


def _main():
    _banner()
    choice = int(input('Votre choix: '))
    link = input("Lien de la vidéo ou le Lien de la playliste : ")
    output_path = input("Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
    if not output_path:
        output_path = os.getcwd()
    try:
        link = validate_url(link)
        if choice == 1:
            download_single_video(link, output_path)
        else:
            download_playlist(link, output_path)
    except Exception as e:
        print(f"il semble avoir un souci avec votre lien . Erreur: {str(e)}")


if __name__ == '__main__':
    _main()
