"""Code to initialize configuration files."""
import configparser


def load_config():
    """Initializes configuration file."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    private_config_file = config['private']['config_file']
    config.read(private_config_file)
    return config


if __name__ == "__main__":
    load_config()
