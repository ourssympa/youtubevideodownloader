import re
from tqdm import tqdm
from pytube import YouTube
from pytube import Playlist
from pytube import StreamQuery
import os

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
CHOICE_QUALITY_MESSAGE = "Choisissez une qualité (entrez un nombre ou/ laisser vide pour utiliser la highest_resolution) "
START_DOWNLOAD_MESSAGE = "-----------Début du téléchargement-----------"
END_MESSAGE = "-----------Fin-----------"


def _banner ():
    print(WELCOME_STR)

def validate_url(link:str) -> str:
    pattern = re.compile(r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?|^(https?://)?(www\.)?youtu\.be/[\w-]+$')
    if pattern.match(link):
        return link
    else:
        raise ValueError(INVALID_LINK_MESSAGE)
def validate_output_path(output_path: str) -> str:
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    elif not os.access(output_path, os.W_OK):
        raise ValueError(f"Le chemin {output_path} n'est pas accessible en écriture.")
    return output_path

def download(streams: StreamQuery, output_path: str, video_title: str, is_playlist: bool = False, file_extension: str = 'mp4'):
    print(RESOLUTIONS_MESSAGE + ":")
    for i, stream in enumerate(streams.filter(file_extension=file_extension)):
        print(f"{i + 1}) {stream.resolution}")
    try:

        choice = input(CHOICE_QUALITY_MESSAGE + " ")

        if not choice:
            video = streams.get_highest_resolution()
        else:
            choice = int(choice)
            video = streams.filter(file_extension=file_extension)[choice - 1]

        print(START_DOWNLOAD_MESSAGE)
    

        video.download(output_path=output_path)
    except Exception as e:
        print(f"Le téléchargement a échoué pour {video_title}. Erreur: {str(e)}")

    
def video(link: str, output_path: str):
    youtube = YouTube(link,on_progress_callback=on_progress)
    print(youtube.title)
    streams = youtube.streams.filter(progressive=True, file_extension=FILE_EXTENSION).order_by('resolution')
    download(streams,output_path,youtube.title)





def playliste(link: str, output_path: str):
    playlist = Playlist(link)
    print(playlist.title)
    output_file_path = os.path.join(output_path, playlist.title)
    for video in playlist.videos:
        print(START_DOWNLOAD_MESSAGE)
        try:
            print(video.title)
            video_streams = video.streams.filter(progressive=True, file_extension=FILE_EXTENSION).order_by('resolution')

            download(video_streams,output_file_path,video.title,True)
        except:
            print('Erreur')
        print(END_MESSAGE)


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    progress = bytes_downloaded / total_size * 100
    print(f"\rTéléchargement en cours: {progress:.2f}%", end="")

def _Main():
    _banner()
    choice = int(input('Votre choix: '))
    link = input("Lien de la vidéo ou le Lien de la playliste : ")
    output_path = input("Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
    if not output_path:
      output_path = os.getcwd()
    try:
      link = validate_url(link)
      output_path = validate_output_path(output_path)
      if choice == 1:
        video(link, output_path)
      else:
        playliste(link, output_path)
    except Exception as e:
      print(f"il semble avoir un souci avec votre lien . Erreur: {str(e)}")


if __name__ == '__main__':
    _Main()
