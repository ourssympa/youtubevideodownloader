import re
from tqdm import tqdm
from pytube import YouTube
from pytube import Playlist
import os


def _banner ():
    print(""" __   __  _______    ______   _______  _     _  __    _ 
    |  | |  ||       |  |      | |       || | _ | ||  |  | |
    |  |_|  ||_     _|  |  _    ||   _   || || || ||   |_| |
    |       |  |   |    | | |   ||  | |  ||       ||       |
    |_     _|  |   |    | |_|   ||  |_|  ||       ||  _    |
      |   |    |   |    |       ||       ||   _   || | |   |
      |___|    |___|    |______| |_______||__| |__||__|_|  |__|

        1-) Download youtube video
        2-) Download youtube playliste
        
        """)

def validate_url(link:str) -> str:
    pattern = re.compile(r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?|^(https?://)?(www\.)?youtu\.be/[\w-]+$')
    if pattern.match(link):
        return link
    else:
        raise ValueError("Le lien n'est pas valide.")

import os

def video(link: str, output_path: str):
    youtube = YouTube(link,on_progress_callback=on_progress)
    print(youtube.title)
    print("Début du téléchargement")
    streams = youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
    print("Qualités disponibles :")
    for i, stream in enumerate(streams):
        print(f"{i+1}) {stream.resolution}")
    try:
        choice = input("Choisissez une qualité (entrez un nombre): ")
        if not choice:
            video = youtube.streams.get_highest_resolution()
        else:
            choice = int(choice)
            video = streams[choice-1]
        video.download(output_path=output_path)
    except Exception as e:
        print(f"Le téléchargement a échoué pour {youtube.title}. Erreur: {str(e)}")





def playliste(link: str, output_path: str):
    playlist = Playlist(link)
    print(playlist.title)
    for video in playlist.videos:
        print("-----------Début du téléchargement-----------")
        try:
            print(video.title)
            video_streams = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
            if video_streams:
                video_choice = video_streams[-1]
                video_choice.download(output_path=output_path)
            else:
                print('Aucune qualité vidéo disponible pour la vidéo', video.title)
        except:
            print('Erreur')
        print("-----------Fin-----------")


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    progress = bytes_downloaded / total_size * 100
    print(f"\rTéléchargement en cours: {progress:.2f}%", end="")

def _Main():
    _banner()

    choice = int(input('Votre choix: '))
    if choice == 1:
        link = input("Lien de la vidéo : ")
        output_path = input("Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
        if not output_path:
            output_path = os.getcwd()
        video(link, output_path)
    else:
        link = input("Lien de la playliste : ")
        output_path = input("Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
        if not output_path:
            output_path = os.getcwd()
        playliste(link, output_path)


if __name__ == '__main__':
    _Main()
