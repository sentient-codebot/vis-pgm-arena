import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import argparse

def visualize_power_grid(json_file_path, layout='spring', output_file=None):
    """
    Visualize a power grid network from a JSON file
    
    Args:
        json_file_path (str): Path to the JSON file containing power grid data
        layout (str): The layout algorithm to use ('spring', 'spectral', or 'kamada_kawai')
        output_file (str): Name of the output file (if None, a default name is used)
    
    Returns:
        None: Saves the visualization to a PNG file
    """
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract the relevant parts of the data
    nodes = data['data']['node']
    lines = data['data']['line']
    transformers = data['data']['transformer']
    
    # Create a graph
    G = nx.Graph()
    
    # Add nodes to the graph
    for node in nodes:
        G.add_node(node['id'], u_rated=node['u_rated'])
    
    # Add regular edges (lines) to the graph
    for line in lines:
        G.add_edge(line['from_node'], line['to_node'], 
                   r1=line['r1'], x1=line['x1'],
                   type='line')
    
    # Add transformer edges to the graph
    for transformer in transformers:
        G.add_edge(transformer['from_node'], transformer['to_node'],
                   u1=transformer['u1'], u2=transformer['u2'],
                   type='transformer')
    
    # Determine the layout based on user choice
    if layout == 'spring':
        pos = nx.spring_layout(G, k=0.3, iterations=100, seed=42)
        title_suffix = "(Spring Layout)"
    elif layout == 'spectral':
        pos = nx.spectral_layout(G)
        title_suffix = "(Spectral Layout)"
    elif layout == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
        title_suffix = "(Kamada-Kawai Layout)"
    else:
        print(f"Unknown layout '{layout}'. Using spring layout.")
        pos = nx.spring_layout(G, k=0.3, iterations=100, seed=42)
        title_suffix = "(Spring Layout)"
        layout = 'spring'
    
    # Set figure size based on the number of nodes
    plt.figure(figsize=(20, 16))
    
    # Get voltage levels for colormap
    voltage_levels = np.array([G.nodes[n]['u_rated'] for n in G.nodes()])
    norm = plt.Normalize(voltage_levels.min(), voltage_levels.max())
    cmap = cm.viridis
    
    # Draw nodes with color based on voltage level - significantly larger
    node_colors = cmap(norm(voltage_levels))
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color=node_colors, 
                           alpha=0.9, edgecolors='dimgray', linewidths=1.5)
    
    # Draw node labels (node indices) - increased font size to match larger nodes
    node_labels = {node: str(node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=11, font_weight='bold', font_color='black', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))
    
    # Draw regular edges (lines)
    line_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'line']
    nx.draw_networkx_edges(G, pos, edgelist=line_edges, edge_color='slategray', 
                           width=1.0, alpha=0.7)
    
    # Draw transformer edges with a different color and style
    transformer_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'transformer']
    nx.draw_networkx_edges(G, pos, edgelist=transformer_edges, edge_color='firebrick', 
                           width=2.5, style='dashed', alpha=1.0)
    
    # Highlight the transformer nodes
    transformer_nodes = set()
    for edge in transformer_edges:
        transformer_nodes.add(edge[0])
        transformer_nodes.add(edge[1])
    
    nx.draw_networkx_nodes(G, pos, nodelist=list(transformer_nodes), 
                           node_size=800, node_color='orange', 
                           edgecolors='firebrick', linewidths=2.5)
    
    # Colorbar removed as requested
    
    # Add legend with more space for node indices to be visible
    plt.plot([], [], color='slategray', linewidth=1.0, label='Power Line')
    plt.plot([], [], color='firebrick', linewidth=2.5, linestyle='dashed', label='Transformer')
    plt.plot([], [], marker='o', markersize=10, markerfacecolor='orange', 
             markeredgecolor='firebrick', linestyle='', label='Transformer Node')
    
    legend = plt.legend(title='Network Elements', loc='lower right', fontsize=12)
    plt.setp(legend.get_title(), fontsize=14)
    
    # Add title and styling
    plt.title(f'Power Grid Network Visualization {title_suffix}', fontsize=20, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # Determine output filename
    if output_file is None:
        output_file = f'power_grid_{layout}.png'
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Power grid visualization saved as '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize a power grid network from a JSON file')
    parser.add_argument('json_file', help='Path to the JSON file containing power grid data')
    parser.add_argument('--layout', choices=['spring', 'spectral', 'kamada_kawai'], 
                        default='kamada_kawai', help='Layout algorithm to use')
    parser.add_argument('--output', help='Output file name (default is based on the layout)')
    
    args = parser.parse_args()
    
    visualize_power_grid(args.json_file, args.layout, args.output)