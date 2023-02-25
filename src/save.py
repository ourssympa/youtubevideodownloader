import json
from datetime import datetime
from Enumeration import SaveData


class Save:
    def __init__(self):
        self.file_name = "config.json"
        self.data = {
            "DEBUG": False,
            "FILE_EXTENSION": "mp4",
            "FILE_PREFIX": "join-",
            'MESSAGES': {
                "OPTION_MSG_START": "Download youtube",
                "INVALID_LINK_MSG": "Le lien n'est pas valide.",
                "RESOLUTIONS_MSG": "Qualités disponibles ",
                "CHOICE_QUALITY_MSG": "Choisissez une qualité (entrez un nombre ou/ laisser vide pour utiliser la "
                                      "highest_resolution) ",
                "START_DOWNLOAD_MSG": "-----------Début du téléchargement-----------",
                "END_MSG": "-----------Fin-----------",
                "DOWNLOADING_MSG": "Downloading",
                "SORRY_ERROR_MSG": "Sorry Error ",
                "YOUR_CHOICE_MSG": 'Votre choix: '
            }

        }
        # self.save_data()
        self.restore_data()
        self.OPTIONS_CHOICE_STR: list = [

            f"{self.get_message('OPTION_MSG_START')} video",
            f"{self.get_message('OPTION_MSG_START')} playlist"
        ]

    def save_data(self):
        self.data['last_run'] = str(datetime.now())
        with open(self.file_name, 'w') as file:
            json.dump(self.data, file)

    def restore_data(self):
        try:
            with open(self.file_name) as file:
                self.data = json.load(file)
        except Exception as e:
            self.save_data()
            print(e)

    def get_data(self, data: SaveData):
        try:
            if data == SaveData.DEBUG:
                return self.data['DEBUG']
            elif data == SaveData.DEBUG:
                return self.data['DEBUG']
            elif data == SaveData.FILE_EXTENSION:
                return self.data['FILE_EXTENSION']
            elif data == SaveData.FILE_PREFIX:
                return self.data['FILE_PREFIX']
            elif data == SaveData.MESSAGES:
                return self.data['MESSAGES']
        except Exception as e:
            print(e)

    def get_message(self, key: str) -> str:
        try:
            return self.get_data(SaveData.MESSAGES)[key]
        except Exception as e:
            print(e)
            return ""
