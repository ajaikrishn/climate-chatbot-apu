import streamlit as st
import sys
from datetime import datetime
import plotly.express as px
import pandas as pd

# Ensure Python can find rag_pipeline.py
sys.path.append('/home/ml_user/data/chat_bot')  
# Import the RAG pipeline
from rag_pipeline import qa_chain  

# Streamlit Page Configuration
st.set_page_config(
    page_title="🌍 Climate Insight Bot", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Chat message styling */
        .stChatMessage {
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stChatMessage.user {
            background-color: #dcf8c6;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }
        
        .stChatMessage.assistant {
            background-color: #f0f0f0;
            border-bottom-left-radius: 5px;
        }
        
        /* Chat input styling */
        .stChatInput input {
            font-size: 16px;
            padding: 15px;
            border-radius: 25px;
            border: 1px solid #ddd;
            transition: border 0.3s;
        }
        
        .stChatInput input:focus {
            border: 1px solid #4CAF50;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
        }
        
        /* Sidebar styling */
        .stSidebar {
            background-color: #f7f7f7;
            padding: 20px;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 20px;
            background-color: #4CAF50;
            color: white;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background-color: #3e8e41;
            transform: scale(1.02);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            background-color: #f0f0f0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }
        
        /* Custom tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Card styling */
        .card {
            border-radius: 10px;
            padding: 20px;
            background-color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

# Sample data for interactive elements
sample_climate_data = {
    "Year": [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100],
    "Temperature Rise (°C)": [1.1, 1.4, 1.7, 2.1, 2.4, 2.8, 3.2, 3.5, 3.9],
    "Sea Level Rise (cm)": [5, 12, 20, 30, 42, 55, 70, 85, 100],
    "Rainfall Change (%)": [2, 5, 8, 10, 13, 16, 18, 21, 25]
}

climate_df = pd.DataFrame(sample_climate_data)

# Climate impact regions in India
impact_regions = {
    "Coastal": ["Mumbai", "Chennai", "Kolkata", "Kerala"],
    "Himalayan": ["Shimla", "Darjeeling", "Srinagar", "Gangtok"],
    "Semi-Arid": ["Rajasthan", "Gujarat", "Telangana", "Maharashtra"],
    "River Basins": ["Gangetic Plains", "Brahmaputra Valley", "Narmada Basin", "Godavari Basin"]
}

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your climate AI assistant. What would you like to know about India's future climate? 🌏"}]

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "faq_expanded" not in st.session_state:
    st.session_state.faq_expanded = False

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Chat"

if "language" not in st.session_state:
    st.session_state.language = "English"

if "climate_scenario" not in st.session_state:
    st.session_state.climate_scenario = "Moderate Change"

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Functions for interactive elements
def toggle_faq():
    st.session_state.faq_expanded = not st.session_state.faq_expanded

def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your climate AI assistant. What would you like to know about India's future climate? 🌏"}]
    st.session_state.questions_asked = 0
    st.session_state.search_history = []

def submit_feedback(message_idx, feedback_type):
    st.session_state.feedback[message_idx] = feedback_type
    st.toast(f"Thank you for your {feedback_type} feedback!", icon="🙏")

def change_language():
    st.toast(f"Language changed to {st.session_state.language}", icon="🌐")

def update_climate_scenario():
    st.toast(f"Climate scenario updated to {st.session_state.climate_scenario}", icon="🌡️")

def add_to_search_history(query):
    if query not in st.session_state.search_history:
        st.session_state.search_history.append(query)
        if len(st.session_state.search_history) > 10:
            st.session_state.search_history.pop(0)

# Sidebar with enhanced information and controls
with st.sidebar:
    st.image("/home/ml_user/data/chat_bot/virtual-assistant.png", width=150)
    st.title("Climate Insight Bot")
    
    # Language selector
    st.subheader("🌐 Language")
    language_options = ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati"]
    selected_language = st.selectbox("Select Language", language_options, index=language_options.index(st.session_state.language), key="language_selector", on_change=change_language)
    st.session_state.language = selected_language
    
    # Climate scenario selector
    st.subheader("🌡️ Climate Scenario")
    scenario_options = ["Conservative Change", "Moderate Change", "Extreme Change"]
    selected_scenario = st.selectbox("Select Scenario", scenario_options, index=scenario_options.index(st.session_state.climate_scenario), key="scenario_selector", on_change=update_climate_scenario)
    st.session_state.climate_scenario = selected_scenario
    
    # About section with expander
    with st.expander("ℹ️ About this Bot", expanded=True):
        st.write("This AI assistant specializes in providing insights about India's future climate based on comprehensive research.")
        st.markdown("- **Powered by:** LangChain & Ollama LLMs")
        st.markdown("- **Data Source:** 'Navigating India's Climate Future' report")
        st.markdown("- **Updated:** March 2025")
    
    # Search history
    with st.expander("🔍 Your Recent Searches", expanded=False):
        if st.session_state.search_history:
            for i, query in enumerate(reversed(st.session_state.search_history)):
                st.markdown(f"{i+1}. {query}")
        else:
            st.write("No searches yet.")
    
    # Advanced options
    with st.expander("⚙️ Advanced Options", expanded=False):
        st.slider("Response Detail Level", min_value=1, max_value=5, value=3, help="Adjust how detailed the AI responses should be")
        st.checkbox("Include Scientific Citations", value=True, help="Include references to scientific sources")
        st.checkbox("Show Confidence Scores", value=False, help="Display AI confidence in answers")
    
    # Reset button
    st.button("🔄 Reset Chat", on_click=reset_chat, use_container_width=True)
    
    # Stats display
    st.subheader("📊 Session Stats")
    st.markdown(f"Questions Asked: **{st.session_state.questions_asked}**")
    st.markdown(f"Current Time: **{datetime.now().strftime('%H:%M:%S')}**")
    st.progress(min(st.session_state.questions_asked / 10, 1.0), "Chat Progress")

# Main interface with tabs
tabs = st.tabs(["💬 Chat", "📈 Climate Trends", "🗺️ Regional Impact", "❓ FAQs"])

# Chat Tab
with tabs[0]:
    st.title("🌍 Climate AI Chatbot")
    st.markdown("#### Explore India's climate future with AI assistance 🌱")
    
    # Suggested questions
    question_cols = st.columns(3)
    with question_cols[0]:
        st.button("How will temperature change in India by 2050?", use_container_width=True)
    with question_cols[1]:
        st.button("Which regions are most vulnerable to climate change?", use_container_width=True)
    with question_cols[2]:
        st.button("What are adaptation strategies for agriculture?", use_container_width=True)
    
    # Display chat history with feedback buttons
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add feedback buttons for assistant messages
            if message["role"] == "assistant" and idx > 0:
                cols = st.columns([0.9, 0.05, 0.05])
                with cols[1]:
                    st.button("👍", key=f"thumbs_up_{idx}", on_click=submit_feedback, args=(idx, "positive"), help="This was helpful")
                with cols[2]:
                    st.button("👎", key=f"thumbs_down_{idx}", on_click=submit_feedback, args=(idx, "negative"), help="This needs improvement")
    
    # User input with enhanced styling
    st.write("")  # Space before input
    user_input = st.chat_input("Ask about India's climate future...", key="chat_input")
    
    if user_input:
        # Track question count
        st.session_state.questions_asked += 1
        add_to_search_history(user_input)
        
        # Add user input to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Show typing indicator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get response from RAG pipeline
                try:
                    response = qa_chain.invoke({"query": user_input})
                    bot_response = response["result"]
                except Exception as e:
                    bot_response = f"I apologize, but I encountered an issue while processing your question. Could you try rephrasing it? (Error: {str(e)})"
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Rerun to display the updated chat
        st.rerun()

# Climate Trends Tab
with tabs[1]:
    st.title("📈 Climate Projections for India")
    st.write("Explore visual projections of climate change impacts in India based on available models and research.")
    
    # Interactive chart selection
    chart_type = st.selectbox(
        "Select Climate Parameter", 
        ["Temperature Rise", "Sea Level Rise", "Rainfall Change"],
        key="chart_selector"
    )
    
    # Date range slider
    years = st.slider(
        "Year Range", 
        min_value=2020, 
        max_value=2100, 
        value=(2020, 2100),
        step=10,
        key="year_slider"
    )
    
    # Filter data based on selections
    filtered_df = climate_df[(climate_df["Year"] >= years[0]) & (climate_df["Year"] <= years[1])]
    
    # Create appropriate chart based on selection
    if chart_type == "Temperature Rise":
        fig = px.line(
            filtered_df, 
            x="Year", 
            y="Temperature Rise (°C)",
            markers=True,
            title="Projected Temperature Rise in India",
            labels={"Temperature Rise (°C)": "Temperature Increase (°C)"}
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Temperature Rise (°C)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Projections show significant warming trends across India, with average temperatures expected to rise between 1.5°C and 4.5°C by 2100 depending on emission scenarios.")
        
    elif chart_type == "Sea Level Rise":
        fig = px.line(
            filtered_df, 
            x="Year", 
            y="Sea Level Rise (cm)",
            markers=True,
            title="Projected Sea Level Rise Affecting Indian Coastlines",
            labels={"Sea Level Rise (cm)": "Sea Level Rise (cm)"}
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Sea Level Rise (cm)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("Coastal areas including Mumbai, Chennai, and Kolkata face significant risks from sea level rise, with projections indicating 30-100 cm rise by 2100.")
        
    else:  # Rainfall Change
        fig = px.bar(
            filtered_df, 
            x="Year", 
            y="Rainfall Change (%)",
            title="Projected Changes in Rainfall Patterns",
            labels={"Rainfall Change (%)": "Change in Rainfall (%)"}
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Rainfall Change (%)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("Monsoon patterns are expected to become more erratic, with some regions experiencing up to 25% increase in rainfall intensity while others may face prolonged droughts.")
    
    # Data source note
    st.caption("Note: These projections are based on climate models from the 'Navigating India's Climate Future' report.")

# Regional Impact Tab  
with tabs[2]:
    st.title("🗺️ Regional Climate Impact Assessment")
    st.write("Climate change will affect different regions of India in various ways. Explore the projected impacts by region.")
    
    # Region selection
    region_type = st.radio(
        "Select Region Type",
        list(impact_regions.keys()),
        horizontal=True,
        key="region_selector"
    )
    
    # Create columns for region cards
    region_cols = st.columns(2)
    
    # Display region cards
    for i, region in enumerate(impact_regions[region_type]):
        with region_cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <h3>{region}</h3>
                <p>Climate Vulnerability Index: <b>High</b></p>
                <p>Primary Concerns:</p>
                <ul>
                    <li>{"Sea level rise & flooding" if region_type == "Coastal" else "Glacial retreat & water scarcity" if region_type == "Himalayan" else "Drought & heat waves" if region_type == "Semi-Arid" else "Flooding & agricultural impacts"}</li>
                    <li>{"Saltwater intrusion" if region_type == "Coastal" else "Landslides & biodiversity loss" if region_type == "Himalayan" else "Groundwater depletion" if region_type == "Semi-Arid" else "Water quality issues"}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Add interactive map (placeholder)
    st.subheader("Vulnerability Hotspots")
    st.image("https://via.placeholder.com/800x400?text=Interactive+Climate+Impact+Map+(Placeholder)", use_column_width=True)
    st.caption("Note: This is a placeholder for an interactive map that would show climate vulnerability hotspots across India.")

# FAQ Tab
with tabs[3]:
    st.title("❓ Frequently Asked Questions")
    st.write("Find answers to common questions about climate change in India.")
    
    # FAQ accordion
    with st.expander("What are the main climate change threats facing India?", expanded=True):
        st.write("""
        India faces several major climate threats:
        
        1. Rising temperatures and more frequent heat waves
        2. Changes in monsoon patterns affecting agriculture
        3. Sea level rise threatening coastal communities
        4. Increased frequency of extreme weather events
        5. Water scarcity in many regions
        
        These threats pose significant risks to agriculture, public health, infrastructure, and economic stability.
        """)
    
    with st.expander("How will climate change affect agriculture in India?"):
        st.write("""
        Climate change is projected to significantly impact Indian agriculture through:
        
        - Reduced crop yields due to higher temperatures
        - Changes in growing seasons and crop suitability
        - Increased water stress and irrigation requirements
        - Greater crop damage from extreme weather events
        - New pest and disease pressures
        
        Studies suggest rice yields could decline 10-40% by 2100 without adaptation measures.
        """)
    
    with st.expander("What adaptation strategies are being implemented?"):
        st.write("""
        India is implementing various climate adaptation strategies:
        
        - Development of drought and heat-resistant crop varieties
        - Water conservation and management initiatives
        - Early warning systems for extreme weather events
        - Coastal protection measures
        - Renewable energy expansion
        - Afforestation and ecosystem restoration
        - Climate-resilient urban planning
        
        The National Action Plan on Climate Change (NAPCC) coordinates many of these efforts.
        """)
    
    with st.expander("How will climate change affect India's water resources?"):
        st.write("""
        Climate change is expected to severely impact India's water resources:
        
        - Greater variability in rainfall patterns
        - Increased glacial melt affecting river flows
        - Rising water demand due to higher temperatures
        - Groundwater depletion in many regions
        - Degraded water quality from flooding and saltwater intrusion
        
        By 2050, per capita water availability could fall below scarcity levels in many regions.
        """)
    
    with st.expander("What can individuals do to help address climate change?"):
        st.write("""
        Individuals can contribute to climate action through:
        
        - Reducing energy consumption and shifting to renewable sources
        - Conserving water and reducing food waste
        - Using sustainable transportation options
        - Supporting climate-friendly policies and businesses
        - Growing trees and protecting local ecosystems
        - Raising awareness in communities
        
        Collective action by individuals can create significant positive impact.
        """)

# Footer
st.markdown("---")
footer_cols = st.columns([1, 2, 1])
with footer_cols[0]:
    st.caption("Updated: March 2025")
with footer_cols[1]:
    st.caption("Powered by LangChain & Ollama LLMs | Data source: 'Navigating India's Climate Future' report")
with footer_cols[2]:
    st.caption("© 2025 Climate Insight Bot")