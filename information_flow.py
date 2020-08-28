import pandas as pd, igraph as ig, numpy as np
import plotly.graph_objs as go
import matplotlib.cm as cm
import plotly
import itertools

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from textwrap import dedent as d

from addEdge import addEdge


import scipy.stats as ss
class InformationFlow():
    def __init__(self):
        self.information_flow_graph = ig.Graph.Read_Pickle("data/information_flow_graph.pickle")
        self.edge_weights = self.get_edge_weights()
        self.edge_data = self.make_edge_data()
        self.figure = self.make_inital_graph()
        
        
    def threshold_edges(self, threshold):
        
        edge_data = self.edge_data[self.edge_weights > threshold, :]
        
        edge_trace = go.Scatter(x=list(edge_data[:,:3].flatten()), 
                        y=list(edge_data[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')
        self.figure['data'][0] = edge_trace
        return self.figure
    
    def make_edge_data(self):
        G = self.information_flow_graph
        edge_data = []
        for e in G.es:
            n0, n1 = e.tuple
            x0, y0 = G.vs[n0]['x'], G.vs[n0]['y']
            x1, y1 = G.vs[n1]['x'], G.vs[n1]['y']
            edge_data += [(x0, x1, None, y0, y1, None)]
        edge_data = np.array(edge_data)
        
        return edge_data
    
    def get_edge_weights(self):
        edge_weights = np.array(self.information_flow_graph.es['weight'])
        weigths_rank = ss.rankdata(edge_weights)
        weigths_percentile = weigths_rank / max(weigths_rank)
        return weigths_percentile
    
        
    def make_inital_graph(self):
        
        G = self.information_flow_graph
        
        edge_trace = go.Scatter(x=list(self.edge_data[:,:3].flatten()), 
                        y=list(self.edge_data[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')

        hovertext = ["%s<br>Bias: %s" % items for items in zip(G.vs['name'], G.vs['bias'])]
        
        node_trace = go.Scatter(x=G.vs['x'], y=G.vs['y'], 
                                hovertext=hovertext, text=[], mode='markers+text', textposition="bottom center", \
                                hoverinfo="text", marker={'size': 10, 'color':G.vs['hex_color']})

        figure = {
            "data": [edge_trace, node_trace] ,
            "layout": go.Layout(title='News Flow Visualization', showlegend=True, hovermode='closest',
                                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                height=600,
                                clickmode='event+select',
                                )}
        return figure



information_flow = InformationFlow()



information_flow_tab = dcc.Tab(label='Information Flow', children = [
	html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Flow Threshold**

                           	Remove low flow edges.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Slider(
                                id='information_flow_threshold',
                                min=0,
                                max=1,
                         		step = 0.05,
                                value = 0.5,
                                # {i: str(i) for i in [0,46,47,69]}
                            ),
                            html.Br(),
                            html.Div(id = 'information_flow_threshold_output')
                        ],
                        style={'height': '300px'}
                    )
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="information_flow-graph",
                                    figure=information_flow.threshold_edges(0.5))],
            ),
        ]
    )
])

