from pytube import YouTube
from pytube import Playlist

def _banner ():
    print(""" __   __  _______    ______   _______  _     _  __    _ 
    |  | |  ||       |  |      | |       || | _ | ||  |  | |
    |  |_|  ||_     _|  |  _    ||   _   || || || ||   |_| |
    |       |  |   |    | | |   ||  | |  ||       ||       |
    |_     _|  |   |    | |_|   ||  |_|  ||       ||  _    |
      |   |    |   |    |       ||       ||   _   || | |   |
      |___|    |___|    |______| |_______||__| |__||_|  |__|

        1-) Download youtube video
        2-) Download youtube playliste
        """)
def video(link):
    youtube=YouTube(link)
    print(youtube.title)
    print("Debut du Telechargement")
    try:
      video=youtube.streams.get_highest_resolution()
    except:
        print('Erreur')
    video.download()

def playliste(link):
    playlist = Playlist(link)
    for video in playlist.videos :

        print("-----------Debut du Telechargement-----------")
        try:
          stream = video.streams.get_highest_resolution().download()
        except:
          print('Erreur')
        print(video.title)
        print("-----------Fin-----------")



def _Main ():

  _banner()

  choice = int(input('votre choix'))
  if choice ==1:
    link=input("Lien de la video :")
    video(link)
  else:
    link=input("Lien de la playliste :")
    playliste(link)
_Main()