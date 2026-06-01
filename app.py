# [file-tag: code-generated-file-3-1780302620063852079]
import streamlit as st
import pandas as pd
import networkx as nx
import json
import streamlit.components.v1 as components

# Set page layout to wide
st.set_page_config(
    page_title="Corporate Tax Network Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Theme Colors
PRIMARY_COLOR = "#1E3A8A"
SECONDARY_COLOR = "#0D9488"

st.markdown(f"""
    <style>
    .main-header {{
        color: {PRIMARY_COLOR};
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
    }}
    .sub-header {{
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }}
    </style>
""", unsafe_allow_html=True)

# English Narratives & Explanations
st.markdown('<h1 class="main-header">📊 Corporate Ownership & Tax Network Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">An advanced graph-based framework to identify Ultimate Beneficial Owners (UBOs), key corporate conglomerates, and critical pathways using NetworkX and interactive D3.js simulations.</p>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("📁 Data Source Configuration")
nodes_file = st.sidebar.file_uploader("Upload nodes_masked.csv", type=["csv"])
edges_file = st.sidebar.file_uploader("Upload edges_masked_part1_a.csv", type=["csv"])

@st.cache_data
def load_default_data():
    try:
        return pd.read_csv("nodes_masked.csv"), pd.read_csv("edges_masked_part1_a.csv")
    except:
        return None, None

if nodes_file and edges_file:
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
else:
    nodes_df, edges_df = load_default_data()
    if nodes_df is None:
        st.sidebar.warning("Please upload both CSV files to proceed.")
        st.stop()

# Build NetworkX Graph
@st.cache_resource
def build_network(edges, nodes):
    G = nx.DiGraph()
    node_attr = nodes.set_index('id').to_dict('index')
    for node_id, attrs in node_attr.items():
        G.add_node(node_id, name=attrs['nama'], type=attrs['jenis_node'])
    for _, row in edges.iterrows():
        G.add_edge(row['sumber'], row['target'], weight=float(row['nilai']), percentage=float(row['persentase']))
    return G

G = build_network(edges_df, nodes_df)

# Calculate Centrality Metrics
@st.cache_data
def calculate_metrics(_graph):
    return nx.out_degree_centrality(_graph), nx.in_degree_centrality(_graph), nx.betweenness_centrality(_graph)

out_deg, in_deg, betweenness = calculate_metrics(G)

summary_data = [{
    "Taxpayer ID": n, "Taxpayer Name": G.nodes[n].get('name', 'Unknown'), "Entity Type": G.nodes[n].get('type', 'Unknown'),
    "Out-Degree (Holding Score)": out_deg.get(n, 0), "In-Degree (Capital Influx)": in_deg.get(n, 0), "Betweenness (Bridge Score)": betweenness.get(n, 0)
} for n in G.nodes()]
df_metrics = pd.DataFrame(summary_data)

# Theoretical Framework Expansion
with st.expander("📖 Theoretical Framework & Methodology (English)", expanded=True):
    st.markdown("""
    ### 🔬 Network Centrality in Corporate Tax Risk Management
    Corporate groups often utilize intricate, multi-layered structures spanning multiple entities (subsidiaries, shell companies, and high-net-worth individuals) to optimize or aggressively plan taxes. This module isolates **Key Players** using network topographies:
    
    1. **Out-Degree Centrality (Holding / Investor Power)**: 
       - *Definition*: Measures how many outward connections a node originates.
       - *Tax Context*: High out-degree entities signify ultimate holding companies, conglomerates, or wealthy family patriarchs/matriarchs owning numerous operational businesses.
    2. **In-Degree Centrality (Capital Accumulators)**:
       - *Definition*: Measures incoming capital and equity injection paths.
       - *Tax Context*: High in-degree units represent deeply capitalized operating subsidiaries receiving extensive external financing, potentially exposed to transfer pricing or high dividend distributions.
    3. **Betweenness Centrality (Strategic Conduits / Bridges)**:
       - *Definition*: Measures how frequently a node falls on the shortest path between all other entity pairs.
       - *Tax Context*: Indicates strategic 'pass-through' channels, intermediate shell companies, or regional management nodes that bridge disparate commercial networks—frequently scrutinized for Base Erosion and Profit Shifting (BEPS) risks.
    """)

tab1, tab2 = st.tabs(["🎮 Interactive D3.js Network Simulation", "📊 Centrality Rankings & Leaderboard"])

with tab2:
    st.markdown("### 🏆 Enterprise Centrality Leaderboards")
    metric_choice = st.selectbox("Select Centrality Metric to Rank Entities:", ["Out-Degree (Holding Score)", "In-Degree (Capital Influx)", "Betweenness (Bridge Score)"])
    top_n = st.slider("Show Top N Records:", 5, 50, 15)
    st.dataframe(df_metrics.sort_values(by=metric_choice, ascending=False).head(top_n), use_container_width=True)

with tab1:
    st.markdown("### 🕸️ Interactive Force-Directed D3.js Sub-Network Visualization")
    focus_metric = st.selectbox("Node Scaling Reference Metric:", ["Out-Degree (Holding Score)", "In-Degree (Capital Influx)", "Betweenness (Bridge Score)"])
    entity_limit = st.slider("Filter to top connected network components:", 50, 300, 120)
    
    # Process graph to json for D3
    top_node_ids = df_metrics.sort_values(by=focus_metric, ascending=False).head(entity_limit)["Taxpayer ID"].tolist()
    subG = G.subgraph(top_node_ids)
    
    color_map = {"Badan": "#1E3A8A", "OP": "#0D9488", "LN": "#D97706", "Non NPWP": "#EF4444"}
    d3_nodes = [{
        "id": str(n), "name": str(subG.nodes[n].get('name', 'Unknown')), "type": str(subG.nodes[n].get('type', 'Unknown')),
        "color": color_map.get(str(subG.nodes[n].get('type', 'Unknown')), "#64748B"),
        "size": max(6, min(6 + (df_metrics.loc[df_metrics["Taxpayer ID"] == n, focus_metric].values[0] * (800 if "Bridge" in focus_metric else 50)), 35))
    } for n in subG.nodes()]
    
    d3_links = [{"source": str(s), "target": str(t)} for s, t in subG.edges()]
    d3_json_str = json.dumps({"nodes": d3_nodes, "links": d3_links})

    d3_html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ font-family: sans-serif; margin: 0; background-color: #FAFAFA; }}
            .link {{ stroke: #94A3B8; stroke-opacity: 0.6; stroke-width: 1.5px; }}
            .node circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
            .node text {{ font-size: 10px; pointer-events: none; fill: #334155; }}
        </style>
    </head>
    <body>
        <svg id="network-viz" width="100%" height="600px"></svg>
        <script>
            const data = {d3_json_str};
            const svg = d3.select("#network-viz");
            const width = window.innerWidth || 800; const height = 600;
            const container = svg.append("g");
            
            svg.call(d3.zoom().on("zoom", (event) => container.attr("transform", event.transform)));
            
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(90))
                .force("charge", d3.forceManyBody().strength(-120))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = container.append("g").selectAll("line").data(data.links).join("line").attr("class", "link");
            const node = container.append("g").selectAll(".node").data(data.nodes).join("g").attr("class", "node")
                .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

            node.append("circle").attr("r", d => d.size).attr("fill", d => d.color);
            node.append("text").attr("dx", d => d.size + 4).attr("dy", ".35em").text(d => d.name);

            simulation.on("tick", () => {{
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});
            function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
            function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
            function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
        </script>
    </body>
    </html>
    """
    components.html(d3_html_content, height=620, scrolling=False)
