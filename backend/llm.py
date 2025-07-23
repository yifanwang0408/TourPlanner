from google.cloud import secretmanager
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory



class LLM:

    def __init__(self, api_key_id, project_id):
        self._api_key_id = api_key_id
        self._project_id = project_id

    def get_api_key(self):
        """fetch the openai api key from secret manager"""
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{self._project_id}/secrets/{self._api_key_id}/versions/latest"
        response = client.access_secret_version(name=name)
        self._api_key = response.payload.data.decode("UTF-8")

    def setup(self, model_name="gpt-4.1-mini", **params):
        """setup the llm api with given params"""
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=self._api_key, **params)

    def chat(self, message):
        return self.llm(message)
    
    






        



    

        