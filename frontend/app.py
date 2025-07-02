import streamlit as st
import requests
import os
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="🏏 Cricket Stats Assistant",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🏏 Cricket Stats Assistant")
st.markdown("### Get comprehensive cricket statistics and visualizations for any player!")

# Main interface
col1, col2 = st.columns([3, 1])

with col1:
    player_name = st.text_input(
        "Enter Cricket Player Name:",
        placeholder="e.g., Virat Kohli, Rohit Sharma, Kane Williamson...",
        help="Enter the full name or just first/last name"
    )

with col2:
    st.write("")  # Space for alignment
    get_stats = st.button("🔍 Get Stats", type="primary", use_container_width=True)

if get_stats and player_name:
    with st.spinner(f"🔍 Generating cricket statistics and chart for {player_name}..."):
        try:
            # Make API request to backend
            response = requests.get(f"http://localhost:8000/get_stats?player_name={player_name}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if execution completed
                if data.get("execution_completed"):
                    st.success(f"✅ {data.get('message', 'Process completed!')}")
                    
                    # Display statistics text
                    if data.get("statistics") and data["statistics"].get("results"):
                        stats_content = data["statistics"]["results"][0].get("content", "")
                        if stats_content:
                            st.markdown("### 📊 Cricket Statistics")
                            st.text(stats_content)
                    
                    # Check if chart was generated and read it directly from file
                    if data.get("chart_generated"):
                        st.markdown("### 📈 Statistical Visualization")
                        
                        # Define possible chart file locations (relative to frontend)
                        chart_locations = [
                            "../backend/docker_tmp/cricket_stats_chart.png",
                            "../../backend/docker_tmp/cricket_stats_chart.png",
                            "../cric_stats_llm/backend/docker_tmp/cricket_stats_chart.png",
                            "cric_stats_llm/backend/docker_tmp/cricket_stats_chart.png",
                            # Absolute path based on working directory
                            os.path.join(os.getcwd(), "cric_stats_llm", "backend", "docker_tmp", "cricket_stats_chart.png"),
                            os.path.join(os.getcwd(), "backend", "docker_tmp", "cricket_stats_chart.png")
                        ]
                        
                        # Try to find and read the chart file
                        chart_found = False
                        for chart_path in chart_locations:
                            try:
                                if os.path.exists(chart_path):
                                    # Read the chart file directly
                                    with open(chart_path, "rb") as chart_file:
                                        chart_bytes = chart_file.read()
                                    
                                    # Display the chart
                                    st.image(
                                        chart_bytes, 
                                        caption=f"Cricket Statistics Chart for {player_name}",
                                        use_column_width=True
                                    )
                                    
                                    # Add download button
                                    st.download_button(
                                        label="💾 Download Chart",
                                        data=chart_bytes,
                                        file_name=f"{player_name.replace(' ', '_')}_cricket_stats.png",
                                        mime="image/png",
                                        type="secondary",
                                        help="Download the generated cricket statistics chart"
                                    )
                                    
                                    st.success(f"📊 Chart successfully loaded from: {chart_path}")
                                    chart_found = True
                                    break
                                    
                            except Exception as e:
                                st.error(f"Error reading chart from {chart_path}: {str(e)}")
                                continue
                        
                        if not chart_found:
                            st.warning("⚠️ Chart was generated but could not be found at expected locations.")
                            st.info("💡 **Possible locations searched:**")
                            for location in chart_locations:
                                exists = "✅" if os.path.exists(location) else "❌"
                                st.text(f"{exists} {location}")
                            
                    elif data.get("execution_completed") and not data.get("chart_generated"):
                        st.warning("⚠️ Chart generation completed but no chart file was created. The statistics are available above.")
                    
                    # Show raw response in expandable section for debugging
                    with st.expander("🔍 Raw API Response", expanded=False):
                        st.json(data)
                
                else:
                    st.error("❌ Execution did not complete successfully.")
                    st.json(data)
            
            else:
                st.error(f"❌ Server error (Status: {response.status_code})")
                st.text(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Please ensure it's running on http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Chart generation may take some time.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

elif get_stats and not player_name:
    st.warning("⚠️ Please enter a player name first.")

# Instructions
if not get_stats:
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Enter Player Name**: Type any cricket player's name
    2. **Wait for Processing**: The system will search for statistics and generate charts  
    3. **View Results**: See both text statistics and visual charts
    4. **Download**: Save charts as PNG files
    """)
    
    st.markdown("### 🎯 Try These Players:")
    st.markdown("`MS Dhoni` • `Virat Kohli` • `Rohit Sharma` • `Kane Williamson`")
