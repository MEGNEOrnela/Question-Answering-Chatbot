from dotenv import load_dotenv

load_dotenv()
import json
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import DeepLake

from langchain.text_splitter import RecursiveCharacterTextSplitter






def create_db(dataset_path: str, json_filepath: str) -> DeepLake:

    '''
        This function compute the embeddings of the documents using OpenAIEmbeddings and store them in Deep Lake.
        The documents are breaking down into smaller chunks, and for each chunk, it save its corresponding URL as a source.
    '''

    with open(json_filepath, "r") as f:
        pages_content = json.load(f)

        
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    all_texts, all_metadatas = [], []
    for d in pages_content:
        chunks = text_splitter.split_text(d["text"])
        for chunk in chunks:
            all_texts.append(chunk)
            all_metadatas.append({ "source": d["url"] })
        
    db = DeepLake.from_texts(all_texts, embeddings, metadatas=all_metadatas, dataset_path=dataset_path
    )

    return db



async def load_db(dataset_path: str, *args, **kwargs) -> DeepLake:
    db = DeepLake(dataset_path, *args, **kwargs)
    return db


if __name__ == "__main__":
    my_activeloop_dataset_name = "child_food_and_nutrition_article"
    dataset_path = f"hub://{os.environ['ACTIVELOOP_ORG_ID']}/{my_activeloop_dataset_name}"
    create_db(dataset_path, "data/article_content.json")
