import os
from dotenv import load_dotenv
import autogen
from autogen import config_list_from_json

dotenv_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)


class GetConfig:
    """
    Get and enrich config from config file.
    """

    def __init__(self):
        """
        Initialize with API key and config list.
        """
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.config_list = self.load_and_enrich_config_list()

    @property
    def base_dir(self):
        """
        Returns the base directory path.
        """
        return os.path.dirname(os.path.dirname(__file__))

    def load_and_enrich_config_list(self):
        """
        Loads config list from a JSON file and enriches it with the API key.
        """
        config_path = os.path.join(
            os.path.dirname(__file__), "OAI_CONFIG_LIST")

        config_list = config_list_from_json(
            env_or_file=config_path,
            filter_dict={"model": "gpt-4-turbo-preview"}
        )
        for config in config_list:
            config['api_key'] = self.api_key

        return {'config_list': config_list}