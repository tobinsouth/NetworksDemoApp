import pandas as pd, igraph as ig, numpy as np

import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d

import plotly.graph_objs as go
import plotly.express as px
import base64 # For rendering images




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

		hovertext = ["Name: %s<br>Popularity: %d<br>Followers: %d" % (artist, pop, followers) for artist, pop, followers in zip(G.vs['Artist'], G.vs['Popularity'], G.vs['Followers'])]

		node_trace = go.Scatter(x=G.vs['x'], y=G.vs['y'], hovertext=hovertext, text=[], mode='markers+text', textposition="bottom center", \
								hoverinfo="text", marker={'size': sizes, 'color':G.vs['centrality'], 'cauto':True, 'colorscale':'Bluered',
								'colorbar':{'thickness':20, 'title':'Network<br>Centrality'}})

		figure = {
			"data": [edge_trace, node_trace] ,
			"layout": go.Layout(title='Spotify Most Central Core', showlegend=False, hovermode='closest',
								margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
								xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
								yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
								height=600,
								clickmode='event+select',
								)}
		return figure



centrality_artists_results = pd.read_csv('data/centrality_artists_results.csv')

grouped = centrality_artists_results.groupby('Eigenvector')
first = grouped.get_group('First')
second = grouped.get_group('Second')

first_average = first.groupby('Genre').apply(
    lambda x: x.groupby('Threshold')['Centraility'].mean()).reset_index().melt(id_vars = 'Genre', value_name='Centrality')

second_average = second.groupby('Genre').apply(
    lambda x: x.groupby('Threshold')['Centraility'].mean()).reset_index().melt(id_vars = 'Genre', value_name='Centrality')


def plot_first_eigencentraility(threshold):
	fig = px.line(first_average, x="Threshold", y="Centrality", 
              title='First Eigenvector (Eigencentraility)', color='Genre',
              labels = dict(Centrality = "Average Group Centrality",
          					Threshold = "Popularity Threshold"))
	choice = first_average.set_index('Threshold').loc[threshold].sort_values('Centrality').iloc[-1]
	fig = fig.add_trace(
	    go.Scatter(x = [threshold], y = [choice.Centrality], 
	               marker = {'size':20},
	               hovertext = ["Average Centrality of\nMost Central Group of\nArtists at threshold %d" % threshold], 
	               showlegend = False)
	)
	return fig

def plot_second_eigencentraility(threshold):
	fig = px.line(second_average, x="Threshold", y="Centrality", 
              title='Second Eigenvector', color='Genre',
              labels = dict(Centrality = "Average Group Centrality",
              				Threshold = "Popularity Threshold"))
	choice = second_average.set_index('Threshold').loc[threshold].sort_values('Centrality').iloc[-1]
	fig = fig.add_trace(
	    go.Scatter(x = [threshold], y = [choice.Centrality], 
	               marker = {'size':20},
	               hovertext = ["Average Second Eigenvector Value\n of group at threshold %d" % threshold], 
	               showlegend = False)
	)
	return fig

spotify = Spotify()


# Define the tab html
spotify_tab = dcc.Tab(label='Spotify Collaboration', children = [
	html.Div(
        className="row",
        children=[ dcc.Markdown(d("""
        ## Popularity and Centrality in the Spotify Artist Collaboration Graph
        #### Critical transitions in eigenvector centrality

        Based on a paper that has recently been submitted for review 
        (but is also [available as a pre-print ;)](https://arxiv.org/abs/2008.11428)), 
        we create a network where nodes are musical artists and edges are collaborations or covers. 
        This data is collected from Spotify using their API. 
        In total the graph has 1,250,065 artists (a bit too big to show here). 
        Each artist also has a popularity between 0 and 100, where 100 is the most streamed artist.

        If we take the eigenvector centrality of the whole graph, 
        the classical artists are the most important (central) in all of music.
        However, if we only look at the *most popular* artists, the most central core is the rappers. 
        While this is already surprising, the way in which this happens is the interesting maths. 
        We see a critical transition between the centrality of the two groups, 
        where the second eigenvector swaps in dominance to the first. 

        Have a play with the popularity threshold and look at the most central artists!
       """))
        ]
    ),
	html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d("""
                            ## Popularity Threshold

                           	We look a subgraph using only the artists above this popularity. 
                           	We then calculate the centrality to produce these plots!
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
                                marks = dict(zip([0,30,45,48,69], ["0","30","45","48","69"]))
                            ),
                            html.Br(),
                            html.Div(id = 'spotify_pop_threshold_output')
                        ]
                    ),
                    html.Div(className = 'twelve columns', style={'height': '50px'}),
                    html.Div(
		                className="twelve columns",
		                children=[dcc.Graph(id="spotify-graph",
		                                    figure=spotify.update_figure(0) )],
		            ),
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="six columns",
                children=[
		            html.Div(
		                className="twelve columns",
		                children=[dcc.Graph(id="spotify_first_eigenvector_graph",
		                                    figure=plot_first_eigencentraility(0))],
		            ),
		             html.Div(
		                className="twelve columns",
		                children=[dcc.Graph(id="spotify_second_eigenvector_graph",
		                                    figure=plot_second_eigencentraility(0))],
		            ),
                ]
            )
        ]
    ),
    html.Div(className = 'row', style={'height': '50px'}),
    html.Div(
	    className="row",
	    children=[ dcc.Markdown(d("""
	    ## Social Group Centrality Model

	    In the paper we propose a random graph based model of social group centrality (SGC) 
	    as a simplified way of capturing the dynamics of critical changes in centrality under thresholding. 
	    The SGC model consists of three groups; “celebrities”, “community leaders” and “the masses.” 
	    The masses are the largest group consisting of a randomly generated Barab́asi–Albert graph. 

	    Using this simulated model, we help explain how the critical transition occurs between the most central group. 
	    To find out more, please read the [paper](https://arxiv.org/abs/2008.11428) or ask me questions!

	   """))
		]
	),
    html.Div(
    	className = 'row', 
    	children = [
		       	html.Div(className= "four columns", children = [
		       		html.Div(className='container', children = [
				        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
				            open('assets/PopDegreeSuper.png', 'rb').read()).decode()), style={'width': '100%'}),
				        html.Div(style = {'height':'20px'}),
				        html.Div(children = ["Popularity and Degree in Spotify Data"])
    			])]),
		       	html.Div(className= "four columns", children = [
		       		html.Div(className='container', children = [
				        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
				            open('assets/leaders_vs_celebrities_threshold1.png', 'rb').read()).decode()), style={'width': '90%'}),
				        html.Div(children = ["Initial Social Group Centrality Model"])
    			])]),
		       	html.Div(className= "four columns", children = [
		       		html.Div(className='container', children = [
				        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
				            open('assets/leaders_vs_celebrities_threshold2.png', 'rb').read()).decode()), style={'width': '90%'}),
				        html.Div(children = ["Model After Popularity Threshold is Applied"])

    			])])
    	]
    )

])



