#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d


from labour import *
from spotify import *
from explain import *
# from information_flow import *


# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.title = "Tobin South - Stoneham Prize"


# Setup the website layout.
app.layout = html.Div([
    #########################Title
    html.Div([html.H1("Networks are Everywhere")],
             className="row",
             style={'textAlign': "center"}),
    html.Div(
        className="row",
        children=[ dcc.Markdown(d("""
        Networks underpin many aspects of everyday life. 
        From our social sphere and labour markets to ecosystem of nature and creativity, 
        hidden networks can reveal much about how we connect and where each of us fit into the bigger picture.
        Mathematics provides a powerful tool for modelling and analysing these networks.
        In this app, we will see just a small explain of the kind of networks that we can obverse around us.
        Click the tabs to find out more about the work Tobin has been doing during his MPhil.
       """))
        ]
    ),
    dcc.Tabs([explain_tab, labour_tab, spotify_tab])

]) 

# This line is needed for webhosting
server = app.server 

######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################

# Spotify Tab Callbacks
@app.callback(
    dash.dependencies.Output('spotify-graph', 'figure'),
    [dash.dependencies.Input('spotify_pop_threshold', 'value')])
def update_main_spotify_output(spotify_pop_threshold):
    return spotify.update_figure(spotify_pop_threshold)

@app.callback(
    dash.dependencies.Output('spotify_first_eigenvector_graph', 'figure'),
    [dash.dependencies.Input('spotify_pop_threshold', 'value')])
def update_first_eigenvector_graph(spotify_pop_threshold):
    return plot_first_eigencentraility(spotify_pop_threshold)

@app.callback(
    dash.dependencies.Output('spotify_second_eigenvector_graph', 'figure'),
    [dash.dependencies.Input('spotify_pop_threshold', 'value')])
def update_second_eigenvector_graph(spotify_pop_threshold):
    return plot_second_eigencentraility(spotify_pop_threshold)

@app.callback(
    dash.dependencies.Output('spotify_pop_threshold_output', 'children'),
    [dash.dependencies.Input('spotify_pop_threshold', 'value')])
def update_main_spotify_pop_threshold_output(spotify_pop_threshold):
    return "You have selected a threshold of %d" % spotify_pop_threshold



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
    app.run_server()

