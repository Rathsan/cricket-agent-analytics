from autogen import AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.coding import DockerCommandLineCodeExecutor
import os
import shutil
from dotenv import load_dotenv
import json

# Simple Unicode fix
os.environ['PYTHONIOENCODING'] = 'utf-8'

shared_dir = "./docker_tmp"
# Remove existing directory and recreate it fresh
if os.path.exists(shared_dir):
    shutil.rmtree(shared_dir)
os.makedirs(shared_dir)

load_dotenv()

llm_config = {"model": "gpt-4o",
              "api_key": os.getenv("OPENAI_API_KEY")}

llm_config_dict = {"fast_reasioning" : {
    "model": "mistralai/mistral-7b-instruct-v0.3",
    "base_url": "http://localhost:1234/v1",
    "api_key": "lm-studio"  # LM Studio typically accepts any string
            },
    "code_generation":{"model":"deepseek-coder-6.7b-instruct",
                       "base_url": "http://localhost:1234/v1",
                       "api_key": "lm-studio"},
    "openai_code_config":{"model":"gpt-4o",
                          "api_key": os.getenv("OPENAI_API_KEY")}
        }

class CodeGen():
    def __init__(self,summary):
        self.summary = summary
        
        

    def codeExecutor(self):
        # Docker executor configuration with proper file handling
        # Using full python:3.10 image (not slim) for better package support
        docker_executor = DockerCommandLineCodeExecutor(
            image="python:3.10",
            timeout=600,  # Increased timeout for package installation
            work_dir=shared_dir  # Use local shared directory directly
        )

        # User proxy agent with code execution capabilities
        user_proxy = UserProxyAgent(
            name='user',
            is_termination_msg=lambda x: x.get('content') is not None and 'TERMINATE' in x['content'],
            human_input_mode='NEVER',
            system_message="You are a helpful user who runs LLM-generated code using Docker.",
            code_execution_config={"executor": docker_executor}
        )

        # Assistant agent for code generation
        assistant = AssistantAgent(
            name='code_writer',
            llm_config=llm_config_dict['openai_code_config'],
            system_message="""You are a Python coding assistant. Write code to analyze cricket statistics and create charts.

REQUIRED OUTPUT FORMAT:
1. First: bash block to install matplotlib
2. Second: python block with complete solution

IMPORTANT RULES:
- Use matplotlib.use('Agg') for headless environment
- Parse the provided JSON data to extract cricket statistics
- Create 4 charts in 2x2 grid: matches, runs, averages, centuries
- Add value labels on top of each bar
- Save chart as absolute path: os.path.abspath('cricket_stats_chart.png')

PARSING STRATEGY:
- Look for "Career statistics:" in the content
- Extract numbers for Test, ODI, T20I formats
- Remove commas from numbers before parsing
- Handle parsing errors gracefully

CHART REQUIREMENTS:
- 2x2 subplot layout
- Bar charts for each metric
- Text labels showing values on bars
- Proper titles and formatting

Write clean, working code that solves this problem. Please avoid using emojis or special Unicode characters in your responses."""
        )

        # Let assistant handle parsing and visualization
        try:
            user_proxy.initiate_chat(
                recipient=assistant,
                message=f"""
        I have cricket statistics data in JSON format that needs to be parsed and visualized.

        Data:
        {json.dumps(self.summary, indent=2)}

        Your task:
        1. Parse this JSON data and extract cricket statistics (matches, runs, averages, centuries)
        2. Handle the text parsing from the 'content' fields in the results array
        3. Create a professional bar chart visualization showing the stats across Test, ODI, and T20I formats  
        4. Save the chart as 'cricket_stats_chart.png' in the current directory

        Requirements:
        - Install matplotlib with: pip install matplotlib
        - Set matplotlib backend for headless Docker: import matplotlib; matplotlib.use('Agg')
        - Extract numeric data from the text content (handle commas in numbers like "14,181")
        - Create a multi-panel chart (2x2 grid) showing: matches, runs, averages, centuries
        - Add proper labels, titles, and formatting
        - **ADD VALUE LABELS: Place exact numbers on top of each bar using ax.text() method**
        - Save as PNG file with absolute path to ensure Docker file persistence
        - Use print statements to show progress

        The PNG file should be saved and accessible from the host system after execution.

        TERMINATE when complete.
        """,
                max_turns=2
            )
        except UnicodeEncodeError as e:
            print(f"[WARNING] Unicode encoding error during chat: {e}")
        except Exception as e:
            print(f"[ERROR] Chat execution error: {e}")
            
        # Always check if the chart was generated
        chart_file = os.path.join(shared_dir, "cricket_stats_chart.png")
        if os.path.exists(chart_file):
            print(f"[SUCCESS] Chart found after execution: {chart_file}")
        else:
            print(f"[WARNING] Chart not found at expected location: {chart_file}")
            # List what files were actually created
            if os.path.exists(shared_dir):
                files = os.listdir(shared_dir)
                print(f"[DEBUG] Files in {shared_dir}: {files}")



