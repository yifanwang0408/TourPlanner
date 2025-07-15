from llm import LLM
import tools


if __name__ == "__main__":
    llm = LLM("open-api-key", "llm-tourplanner")
    llm.get_api_key()
    llm.setup()






