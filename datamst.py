import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random
import time
import json
import os

# Set page configuration
st.set_page_config(page_title="Optimal Irrigation Network", layout="wide")

# Sidebar for settings
st.sidebar.header("⚙️ Settings")
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

# Apply theme based on mode
page_bg = f'''
<style>
[data-testid="stAppViewContainer"] {{
    background-color: {'#1E1E1E' if dark_mode else '#F5F5F5'};
    color: {'white' if dark_mode else 'black'};
}}
[data-testid="stSidebar"] {{
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    padding: 15px;
}}
.stButton > button {{
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
    font-size: 16px;
    transition: 0.3s;
}}
.stButton > button:hover {{
    background-color: #45a049;
}}
</style>
'''
st.markdown(page_bg, unsafe_allow_html=True)

# Pipe selection with varieties
pipe_types = {
    "PVC": 75,
    "HDPE": 100,
    "Drip Irrigation": 85,
    "Steel": 150,
    "Concrete": 200
}

# JSON file path
json_file = "irrigation_data.json"

# Function to save data to JSON file
def save_to_json(data):
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=4)

# Function to read saved JSON data
def load_json_data():
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Function to generate a random graph
def generate_random_graph(num_nodes):
    edges = []
    for _ in range(num_nodes * 2):
        u, v = random.sample(range(num_nodes), 2)
        w = random.randint(1, 20)
        edges.append((u, v, w))
    return edges

# Function to compute MST using Kruskal's Algorithm
def kruskal_mst(num_nodes, edges, cost_per_meter):
    G = nx.Graph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    mst = list(nx.minimum_spanning_edges(G, algorithm='kruskal', data=True))
    total_length = sum(edge[2]['weight'] for edge in mst)
    total_cost = total_length * cost_per_meter
    return mst, total_cost

# Function to animate the MST visualization
def animate_graph(num_nodes, edges, mst_edges):
    G = nx.Graph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    pos = nx.spring_layout(G)
    fig = go.Figure()
    
    # Display nodes
    for node, (x, y) in pos.items():
        fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text', text=[str(node)],
                                 textposition='top center', marker=dict(size=15, color='lightgreen'), name='Nodes'))
    
    st.plotly_chart(fig, use_container_width=True)
    time.sleep(1)
    
    # Display edges
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color='gray', width=1), name='Edges'))
        st.plotly_chart(fig, use_container_width=True)
        time.sleep(0.5)
    
    # Highlight MST Edges
    for u, v, data in mst_edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color='red', width=3), name='MST Edges'))
    st.plotly_chart(fig, use_container_width=True)
    
    return fig

# Streamlit UI
st.markdown(f"""
    <h1 style='text-align: center; font-size: 40px; color: {"#FFFFFF" if dark_mode else "#2E8B57"};'>🌿 Optimal Irrigation Network Design</h1>
    <h3 style='text-align: center; color: {"#AAAAAA" if dark_mode else "#555"};'>Design the most cost-efficient irrigation pipeline network</h3>
""", unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Input Parameters")
    num_nodes = st.number_input("Enter Number of Crops (Nodes):", min_value=2, max_value=20, value=5, step=1)
    
    pipe_type = st.selectbox("Select Pipe Material:", list(pipe_types.keys()))
    cost_per_meter = pipe_types[pipe_type]
    st.write(f"Cost per meter: ₹{cost_per_meter}")
    
    generate = st.button("🎲 Generate Random Field")
    edges_input = st.text_area("Enter Edges (u v w), comma-separated:", "")
    compute = st.button("🔍 Compute MST")

# Generate Random Field
if generate:
    edges = generate_random_graph(num_nodes)
    edges_str = ", ".join([f"{u} {v} {w}" for u, v, w in edges])
    st.session_state['edges'] = edges_str
    st.success("✅ Random Irrigation Field Generated!")

# Load generated edges into the text area
if 'edges' in st.session_state:
    edges_input = st.session_state['edges']
st.text_area("Edges", edges_input, disabled=True)

# Compute MST and Save Data
if compute:
    try:
        edges = [tuple(map(int, edge.split())) for edge in edges_input.split(',')]
        mst, total_cost = kruskal_mst(num_nodes, edges, cost_per_meter)
        
        st.markdown(f"""
        <h2 style='text-align: center; color: green;'>✅ Minimum Irrigation Cost:</h2>
        <h2 style='text-align: center; font-size: 30px; color: blue;'>💰 ₹{total_cost}</h2>
        """, unsafe_allow_html=True)
        
        animate_graph(num_nodes, edges, [(u, v, d['weight']) for u, v, d in mst])
        
        # Save data to JSON file
        irrigation_data = {
            "num_nodes": num_nodes,
            "edges": edges_input,
            "pipe_type": pipe_type,
            "cost_per_meter": cost_per_meter,
            "total_cost": total_cost
        }
        save_to_json(irrigation_data)
        
        st.success("✅ Data Saved to JSON File!")
    except Exception as e:
        st.error("❌ Invalid input! Please check your values.")

# Section to View Saved Data
st.markdown("### 📜 Previously Computed Irrigation Networks")
saved_data = load_json_data()

if saved_data:
    for i, entry in enumerate(saved_data[::-1]):
        with st.expander(f"💾 Record {len(saved_data) - i} - {entry['num_nodes']} Nodes, {entry['pipe_type']} Pipe"):
            st.write(f"**Total Cost:** ₹{entry['total_cost']}")
            st.write(f"**Edges:** {entry['edges']}")
else:
    st.info("No saved irrigation network data found.")
