"""Code to initialize configuration files."""
import configparser


@staticmethod
def load_config():
    """Initializes configuration file."""
    config = configparser.ConfigParser()
    config.read('../config_files/spotify-billboard-charts-config.ini')
    return config
