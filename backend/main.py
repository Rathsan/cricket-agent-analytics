from fastapi import FastAPI
from autogen import Agent, UserProxyAgent, AssistantAgent,ConversableAgent
import os
import sys
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Annotated
from direct_search import direct_web_search
from coding_gen_test import CodeGen

# Simple Unicode fix without aggressive redirection
os.environ['PYTHONIOENCODING'] = 'utf-8'

load_dotenv()

app = FastAPI()

@app.get("/get_stats")
def get_stats(player_name: str):

    # Get cricket statistics and automatically compact for better parsing
    search = direct_web_search(player_name)  # Fixed: use actual parameter
    full_results = search.search_stats_tool()  # Get full search results
    summary = search.compact_search_results(full_results)  # Use compact version

    print("=== COMPACTED SEARCH RESULTS ===")
    print(f"Original size: ~{len(str(full_results))} characters")
    print(f"Compact size: ~{len(str(summary))} characters") 
    print(f"Compression ratio: {len(str(summary))/len(str(full_results))*100:.1f}%")
    print(f"Compact data: {summary}")

    # Execute code generation
    print("[INFO] Starting chart generation...")
    try:
        code_gen = CodeGen(summary)
        code_gen.codeExecutor()
        print("[SUCCESS] Chart generation completed!")
    except UnicodeEncodeError as e:
        print(f"[WARNING] Unicode error caught but continuing: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Chart generation failed: {str(e)}")
        # Continue execution even if chart generation fails

    # Check if chart was generated (just check file existence)
    chart_paths = [
        "./docker_tmp/cricket_stats_chart.png",
        "docker_tmp/cricket_stats_chart.png", 
        "../backend/docker_tmp/cricket_stats_chart.png"
    ]
    
    chart_found = False
    chart_path = None
    
    for path in chart_paths:
        if os.path.exists(path):
            chart_found = True
            chart_path = path
            print(f"[CHART] Chart found at: {chart_path}")
            break
    
    if not chart_found:
        print("[WARNING] Chart not found in any expected location")
    
    # Return simple completion signal (no chart data)
    return {
        "execution_completed": True,
        "player_name": player_name,
        "chart_generated": chart_found,
        "chart_path": chart_path,
        "statistics": summary,
        "message": f"Chart generation completed for {player_name}" if chart_found else f"Chart generation failed for {player_name}"
    }

    






