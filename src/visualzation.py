import networkx as nx
import matplotlib.pyplot as plt

def build_network_graph(vertiports, transport_times):
    """
    Build a NetworkX graph from your vertiports and transport time data.

    Args:
        vertiports (list): A list of vertiport objects; each vertiport should have a 'name' attribute.
        transport_times (dict): A dictionary keyed by tuples (src, dest) -> transport time.
                                For example: {('V1','V2'): 15, ('V2','V3'): 20, ...}
    Returns:
        G (networkx.Graph): A graph with nodes and edges for each vertiport/route.
        pos (dict): Positions for each node to draw consistently.
    """
    G = nx.Graph()

    # Add nodes (one node for each vertiport)
    for v in vertiports:
        G.add_node(v.name)

    # Add edges (one edge for each known transport route)
    # For illustration, treat 'transport_time' as an attribute
    for t in transport_times:
        src, dest, ttime = t.src, t.dest, t.time
        G.add_edge(src, dest, transport_time=ttime)

    # You can define a layout or simply rely on a default layout
    # For repeatable layout, one approach is random but with a fixed seed or use spring_layout/circular_layout/etc.
    # We'll do a spring_layout here for demonstration (which does not specify color, just positions):
    pos = nx.spring_layout(G, seed=42)
    return G, pos

def visualize_current_state(G, pos, vertiports, current_time):
    """
    Draw a snapshot of the network, showing how many aircraft/passengers
    are currently at each vertiport.

    Args:
        G (networkx.Graph): The network graph of vertiports.
        pos (dict): A dictionary of positions for each node.
        vertiports (list): List of vertiport objects, each with name, current_aircraft, current_passengers.
        current_time (float): The current simulation time (minutes, or any unit).
    """

    # Clear any previous figure
    plt.figure()
    
    # Draw the base graph with default settings
    nx.draw(G, pos, with_labels=True)

    # Create text labels for the node that show #aircraft, #passengers, etc.
    for v in vertiports:
        # Number of aircraft
        num_aircraft = len(v.current_aircraft)
        # Number of waiting passengers
        num_passengers = len(v.current_passengers)

        # We'll place a text label slightly offset from the node
        x, y = pos[v.name]
        plt.text(x, y + 0.04, f"A: {num_aircraft}, P: {num_passengers}",
                 horizontalalignment='center')

    # Optionally label edges with transport time
    # edge_labels = nx.get_edge_attributes(G, 'transport_time')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Add a title for simulation time
    plt.title(f"Simulation Time: {current_time:.2f}")
    plt.show()
