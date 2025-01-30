import yaml

from src.config.models.settings_model import SettingsModel


class Settings:
    def __init__(self, file: str):
        self.__file = file
        self.config_data = self._get_config_data()

    def _get_config_data(self) -> SettingsModel:
        with open(self.__file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return SettingsModel(**data)
