from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.llms import Ollama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import pandas as pd
import numpy as np
import time
import json

class Store:
    def __init__(self) -> None:
        with open('taxonomy.json', 'r') as f:
            self._taxonomy = f.read()
            self._parsed_taxonomy = json.loads(self._taxonomy)

        with open('prompt.txt', 'r') as f:
            self._prompt = f.read()

        with open('examples.json', 'r') as f:
            examples = json.load(f)
            self._examples = examples["examples"]
        
        # print(1, self._taxonomy, type(self._taxonomy))
        # print(2, self._parsed_taxonomy, type(self._parsed_taxonomy))
        # print(3, self._prompt, type(self._prompt))
        # print(4, self._examples, type(self._examples))
        

    def get_prompt(self):
        return self._prompt

    def get_parsed_taxonomy(self):
        return self._parsed_taxonomy
    
    def get_taxonomy(self):
        return self._taxonomy

    def get_examples(self):
        return self._examples

class MedNerModel:
    def __init__(self, model_name, embedding_model) -> None:
        self.llm = Ollama(model=model_name)
        self.embedding_model = embedding_model
        self.store = Store()
        self.setup_chain()
    
    def get_full_prompt(self, text_extract="TEXT_EXTRACT"):
        return self.similar_prompt.format(text_extract=text_extract, taxonomy=self.store.get_taxonomy())
    
    def setup_chain(self):
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
            input_variables=["input", "output"],
            template="Example Input: {input}\nExample Output: {output}",
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
            suffix="Input: {text_extract}\nOutput:",
            input_variables=["text_extract"],
            partial_variables={"format_instructions": format_instructions},
        )


    def get_annotations(self, text_extract):
        chain = self.similar_prompt | self.llm
        return chain.invoke({"text_extract": text_extract, "taxonomy": self.store.get_taxonomy()})

    def get_parsed_annotations(self, text_extract):
        try:
            annotated = self.get_annotations(text_extract)
            output = self.output_parser.parse(annotated)
            return output
        except Exception as e:
            return {"text_extract": text_extract, "factors": ["Error parsing annotations"]}


if __name__ == "__main__":
    extract = "This means that IA was not performed in line with local or national guidance."

    model = MedNerModel("mistral", "mistral")

    full_prompt = model.get_full_prompt(extract)
    print("full_prompt", full_prompt)

    output = model.get_annotations(extract)
    print("output", output)

    parsed_output = model.get_parsed_annotations(output)

    print("parsed_output", parsed_output)