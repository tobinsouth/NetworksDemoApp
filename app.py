#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json

import pandas as pd, igraph as ig, numpy as np
from textwrap import dedent as d


from labour import *
from spotify import *
# from information_flow import *
from explain import *

######################################################################################################################################################################
# To improve speed during console runtime, we're gonna do some extra work upfront. 
######################################################################################################################################################################



######################################################################################################################################################################
# This is the setup of the actual dash html interface
######################################################################################################################################################################

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.title = "Tobin South - Stoneham Prize"


app.layout = html.Div([
    #########################Title
    html.Div([html.H1(" Network Graph")],
             className="row",
             style={'textAlign': "center"}),
    dcc.Tabs([explain_tab, labour_tab, spotify_tab])
    
])

######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################

# @app.callback(
#     dash.dependencies.Output('spotify-graph', 'figure'),
#     [dash.dependencies.Input('spotify_pop_threshold', 'value')])
# def update_main_spotify_output(spotify_pop_threshold):
#     return spotify.update_figure(spotify_pop_threshold)

# @app.callback(
#     dash.dependencies.Output('spotify_pop_threshold_output', 'children'),
#     [dash.dependencies.Input('spotify_pop_threshold', 'value')])
# def update_main_spotify_pop_threshold_output(spotify_pop_threshold):
#     return "You have selected a threshold of %d" % spotify_pop_threshold



# Labour Networks Tab Callbacks
@app.callback(
    dash.dependencies.Output('labour-graph', 'figure'),
    [dash.dependencies.Input('color_choice', 'value'), 
     dash.dependencies.Input('labour_edge_threshold', 'value'),
     dash.dependencies.Input('size_choice', 'value')])
def update_main_labour_output(color_choice, labour_edge_threshold, size_choice):
    return labourNetwork.get_updated_graph(color_choice, 1-labour_edge_threshold, size_choice)

@app.callback(
    dash.dependencies.Output('color_choice_output', 'children'),
    [dash.dependencies.Input('color_choice', 'value')])
def update_color_choice_output(color_choice):
    return color_choice_output_dict[color_choice]

@app.callback(
    dash.dependencies.Output('size_choice_output', 'children'),
    [dash.dependencies.Input('size_choice', 'value')])
def update_size_choice_output(size_choice):
    return size_choice_output_dict[size_choice]


# Explain Tab Callbacks
@app.callback(
    dash.dependencies.Output('explain_graph', 'figure'),
    [dash.dependencies.Input('explain_edge_prob', 'value'), 
     dash.dependencies.Input('explain_number_of_nodes', 'value'),
     dash.dependencies.Input('explain_graph_type', 'value'),
     dash.dependencies.Input('explain_centrality', 'value')])
def update_explain_graph(explain_edge_prob, explain_number_of_nodes, explain_graph_type, explain_centrality):
    return explain_make_network(explain_number_of_nodes, explain_edge_prob, explain_graph_type, explain_centrality)

@app.callback(
    dash.dependencies.Output('explain_N_M_output', 'children'),
    [dash.dependencies.Input('explain_edge_prob', 'value'), 
     dash.dependencies.Input('explain_number_of_nodes', 'value')])
def update_explain_N_M_output(explain_edge_prob, explain_number_of_nodes):
    return "You have selected %d nodes and an edge probability of %.1f" % (explain_number_of_nodes, explain_edge_prob)

@app.callback(
    dash.dependencies.Output('explain_graph_type_output', 'children'),
    [dash.dependencies.Input('explain_graph_type', 'value')])
def update_explain_graph_type_output(explain_graph_type):
    return explain_graph_type_output_dict[explain_graph_type]

@app.callback(
    dash.dependencies.Output('explain_centrality_output', 'children'),
    [dash.dependencies.Input('explain_centrality', 'value')])
def update_explain_graph_type_output(explain_graph_type):
    return explain_centrality_output_dict[explain_graph_type]



if __name__ == '__main__':
    app.run_server(debug=True)

