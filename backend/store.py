import json
import logging

TAXONOMY_FILE = 'constants/taxonomy.json'
PROMPT_FILE = 'constants/prompt.txt'
EXAMPLES_FILE = 'constants/examples.json'

class Store:
    """
    Store class to load and store the taxonomy, prompt, and examples
    """

    def __init__(self, 
                 taxonomy_file=TAXONOMY_FILE, 
                 prompt_file=PROMPT_FILE, 
                 examples_file=EXAMPLES_FILE) -> None:
        self._taxonomy = self._load_file(taxonomy_file)
        self._parsed_taxonomy = self._load_file(taxonomy_file, json_key='taxonomy' , json_file=True)
        self._examples = self._load_file(examples_file, json_key='examples', json_file=True)
        self._prompt = self._load_file(prompt_file)


    @staticmethod
    def _load_file(file_name, json_key='', json_file=False):
        """
        Load a file and return its contents. If json_file is True, parse the file as JSON.

        Args:
            file_name (str): name of the file to load
            json_key (str): key to extract from the JSON file
            json_file (bool): flag to parse the file as JSON

        Return:
            str or dict: contents of the file
        """
        try:
            with open(file_name, 'r') as f:
                if json_file:
                    return json.load(f)[json_key]
                else:
                    return f.read()
        except IOError:
            logging.info(f'Error opening or reading file: {file_name}')
            return None
        except KeyError:
            logging.info(f"Missing key '{json_key}' in file: {file_name}")
            return None

    def get_prompt(self):
        return self._prompt

    def get_parsed_taxonomy(self):
        return self._parsed_taxonomy

    def get_taxonomy(self):
        return self._taxonomy

    def get_examples(self):
        return self._examples


if __name__ == '__main__':
    store = Store()
    print(store.get_prompt())
    print(store.get_taxonomy())
    print(store.get_parsed_taxonomy())
    print(store.get_examples())