import pandas as pd, igraph as ig, numpy as np
import plotly.graph_objs as go
import plotly
import itertools

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from textwrap import dedent as d
import copy
import base64


def setup_edges(G):
    edge_data = []
    for e in G.es:
        n0, n1 = e.tuple
        x0, y0 = G.vs[n0]['x'], G.vs[n0]['y']
        x1, y1 = G.vs[n1]['x'], G.vs[n1]['y']
        edge_data += [(x0, x1, None, y0, y1, None)]
    return np.array(edge_data)


class LabourNetwork():
    def __init__(self):
        self.four_digit_G = ig.Graph.Read_Pickle("data/skill_scape_graph.pickle")
        self.edge_data = setup_edges(self.four_digit_G)
        self.edge_weights = np.array(self.four_digit_G.es['weight'])
        self.edge_weights = np.argsort(self.edge_weights) / len(self.edge_weights)

        self.current_threshold = 0
        self.main_figure = self.get_labour_figure()
        self.edge_trace = self.update_threshold(0.5)

        self.current_color_choice = "louvain community"
        self.current_size_choice = 'None'
        self.louvain_marker = self.main_figure['data'][1]['marker']
        self.unemployment_marker = {'size':10, 'color':self.four_digit_G.vs['unemployment'], 'cauto':True, 'colorscale':'RdBu', 
                                       'colorbar':{'thickness':20, 'title':'Percentage<br>Employment<br>Change'}}

    def update_threshold(self, threshold):
        if self.current_threshold != threshold:
            ed = self.edge_data[self.edge_weights > threshold,:]
            self.edge_trace = go.Scatter(x=list(ed[:,:3].flatten()), 
                        y=list(ed[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')
            self.current_threshold = threshold
            self.main_figure['data'][0] = self.edge_trace

    def update_colors(self, color_choice):
        if self.current_color_choice != color_choice:
            if color_choice == "louvain community":
                self.main_figure['data'][1]['marker'] = self.louvain_marker 
            elif color_choice == "unemployment":
                self.main_figure['data'][1]['marker'] = self.unemployment_marker
            self.current_color_choice = color_choice
            self.update_size(self.current_size_choice)

    def update_size(self, size_choice):
        if size_choice == 'None':
            self.main_figure['data'][1]['marker']['size'] = 0
        elif size_choice == "total_pop":
            sizes = np.log(np.array(self.four_digit_G.vs['total_pop'])+1)
            sizes = list(30*sizes / np.max(sizes))
            self.main_figure['data'][1]['marker']['size'] = sizes
        self.current_size_choice = size_choice


    def get_updated_graph(self, color_choice, threshold, size_choice):
        self.update_threshold(threshold)
        self.update_colors(color_choice)
        self.update_size(size_choice)
        return self.main_figure


    def get_labour_figure(self, colour_by = "louvain community", new_layout = False, edge_trace = None, size = 10):

        G = self.four_digit_G

        self.edge_trace = go.Scatter(x=list(self.edge_data[:,:3].flatten()), 
                        y=list(self.edge_data[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')

        if new_layout:
            layout = np.array(G.layout_fruchterman_reingold(weights=field).coords)
            G.vs["x"] = [f.item() for f in layout[:,0]]
            G.vs["y"] = [f.item() for f in layout[:,1]]

        node_x = G.vs['x']
        node_y = G.vs['y']
        node_hovertext = ["%s<br>Employed in Aus (1000's): %.2f<br>Percentage Females: %.3f" % items for items in 
                    zip(G.vs['title'], G.vs['total_pop'], np.array(G.vs['Females']) / (np.array(G.vs['Males']) + np.array(G.vs['Females'])))]

        color = [plotly.colors.diverging.Portland[c] for c in G.vs[colour_by]]
        if type(size) == int:
            sizes = size
        else:
            sizes =  G.vs[size]
            sizes = np.log(np.array(sizes)+1)
            sizes = list(20*sizes / np.max(sizes))

        node_trace = go.Scatter(x=node_x, y=node_y, hovertext=node_hovertext, text=[], mode='markers+text', textposition="bottom center", \
                                hoverinfo="text", marker={'size': sizes, 'color':color}, showlegend=True)

        figure = {
                "data": [self.edge_trace, node_trace] ,
                "layout": go.Layout(title='Labour Network Visualization', showlegend=False, hovermode='closest',
                                    margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                    xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    height=600,
                                    clickmode='event+select',
                                    )}
        return figure


labourNetwork = LabourNetwork()

# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

labour_tab = dcc.Tab(label='Labour Networks', children = [
    html.Div(
        className="row",
        children=[ dcc.Markdown(d("""
        ## Labour Market Networks in SA

        As part of a project in collaboration with the MIT Big Data Living Lab and South Australian Government 
        we have been using networks to help analyse the labour market in SA and around Australia.

        Work by Morgan Frank from MIT has used network to examine any labour market. 
        In this work, each possible job in the state is a node. 
        Each of these jobs has a list of skills associated with it and how important those skills are.
        Jobs are connected with weighted edges determined by how similar the skills are between a pair of jobs.
        We remove edges that have very little similarity to construct the graph you see below.

        These skill similarity edges correlate with a persons ability to move from one job to another, 
        and can provide interesting insights into the resilience and potential of the workforce.
       """))
        ]
    ),
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="three columns",
                children=[
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            #### Color Choice
                            """)),
                            dcc.Dropdown(id="color_choice", value="louvain community", options=[
                                {'label':"Cognitive Community", 'value': "louvain community"},
                                {'label':"Unemployment", 'value': "unemployment"},
                                # {'label':"Detailed Occupation (6-digit)", 'value': 6}
                                ]),
                            html.Div(id="color_choice_output")
                        ],
                        # style={'height': '300px'}
                    ),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            \n
                            #### Size Choice
                            """)),
                            dcc.Dropdown(id="size_choice", value="None", options=[
                                {'label':"Uniform", 'value': "None"},
                                {'label':"Workforce Size", 'value': "total_pop"},
                                # {'label':"Detailed Occupation (6-digit)", 'value': 6}
                                ]),
                            html.Div(id="size_choice_output")
                        ],
                        # style={'height': '300px'}
                    ),
                    dcc.Markdown(d("""
                            \n
                            #### Edge Removal 

                            The percentage proportion of edges to keep.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Slider(
                                id='labour_edge_threshold',
                                min=0.1,
                                max=0.9,
                                step=0.1,
                                value = 0.5,
                                marks = {i / 10.0: str(i / 10.0) for i in range(0,10)}
                            )
                        ],
                        style={'height': '300px'}
                    ),
                ]
            ),
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="labour-graph",
                                    figure=labourNetwork.main_figure)],
            ),
        ]
    ),
    html.Div(
        className="row",
        children=[
             html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d(
                        """
                        **Unemployment Estimation**

                        We can estimate what areas and jobs are most effected by COVID.
                        """
                    )),
                    html.Div([
                        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
                            open('assets/April Total Employment Losses.png', 'rb').read()).decode()), style={'width': '100%'})
                    ])
                ]
            ),
            html.Div(
                className="six columns",
                children=[
                    dcc.Markdown(d(
                        """
                        **State Complementarity**

                        Australian States are projected onto the job networks using the *revealed comparative advantage* (RCA) of our job. 
                        The RCA measures the relative advantage or disadvantage of a certain state in employing these workers. 
                        The characteristic occupations of each state are colored along with the edges connecting those occupations. 
                        $RCA\_{j, s} = \\frac{E\_{j,s} / \sum\_{s \in State} E\_{j,s} } { \sum\_{j \in Jobs } E\_{j,s} / \sum\_{j \in Jobs} \sum\_{s \in States} E\_{j,s} }$
                        """
                    )),
                    html.Div([
                        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
                            open('assets/RCA_States_Overlap.png', 'rb').read()).decode()), style={'width': '100%'})
                    ])
                    
                ]
            )
        ]
    )
])


color_choice_output_dict = {
    'louvain community': 
        dcc.Markdown(d(
            """
            Cognitive Community
            louvain community
            """
        )),
    'unemployment':
        dcc.Markdown(d(
            """
            unemployment
            """
        )),
}

size_choice_output_dict = {
    'None': "",
    "total_pop":"Workforce Size"
}