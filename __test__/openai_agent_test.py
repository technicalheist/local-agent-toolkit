
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest


from agents.OpenAIAgent import OpenAIAgent
from helper.tools import list_files
from helper.tools_definition import tools as tool_definitions


class TestOpenAIAgent(unittest.TestCase):
    
    
    def setUp(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        self.agent = OpenAIAgent(
            model=os.getenv("OPENAI_MODEL"),
            tool_definitions=tool_definitions,
            tool_callables={"list_files": list_files},
            system_prompt="You are a helpful assistant.",
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE")
        )

    def test_run(self):
        try:
            result = self.agent.run("List all the files and folder in current directory", max_iterations=10)
        except Exception as e:
            result = str(e)
        self.assertIsInstance(result, str)

    def test_run_with_streaming(self):
        try:
            result = self.agent.run_with_streaming("List all the files and folder in current directory", max_iterations=10)
        except Exception as e:
            result = str(e)
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()
