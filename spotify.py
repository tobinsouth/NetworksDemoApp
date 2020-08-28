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


class Spotify():
	def __init__(self):
		self.top_centrality = pd.read_csv('data/top100results.csv')
		self.centrality_lookup = self.top_centrality.groupby('Threshold').apply(lambda x: x.set_index('ID')['Centraility'].to_dict()).to_dict()
		self.spotify_core_graph = ig.Graph.Read_Pickle("data/spotify_core_graph.pickle")

	def update_figure(self, threshold):
		subgraph = self.threshold_spotify(threshold)
		return self.get_labour_figure(subgraph)

	def threshold_spotify(self, threshold):
		subgraph = self.spotify_core_graph.subgraph(self.centrality_lookup[threshold].keys())
		subgraph.vs['centrality'] = [self.centrality_lookup[threshold][v] for v in subgraph.vs['name']]
		return subgraph

	def get_labour_figure(self, G):
		edge_data = []
		for e in G.es:
		    n0, n1 = e.tuple
		    x0, y0 = G.vs[n0]['x'], G.vs[n0]['y']
		    x1, y1 = G.vs[n1]['x'], G.vs[n1]['y']
		    edge_data += [(x0, x1, None, y0, y1, None)]
		edge_data = np.array(edge_data)
		edge_trace = go.Scatter(x=list(edge_data[:,:3].flatten()), 
						y=list(edge_data[:,3:].flatten()),
						mode='lines',\
						line={'width': 0.2},\
						line_shape='spline',\
						opacity=0.5,\
						hoverinfo='none')


		sizes =  np.array(G.vs['Popularity']) / 3

		hovertext = ["Name: %s\nPopularity: %d\nFollowers: %d" % (artist, pop, followers) for artist, pop, followers in zip(G.vs['Artist'], G.vs['Popularity'], G.vs['Followers'])]

		node_trace = go.Scatter(x=G.vs['x'], y=G.vs['y'], hovertext=hovertext, text=[], mode='markers+text', textposition="bottom center", \
								hoverinfo="text", marker={'size': sizes, 'color':G.vs['centrality'], 'cauto':True, 'colorscale':'Bluered',
								'colorbar':{'thickness':20, 'title':'Network<br>Centrality'}})

		figure = {
			"data": [edge_trace, node_trace] ,
			"layout": go.Layout(title='Spotify Visualization', showlegend=False, hovermode='closest',
								margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
								xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
								yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
								height=600,
								clickmode='event+select',
								)}
		return figure



spotify = Spotify()


spotify_tab = dcc.Tab(label='Spotify Collaboration', children = [
	html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Popularity Threshold**

                           	We take a subgraph using only the artists above this popularity.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Slider(
                                id='spotify_pop_threshold',
                                min=0,
                                max=69,
                                step=1,
                                value = 0,
                                marks = dict(zip([0,30,46,47,69], ["0","30","","47","69"]))
                                # {i: str(i) for i in [0,46,47,69]}
                            ),
                            html.Br(),
                            html.Div(id = 'spotify_pop_threshold_output')
                        ],
                        style={'height': '300px'}
                    )
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="spotify-graph",
                                    figure=spotify.update_figure(0))],
            ),
        ]
    )
])



