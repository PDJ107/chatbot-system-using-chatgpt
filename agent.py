import configparser
from langchain import SerpAPIWrapper, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationSummaryBufferMemory
from tools.retrievers import CustomRetriever
from tools.places import CustomPlacesTool
from reader.prompts import CustomPromptTemplate
from reader.parser import CustomOutputParser
from elasticsearch import Elasticsearch
from messages import SpecificFCM
import pickle
import base64


class Agent:

    def __init__(self, client: Elasticsearch, index_name: str, memory_pickle: str, message_client: SpecificFCM | None = None, config_path='resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.message_client = message_client
        self.llm = ChatOpenAI(
            openai_api_key=config['OPENAI']['API_KEY'],
            temperature=0,
            model='gpt-3.5-turbo'
        )
        self.tools = [
            Tool(
                name="Search",
                description="A search engine. Useful for when you need to answer questions about current events. Input should be a search query. Lets you search for a phone number.",
                func=SerpAPIWrapper(serpapi_api_key=config['SERP']['KEY']).run,
                coroutine=SerpAPIWrapper(serpapi_api_key=config['SERP']['KEY']).arun,
            ), Tool(
                name="한기대 정보 검색",
                func=CustomRetriever(client, index_name).get_relevant_documents,
                description="한기대 공지사항이나 학사 관련 정보를 검색해야할 때 사용합니다."
            ), Tool(
                name="장소 검색",
                func=CustomPlacesTool(config_path).run,
                description="장소를 검색하는데 사용합니다."
            )
        ]
        self.prompt = CustomPromptTemplate(
            template=config['OPENAI']['TEMPLATE'],
            tools=self.tools,
            input_variables=["input", "intermediate_steps", "chat_history"]
        )
        if memory_pickle == '':
            self.memory = ConversationSummaryBufferMemory(
                memory_key="chat_history",
                llm=self.llm,
                max_token_limit=650,
                return_messages=True
            )
        else:
            self.memory = pickle.loads(base64.b64decode(memory_pickle))
        self.agent = LLMSingleActionAgent(
            llm_chain=LLMChain(llm=self.llm, prompt=self.prompt),
            output_parser=CustomOutputParser(message_client),
            stop=["\nObservation:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
        self.failed = config['OPENAI']['FAILED']

    def run(self, query) -> (str, str):
        try:
            answer = self.agent_executor.run(query)
            if self.message_client is not None:
                self.message_client.send_message(answer)
            return answer, base64.b64encode(pickle.dumps(self.agent_executor.memory)).decode('utf-8')
        except ValueError as e:
            print(e)
            self.message_client.send_message(self.failed)
            return self.failed, base64.b64encode(pickle.dumps(self.agent_executor.memory)).decode('utf-8')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('resources/config.ini')

    client = Elasticsearch(
        config['ES']['URL'],
        request_timeout=60*1
    )
    agent = Agent(
        client,
        config['RETRIEVER']['INDEX'],
        message_client=SpecificFCM(config['FCM']['TEST_TOKEN'])
    )
    agent.run("한기대 주소")
