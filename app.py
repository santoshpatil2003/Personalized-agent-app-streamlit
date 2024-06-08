import streamlit as st
import os
from llama_index.llms.gemini import Gemini
from Backend import Agent
from Embedding import DataSaver
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer

def datascraper(uploaded_files) -> bool:
    if uploaded_files is not None:
        with st.spinner('Wait for it...'):
            url = f'./Data/{uploaded_files.name}'
            f = open(f"{url}", 'wb')
            f.write(uploaded_files.getvalue())
            DataSaver()
        st.success('Done!')
        

st.info("""This personalized agent will respond to your query based on the previous task it completed for you, just like a human.\n
           Note: First, teach the agent what type of output you require and click the 
          "Accept" button. The next time you ask a question, the results will be 
          similar to what you expected.
        """)
        
st.title("Personalized Agent")
llm = Gemini(model_name="models/gemini-pro", safety_settings=None)


if "messages" and "history" and "uploaded" and "index" and "upload" and "edit" not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.edit = False
    if os.path.exists("Data"):
        st.session_state.uploaded = len(os.listdir("Data")) > 1
        st.session_state.upload = not len(os.listdir("Data")) > 1
    else:
        st.session_state.uploaded = False
        st.session_state.upload = True
    st.session_state.index = ""
    
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        

memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=st.session_state.history, token_limit=3500)
agent = Agent(chat_history=memory)
    
# if os.path.exists("Data"):
#     st.session_state.uploaded = len(os.listdir("Data")) > 0
#     st.session_state.upload == False
# else:
#     st.session_state.uploaded = False
if prompt := st.chat_input("What is up?", disabled= not st.session_state.uploaded):

    
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.history.append(ChatMessage(role="user", content=prompt))
    
    res = agent.agent2(prompt, st.session_state.edit)
    response = res[0]
    # st.session_state.index = res[1]

    with st.chat_message("assistant"):
        st.write(response)
        
        
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.history.append(ChatMessage(role="assistant", content=response))
    
    
    
def call():
    with st.spinner('Wait for it...'):
        li = st.session_state.messages
        agent.InsertDocument(index=st.session_state.index ,response=li[len(li) - 1]["content"])
    st.success('Done!')
    
def de():
    st.session_state.uploaded = True
    st.session_state.upload = True
    
with st.sidebar:
    uploaded_files = st.file_uploader("Choose a txt file",on_change=de)
    if st.session_state.uploaded == True and st.session_state.upload == True:
        datascraper(uploaded_files=uploaded_files)
        st.session_state.uploaded = True
        st.session_state.upload = False
    
    st.info("""The button below accepts the type of output you want the agent to produce each time you ask it to.""")
    st.button("Accept", type="primary", on_click=call)
    
    st.info("""Use the below toggle button to edit your agents output.
               toggle it and chat with your agent.
               Note: if you don't toggle it and try to change the agent's output 
          it will not work.
            """)
    on = st.toggle("Edit agent")

    if on:
        st.session_state.edit = True
    else:
        st.session_state.edit = False

