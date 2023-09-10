# 👋 Welcome to Tiny NutriKids Guide 🥙🧒

This app provides answers to questions related to  child food and nutrition with sourced information. The responses are provided in the same language as the input questions.

This work is inspired by this [course](https://learn.activeloop.ai/order?ct=c8c2189a-b8ef-4f77-a5b4-ef225ee6d385), offered by [Gen AI 360](https://learn.activeloop.ai/courses/langchain).

## Description

The following points outline the steps used to achieve the task:
- Scrape online nutritional articles and store each article's text content and URL in a JSON format.

- Use an embedding model to compute embeddings of these documents and store them in [Deep Lake](https://www.deeplake.ai/) vector database.

- Split the article texts into smaller chunks, keeping track of each chunk's source.

- Utilize RetrievalQAWithSourcesChain to create a chatbot that retrieves answers and tracks their sources.

- Generate a response to a query using the chain and display the answer along with its sources.

## Setup and Run the app
1. Clone the repo 
2. create an activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
   ```
3. Install the requirements
```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
   ```
4. Setup the .env file by adding
  ```bash
OPENAI_API_KEY=<OPENAI_API_KEY>
ACTIVELOOP_ORG_ID=<ACTIVELOOP_ORG_ID>
ACTIVELOOP_TOKEN=<ACTIVELOOP_TOKEN>
   ```
5. Test the app
```bash
streamlit run app.py
```
