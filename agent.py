import configparser
from langchain import SerpAPIWrapper, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationSummaryBufferMemory
from tools.retrievers import CustomRetriever
from tools.places import CustomPlacesTool
from tools.assignments import Assignment
from tools.timer import Timer
from reader.prompts import CustomPromptTemplate
from reader.parser import CustomOutputParser
from elasticsearch import Elasticsearch
from messages import SpecificFCM
from firebase_admin import credentials
import firebase_admin
import pickle
import base64


class Agent:

    def __init__(
            self,
            client: Elasticsearch,
            index_name: str,
            memory_pickle: str,
            portal_id: str,
            portal_pw: str,
            background_tasks,
            message_client: SpecificFCM = None,
            config_path='resources/config.ini',
    ):
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
                description="한기대 관련 정보나 공지사항, 학사 정보, 일정을 찾을 때 유용합니다."
            ), Tool(
                name="장소 검색",
                func=CustomPlacesTool(config_path).run,
                description="장소를 검색할 때 사용한다."
            ), Tool(
                name="Assignments",
                func=Assignment(portal_id, portal_pw).run,
                description='''
                과제나 퀴즈 정보를 알아야 할 때 유용합니다.
                유저의 과제나 퀴즈 정보를 json 형태로 가져옵니다.
                마감일 순으로 정렬되어 있습니다.
                The json form is as follows.
                {
                    'type': assignment type,
                    'subject_name': subject name,
                    'name': assignment name,
                    'schedule': {'start': start of assignment, 'end': end of assignment}
                }
                '''
            ), Tool(
                name="Timer",
                func=Timer(
                    background_tasks=background_tasks,
                    message_client=message_client
                ).run,
                description='특정 시간에 메시지를 예약해야할 때 유용합니다. The format is as follows. {"message": "message string", "time": "%Y-%m-%d %H:%M:%S.%f"}. Final Answer은 "메시지 예약이 완료되었습니다."로 해주세요.'
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
            output_parser=CustomOutputParser([tool.name for tool in self.tools], message_client),
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
                self.message_client.send_message(answer, final=True)
            return answer, base64.b64encode(pickle.dumps(self.agent_executor.memory)).decode('utf-8')
        except ValueError as e:
            print(e)
            if self.message_client is not None:
                self.message_client.send_message(self.failed, final=True)
            return self.failed, base64.b64encode(pickle.dumps(self.agent_executor.memory)).decode('utf-8')
