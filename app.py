
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import openai
import asyncio
import time
from create_db import load_db
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


# Page  header
st.set_page_config(
    page_title="Tiny NutriKids Guide",
    page_icon="🥙",
    initial_sidebar_state="expanded",
    layout="centered",
)
st.title('Tiny NutriKids Guide 🥙🧒' )

#Initialization
if 'openai_api_key' and "auth_ok" not in st.session_state:
    st.session_state['openai_api_key'] = None
    st.session_state['auth_ok'] = False




class StreamHandler(BaseCallbackHandler):
    '''
    This class will help streaming output from LangChain to Streamlit
    '''

    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token + ""
        display_function = getattr(self.container, self.display_method, None)
        
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")




# Function to load the database
@st.cache(allow_output_mutation=True)
def init_ressource(openai_api_key = st.session_state['openai_api_key']):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key,model="text-embedding-ada-002")
    my_activeloop_dataset_name = 'child_food_and_nutrition_article'
    dataset_path = f"hub://{os.environ['ACTIVELOOP_ORG_ID']}/{my_activeloop_dataset_name}"
    return asyncio.run(load_db(dataset_path, embedding_function = embeddings))
db = init_ressource()


def get_ressource(openai_api_key = st.session_state['openai_api_key']):
    chat_box = st.empty()
    stream_handler = StreamHandler(chat_box, display_method='write')

    llm = OpenAI(streaming=True, callbacks=[stream_handler], openai_api_key=openai_api_key,model_name="text-davinci-003", temperature=0)
    llm_ = OpenAI(openai_api_key=openai_api_key,temperature=0)

    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 3
    retriever.search_kwargs['k'] = 1
    
    chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm_,
                                                    chain_type="stuff",
                                                    retriever=retriever)

    # This is an LLMChain to write the output in the same language as input.
    template = """You are an amazing translator. Given the user input, it is your job to write the answer to his query in the same language as input.

    Question:
    {question}
    Answer:
    {answer}
    Sources:
    {sources}
    
    The review answer including the `Sources` from the input question:
    """
    prompt_template = PromptTemplate(input_variables=["question" ,"answer","sources"], template=template)
    review_chain = LLMChain(llm=llm, prompt=prompt_template,output_key="review")

    return chain,review_chain



# widget for authentication input form
with st.sidebar:
    st.markdown("# 👋 Welcome to NutriKids")
    st.markdown(" ")
    st.markdown("This app provides answer to questions on  child food and nutrition with sourced information.")
    st.markdown("--- ")
    st.title("Authentication")
    with st.form("authentication"):
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Add your Openai API key",
            placeholder="This field is mandatory",
        )

        submitted = st.form_submit_button("Submit")



#Helper functions

def authenticate(openai_api_key: str) -> None:
    openai_api_key = openai_api_key
    
    if not openai_api_key :
        st.error("No credentials")
        return
    try:
        # Try to access openai
        with st.spinner("Authentifying..."):
            openai.api_key = openai_api_key
            openai.Model.list()
    except Exception as e:
        st.error("Authentification failed 🥴")
        return
    # store credentials in the session state
    st.session_state["auth_ok"] = True
    st.session_state["openai_api_key"] = openai_api_key
    st.markdown("#### Authentification succeeded 😎!")


if submitted:
    authenticate(openai_api_key)


user_input = st.text_input(
    label="Ask me a nutrition-related questions:",
    placeholder="Enter your question here!")

ask_button = st.button("send")


def generate_response(user_input: str):
    
    if st.session_state["auth_ok"] == False:
        st.text("Please  input a valid API key and try again.")
        return
    if user_input =="":
        return

    user_input = user_input[:100]
    st.markdown("### Response:")

    chain,review_chain =  get_ressource()
    response =  chain({"question": f"{user_input}"})
    review_chain({"question":response['question'],"answer":response["answer"],"sources":response["sources"]})


if user_input and ask_button:
    
    with st.spinner("In progress..."):
        start = time.time()
        generate_response(user_input)
        end = time.time()


#Collect feedback from users using the trubrics library
from trubrics.integrations.streamlit import FeedbackCollector

collector = FeedbackCollector()
st.markdown(" ")
st.markdown("Feedback")
collector.st_feedback(
	feedback_type="thumbs",
	path="feedback/thumbs_feedback.json",
    open_feedback_label="[Optional] Provide additional feedback",
)

