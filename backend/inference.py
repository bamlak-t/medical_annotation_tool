from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.llms import Ollama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import logging

TAXONOMY_FILE = 'taxonomy.json'
PROMPT_FILE = 'prompt.txt'
EXAMPLES_FILE = 'examples.json'
MODEL_NAME = 'mistral'
EMBEDDING_MODEL = 'mistral'

class Store:
    """
    Store class to load and store the taxonomy, prompt, and examples
    """

    def __init__(self, taxonomy_file=TAXONOMY_FILE, prompt_file=PROMPT_FILE, examples_file=EXAMPLES_FILE) -> None:
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
            print(f'Error opening or reading file: {file_name}')
            return None
        except KeyError:
            print(f"Missing key '{json_key}' in file: {file_name}")
            return None

    def get_prompt(self):
        return self._prompt

    def get_parsed_taxonomy(self):
        return self._parsed_taxonomy

    def get_taxonomy(self):
        return self._taxonomy

    def get_examples(self):
        return self._examples


class MedNerModel:
    """
    MedNerModel class to annotate text extracts with factors from the taxonomy
    """

    def __init__(self, model_name=MODEL_NAME, embedding_model=EMBEDDING_MODEL) -> None:
        self.llm = Ollama(model=model_name)
        self.embedding_model = embedding_model
        self.store = Store()
        self.setup_chain()
        logging.info(f'MedNerModel initialized with model: {model_name}')

    def setup_chain(self):
        """
        Setup the chain for the model
        """
        self.output_parser = StructuredOutputParser.from_response_schemas([
            ResponseSchema(
                name='text_extract',
                type='string',
                description='Text extract from the medical case'
            ),
            ResponseSchema(
                name='factors',
                type='List[string]',
                description='List of factors associated with the text extract'
            )
        ])

        format_instructions = self.output_parser.get_format_instructions()

        example_prompt = PromptTemplate(
            input_variables=['input', 'output'],
            template='Example Input: {input}\nExample Output: {output}',
        )

        # example_selector = SemanticSimilarityExampleSelector.from_examples(
        #     self.store.get_examples(),
        #     OllamaEmbeddings(model=self.embedding_model),
        #     Chroma,
        #     k=2
        # )

        self.similar_prompt = FewShotPromptTemplate(
            # example_selector=example_selector,
            examples=self.store.get_examples(),
            example_prompt=example_prompt,
            prefix=self.store.get_prompt(),
            suffix='Input: {text_extract}\nOutput:',
            input_variables=['text_extract'],
            partial_variables={'format_instructions': format_instructions},
        )

    def get_annotations(self, text_extract):
        """
        Get the annotations for a given text extract

        Args:
            text_extract (str): text extract to be annotated

        Return:
            dict: dictionary containing annotations
        """
        chain = self.similar_prompt | self.llm
        return chain.invoke({'text_extract': text_extract, 'taxonomy': self.store.get_taxonomy()})

    def get_parsed_annotations(self, text_extract):
        """
        Get the parsed annotations for a given text extract

        Args:
            text_extract (str): text extract to be annotated

        Return:
            dict: dictionary containing parsed annotations
        """
        try:
            annotated = self.get_annotations(text_extract)
            output = self.output_parser.parse(annotated)
            return output
        except Exception as e:
            return {'text_extract': text_extract, 'factors': ['Error parsing annotations']}

    def get_full_prompt(self, text_extract='TEXT_EXTRACT'):
        """
        Construct the full prompt for the model

        Args:
            text_extract (str): text extract to be annotated

        Return:
            str: full prompt for the model
        """
        return self.similar_prompt.format(text_extract=text_extract, taxonomy=self.store.get_taxonomy())


if __name__ == '__main__':
    extract = 'This means that IA was not performed in line with local or national guidance.'

    model = MedNerModel()

    full_prompt = model.get_full_prompt(extract)
    print('full_prompt', full_prompt)

    output = model.get_annotations(extract)
    print('output', output)

    parsed_output = model.get_parsed_annotations(output)

    print('parsed_output', parsed_output)
