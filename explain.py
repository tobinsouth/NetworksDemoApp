# About Networks Explanation

import igraph as ig
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from textwrap import dedent as d
import numpy as np


def explain_make_network(n, p, style = 'Erdős–Rényi Random Graph', color = "None"):
    if style == 'Erdős–Rényi Random Graph':
        G = ig.Graph.Erdos_Renyi(n, p)
    elif style == 'Barabási–Albert Random Graph':
        G = ig.Graph.Barabasi(n, int(p*((n**2)/2 - n)))

    layout = np.array(G.layout_fruchterman_reingold().coords)
    G.vs["x"] = [f.item() for f in layout[:,0]]
    G.vs["y"] = [f.item() for f in layout[:,1]]

    edge_x, edge_y =[],[]
    for e in G.es:
        n0, n1 = e.tuple
        x0, y0 = G.vs[n0]['x'], G.vs[n0]['y']
        x1, y1 = G.vs[n1]['x'], G.vs[n1]['y']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(x=edge_x, 
                    y=edge_y,
                    mode='lines',\
                    line={'width': 0.2},\
                    line_shape='spline',\
                    opacity=0.5,\
                    hoverinfo='none')
       
    if color == 'Eigencentraility':
        G.vs['centrality'] = G.eigenvector_centrality()
        node_trace = go.Scatter(x=G.vs['x'], y=G.vs['y'], hovertext=[], text=[], 
            mode='markers', textposition="bottom center", hoverinfo="none", 
            marker={'size': 10,
                    'color':G.vs['centrality'], 'cauto':True, 'colorscale':'Bluered',
                    'colorbar':{'thickness':20, 'title':'Eigenvector<br>Centrality'}
                    })
    else:
         node_trace = go.Scatter(x=G.vs['x'], y=G.vs['y'], hovertext=[], text=[], 
            mode='markers', textposition="bottom center", \
                                hoverinfo="none", marker={'size': 10})
    figure = {
        "data": [edge_trace, node_trace] ,
        "layout": go.Layout(title=style, showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            )}
    return figure


explain_tab = dcc.Tab(label='Introduction', children = [
    html.Div(
        className="row",
        children=[ dcc.Markdown(d("""
        ## An introduction to networks


        A network is simply a collection of connected objects. We refer to the objects as *nodes* or *vertices*, and usually draw them as points. 
        We refer to the connections between the nodes as *edges*, and usually draw them as lines between points.
        In mathematics, networks are often referred to as graphs, and the area of mathematics concerning the study of graphs is called graph theory.


        Networks can represent all sorts of systems in the real world. 
        For example, one could describe the Internet as a network where the nodes are computers or other devices and the edges are connections between the devices. 
        The World Wide Web is a huge network where the pages are nodes and links are the edges. Famously, this network was used by Google to create their search engine algorithms.
        Other common network examples are you social media friend networks on Facebook or Twitter, or the network of academic papers connected by co-authors.
        Importantly, these nodes can be real things in the real world, and describing them using networks can be a very powerful tool.
       
        Encapsulating systems as networks can allow us to solve challenging problems and understand dynamics better. However, creating a network from data can often be a challenge. 
        """))
        ]
    ),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d("""
                            ## Random Graphs Generator

                            One of the most common ways to play with networks is to generate them randomly using an algorithm. 
                            Here we can generate some random graphs of different types and see how they behave.                    
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Number of Nodes**
                            """)),
                            dcc.Slider(
                                id='explain_number_of_nodes',
                                min=1,
                                max=100,
                                step=1,
                                value = 10,
                                # marks = {i / 10.0: str(i / 10.0) for i in range(0,10)}
                            ),
                            dcc.Markdown(d("""
                            **Probability of an edge between two nodes**
                            """)),
                            dcc.Slider(
                                id='explain_edge_prob',
                                min=0,
                                max=1,
                                step=0.1,
                                value = 0.5,
                                # marks = {i / 10.0: str(i / 10.0) for i in range(0,10)}
                            ),
                            html.Div(id="explain_N_M_output"),
                            dcc.Markdown(d("""
                            ### Graph Type 
                            There are many different ways to generate a graph. Here is just a few. Have a play and see how they behave!
                            """)),
                            dcc.Dropdown(id="explain_graph_type", value="Erdős–Rényi Random Graph", 
                                options=[
                                {'label':"Erdős–Rényi", 'value': "Erdős–Rényi Random Graph"},
                                {'label':"Barabási–Albert", 'value': "Barabási–Albert Random Graph"},
                                ]),
                            html.Div(id="explain_graph_type_output"),
                            dcc.Markdown(d("""
                            ### Graph Centrality 
                            Graph centrality is a way of asking how important nodes are in a graph. This can be useful for many applications; 
                            however there are many ways to define the centrality of nodes in the graph. Here is some example centrality measures to play with.
                            """)),
                            dcc.Dropdown(id="explain_centrality", value="None", 
                                options=[
                                {'label':"None", 'value': "None"},
                                {'label':"Eigenvector Centrality", 'value': "Eigencentraility"},
                                ]),
                            html.Div(id="explain_centrality_output")
                        ],
                        style={'height': '300px'}
                    ),

                    html.Div(
                        className="twelve columns",
                        children=[
                            
                        ],
                        style={'height': '300px'}
                    ),
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="six columns",
                children=[dcc.Graph(id="explain_graph",
                                    figure=explain_make_network(10, 0.5))],
            ),
        ]
    )
])

explain_centrality_output_dict ={
    'None':"",
    "Eigencentraility":"Eigencentraility is cool"
}

explain_graph_type_output_dict = {
    'Erdős–Rényi Random Graph': 
        "Erdős–Rényi is the simplest kind of random graph there is. We create N nodes and connect them using M edges.",
    'Barabási–Albert Random Graph':
        "A Barabási–Albert random graph is more special. It's desired to replace real world networks more closely. Rich get richer."

}
