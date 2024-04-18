from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

class Manager:
    """
    Inference class manages the input and output of the model
    """

    def __init__(self, store):
        self.store = store

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

        self.few_shot_template = FewShotPromptTemplate(
            examples=self.store.get_examples(),
            example_prompt=example_prompt,
            prefix=self.store.get_prompt(),
            suffix='Input: {text_extract}\nOutput:',
            input_variables=['text_extract'],
            partial_variables={'format_instructions': format_instructions},
        )

    def get_full_prompt(self, text_extract=''):
        """
        Construct the full prompt for the model

        Args:
            text_extract (str): text extract to be annotated

        Return:
            str: full prompt for the model
        """
        return self.few_shot_template.format(text_extract=text_extract, taxonomy=self.store.get_taxonomy())