import os
import datetime as t
from dotenv import load_dotenv
from llama_index.core.tools import QueryEngineTool
from llama_index.core import Settings, Document, SimpleDirectoryReader, VectorStoreIndex, PromptTemplate
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.packs.agents_coa import CoAAgentPack
# from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import StorageContext,ServiceContext, load_index_from_storage, PromptTemplate, Prompt
from llama_index.core.query_pipeline import QueryPipeline
# from llama_index.core.llms import ChatMessage
from llama_index.core.agent import ReActAgent
import redis

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

def format_upload(context):
    r = redis.Redis(
    host='amusing-katydid-53208.upstash.io',
    port=6379,
    password='Ac_YAAIncDFiM2I4ZTE5YzkzYjA0YTRlOTExYTdmODBlZjQ2NTIzYXAxNTMyMDg',
    ssl=True
    )
    format1 = str(context)
    h = r.set('Santosh2003', format1)
    return [h, format1]

def check_first():
    r = redis.Redis(
    host='amusing-katydid-53208.upstash.io',
    port=6379,
    password='Ac_YAAIncDFiM2I4ZTE5YzkzYjA0YTRlOTExYTdmODBlZjQ2NTIzYXAxNTMyMDg',
    ssl=True
    )
    h = r.get('Santosh2003')
    return h

def get_data():
    r = redis.Redis(
    host='amusing-katydid-53208.upstash.io',
    port=6379,
    password='Ac_YAAIncDFiM2I4ZTE5YzkzYjA0YTRlOTExYTdmODBlZjQ2NTIzYXAxNTMyMDg',
    ssl=True
    )
    h = r.get('Santosh2003')
    return str(h,'utf-8')


class Agent:
    def __init__(self, chat_history):
        self.memory = chat_history
        self.llm = Gemini(model_name="models/gemini-pro", safety_settings=None)
        self.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

    def agent2(self, user_input, edit) -> list:
        storage_context = StorageContext.from_defaults(persist_dir="Storage")
        index1 = load_index_from_storage(storage_context)
        knowledge = index1.as_query_engine(memory=self.memory)

        # if os.path.exists("./Brain/Accepted"):
        #     storage_context2 = StorageContext.from_defaults(persist_dir="./Brain/Accepted")
        #     examples = load_index_from_storage(storage_context2)
        #     ex = examples.as_query_engine(memory=self.memory)
        # else:
        #     documents = SimpleDirectoryReader("./Data").load_data()
        #     service_context = ServiceContext.from_defaults(chunk_size=512, llm=self.llm, embed_model=self.embed_model)
        #     index2 = VectorStoreIndex.from_documents(documents, service_context=service_context)
        #     index2.storage_context.persist(persist_dir="./Brain/Accepted")
        #     storage_context3 = StorageContext.from_defaults(persist_dir="./Brain/Accepted")
        #     examples = load_index_from_storage(storage_context3)
        #     ex = examples.as_query_engine(memory=self.memory)

        query_engine_tools1 = [
            QueryEngineTool.from_defaults(
                query_engine=knowledge,
                name="KnowledgeBase",
                description=(
                    "Provides information about Content you should write as a copywriter."
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ]
        
        # query_engine_tools2 = [
        #     QueryEngineTool.from_defaults(
        #         query_engine=ex,
        #         name="PreviousAcceptedTasks",
        #         description=(
        #             "Provides information about your previous tasks which was accepted by the user or clint,"
        #             "use this tool to rewrite the context in the users format."
        #             "make sure to refer the previous accepted tasks pattern to do your new tasks."
        #             "Use a detailed plain text question as input to the tool."
        #         ),
        #     ),
        # ]
        
        # query_engine_tools = [
        #     QueryEngineTool.from_defaults(
        #         query_engine=knowledge,
        #         name="KnowledgeBase",
        #         description=(
        #             "Note: access this tool only before using PreviousAcceptedTasks tool, not after that,"
        #             "make sure to run the PreviousAcceptedTasks tool later without missing it."
        #             "Provides information about Content you should write as a copywriter."
        #             "Use a detailed plain text question as input to the tool."
        #         ),
        #     ),
        #     QueryEngineTool.from_defaults(
        #         query_engine=ex,
        #         name="PreviousAcceptedTasks",
        #         description=(
        #             "Note: access this tool only after using KnowledgeBase tool, not before that."
        #             "Provides information about your previous tasks which was accepted by the user or clint,"
        #             "make sure to refer the previous accepted tasks pattern to do your new tasks."
        #             "Use a detailed plain text question as input to the tool."
        #         ),
        #     ),
        # ]
        if check_first() == None or edit == True:
            pack = ReActAgent(tools=query_engine_tools1, llm=self.llm, memory=self.memory, verbose=True)
            response1 = pack.chat(user_input)
            response = response1.response
        else:
            pack = ReActAgent(tools=query_engine_tools1, llm=self.llm, memory=self.memory, verbose=True)
            response1 = pack.chat(user_input)
            response = response1.response
            get_format = get_data() 
            response = self.rewrite(context=str(response), format=str(get_format))
        
        return [response]
    
    
    def rewrite(self, context, format):
        prompt = """Rewrite the below context
                    -------------------------------
                    {context}
                    -------------------------------
                    in the given below format (not same but similar to it).
                    Format: {format}
                """
        template_var_mappings = {"context": "context", "format": "format"}
        prompt_tmpl = PromptTemplate(prompt, template_var_mappings=template_var_mappings)
        
        fmt_prompt = prompt_tmpl.format(
                context=context,
                format=format,
        )
        p = QueryPipeline(chain=[prompt_tmpl, self.llm], verbose=True)
        output = p.run(context=context, format = format)
        return str(output)
    
    
    
    def InsertDocument(self, index, response) -> None:
        formated_str = format_upload(response) 




# if __name__ == "__main__":
#     llm = Gemini(model_name="models/gemini-pro", safety_settings=None)
#     chat_history = []
#     memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=chat_history, token_limit=3500)
#     agent = Agent(chat_history=memory)
#     loop = True
#     while loop:
#         i = input("input:  ")
#         res = agent.agent2(i)
#         response = res[0]
#         index = res[1]
#         chat_history.append(ChatMessage(role="user", content=i))
#         chat_history.append(ChatMessage(role="assistant", content=response))
#         print("------------------------------------------------------------")
#         print(response)
#         inp = input("choose: ")
#         if inp == "y":
#             agent.InsertDocument(index, response)
#         else:
#             loop = True
