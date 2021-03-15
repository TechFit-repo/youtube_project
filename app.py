import base64
import io
import os
import json
import oauth2client
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_daq as daq
import dash_auth
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.express as px
from wordcloud import WordCloud
import youtube_db as db

#######################
# Data
#######################

def parseData():
    try:
        data = pd.DataFrame()
        channels = ['Meet Kevin','Andrei Jikh','Joma Tech','Ali Abdaal','Graham Stephan']
        you_tube = db.YouTube()
        for channel in channels:
            results = you_tube.searchChannels(query=channel)
            youtube_df = you_tube.createDatabase(results=results)
            data = data.append(youtube_df)
        data = data.reset_index()
        data['channelVideoId'] = data['channelTitle'] + ' ' + data['level_0'].astype(str)
        data['datePublished'] = pd.to_datetime(data['publishedAt'].str.slice(0, 10), format='%Y-%m-%d')
        Current_Date = (datetime.today() + timedelta(days=1)).strftime ('%Y-%m-%d')
        data['todayDate'] = pd.to_datetime(Current_Date, format='%Y-%m-%d')
        data['daysPublished'] = data['todayDate'].sub(data['datePublished'], axis=0).dt.days
        data['averageViewCount'] = round(data['viewCount'].astype(int) / data['daysPublished'].astype(int))
        data['positiveRating'] = round(data['likeCount'].astype(int) / data['viewCount'].astype(int) * 100, 2)
        data['negativeRating'] = round(data['dislikeCount'].astype(int) / data['viewCount'].astype(int) * 100, 2)
        data['engagementRating'] = round(data['commentCount'].astype(int) / data['viewCount'].astype(int) * 100, 2)
    except:
        data = pd.read_csv('dataset.csv',converters={'tags': eval})
    return data

df = parseData()

#######################
# App & Server
#######################

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


#######################
# Styling
#######################

app.title = 'TOP YOUTUBE CHANNEL'

colors = {
        "background": "#ffffff",
        "text": "#004687",
        "heading": "#004687",
        "graphBackground": "#EFEFEF"
        }

#######################
# Components
#######################

power = dbc.Row([daq.PowerButton(id='power-button',
                                 on=True
                                 )
                 ],
                    no_gutters=True,
                    className="ml-auto flex-nowrap mt-3 mt-md-0",
                    align="center",
            )

navbar = dbc.Navbar(
    [
        html.A(dbc.Container(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('TechFit.png'), height="40px")),
                    dbc.Col(dbc.NavbarBrand("Top YouTube Channel", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            )),
            href="https://techfitlab.com",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(power, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

#######################
# Layout
#######################

app.layout = html.Div([navbar,
                          dbc.Row([
                          dbc.Col(dbc.Container([dcc.Graph(id='graph1')
                                                 ]),md=6),
                          dbc.Col(dbc.Container([dcc.Graph(id='graph3')
                                                 ]),md=6,)
                          ]),
                          dbc.Row([dbc.Container(dcc.Graph(id='graph2'))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(dcc.Graph(id='graph4'))
                                  ]),
                          dbc.Row([dbc.Container(html.Div(id='table1'))
                                  ]),
                          html.Br(),
                          html.Br(),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.H4(id='image1_name')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.Img(id='image1')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.H4(id='image2_name')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.Img(id='image2')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.H4(id='image3_name')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.Img(id='image3')))
                                  ]), 
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.H4(id='image4_name')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.Img(id='image4')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.H4(id='image5_name')))
                                  ]),
                        dcc.Markdown('***'),
                          dbc.Row([dbc.Container(html.Center(html.Img(id='image5')))
                                  ])
                        ]
                      )

#######################
# Plots
#######################
@app.callback(Output('graph1', 'figure'), 
             [Input('power-button', 'on')])
def updateGraph1(on):
    if not on:
        data = pd.DataFrame(df.groupby(['channelTitle'])['averageViewCount'].mean())[0:0]
    else:
        data = pd.DataFrame(df.groupby(['channelTitle'])['averageViewCount'].mean())
       
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index,
                y=data.iloc[:,0],
                name='Channels',
                marker_color='rgb(48, 88, 128)'
                ))
    fig.update_layout(
    title='Average Daily Views Count By Channel',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Views',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1
    )
    
    return fig

@app.callback(Output('graph2', 'figure'),
             [Input('power-button', 'on')])
def updateGraph2(on):
    if not on:
        data = pd.DataFrame(df[['channelTitle','positiveRating','negativeRating']].groupby(['channelTitle']).mean())[0:0]
    else:
        data = pd.DataFrame(df[['channelTitle','positiveRating','negativeRating']].groupby(['channelTitle']).mean())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index,
                    y=data.iloc[:,0],
                    name='Positive Rating',
                    marker_color='rgb(0, 153, 153)'
                    ))
    fig.add_trace(go.Bar(x=data.index,
                    y=data.iloc[:,1],
                    name='Negative Rating',
                    marker_color='rgb(96, 96, 96)'
                    ))
    
    fig.update_layout(
        title='Content Quality Rating',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Ratings (%)',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    
    return fig

@app.callback(Output('graph3', 'figure'),
             [Input('power-button', 'on')])
def updateGraph3(on):
    if not on:
        data = pd.DataFrame(df.groupby(['channelTitle'])['engagementRating'].mean())[0:0]
    else:
        data = pd.DataFrame(df.groupby(['channelTitle'])['engagementRating'].mean())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index,
                y=data.iloc[:,0],
                name='Channels',
                marker_color='rgb(48, 88, 128)'
                ))
    fig.update_layout(
    title='Audience Engagement Rating',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Engagement (%)',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1
    )
    
    return fig

@app.callback(Output('graph4', 'figure'),
             [Input('power-button', 'on')])
def updateGraph4(on):
    if not on:
        data = df[['channelTitle','channelVideoId','viewCount']][0:0]
    else:
        data = df[['channelTitle','channelVideoId','viewCount']]
        
    fig = px.treemap(data, path=['channelTitle', 'channelVideoId'], values='viewCount',
                     color="channelTitle", color_discrete_sequence=px.colors.qualitative.Antique)
    
    return fig


@app.callback(Output('table1', 'children'),
             [Input('power-button', 'on')])
def updateTable1(on):
    if not on:
        data = df[['channelTitle','channelVideoId','title','viewCount']][0:0]
    else:
        data = df[['channelTitle','channelVideoId','title','viewCount']]
    
    table = dbc.Container([
    html.Center(html.H6('YouTube Videos')),
    dash_table.DataTable(
        fixed_rows={'headers': True},
        style_table={'height': 400} ,
        style_header={'backgroundColor': '#009999','color': 'white'},
        style_data = {'whiteSpace': 'normal','height': 'auto','lineHeight': '20px'},
        style_cell={'textAlign': 'center','minWidth': '20px', 'width': '20px', 'maxWidth': '20px',},
        columns =[{"name": i, "id": i} for i in data.columns],
        data=data.to_dict('records')
    )]) 
    return table

@app.callback([Output('image1', 'src'),Output('image1_name', 'children')],
              [Input('power-button', 'on')])
def updateImage1(on):
    db_name = 'Meet Kevin'
    db = df[(df['channelTitle']==db_name) & (df['tags'] != 0)]['tags']
    db_tags = []
    for i in db:
        for j in i:
            db_tags.append(j)
    
    if not on:
        db_bag_of_words = 'na'
    else:
        db_bag_of_words = ' '.join([str(item) for item in db_tags])
    
    img = io.BytesIO()        
    wordcloud = WordCloud(width=800, height=300, background_color="white").generate(db_bag_of_words)
    wordcloud.to_image().save(img, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode()), db_name

@app.callback([Output('image2', 'src'),Output('image2_name', 'children')],
              [Input('power-button', 'on')])
def updateImage2(on):
    db_name = 'Andrei Jikh'
    db = df[(df['channelTitle']==db_name) & (df['tags'] != 0)]['tags']
    db_tags = []
    for i in db:
        for j in i:
            db_tags.append(j)
    
    if not on:
        db_bag_of_words = 'na'
    else:
        db_bag_of_words = ' '.join([str(item) for item in db_tags])
    
    img2 = io.BytesIO()        
    wordcloud = WordCloud(width=800, height=300, background_color="white").generate(db_bag_of_words)
    wordcloud.to_image().save(img2, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img2.getvalue()).decode()), db_name

@app.callback([Output('image3', 'src'),Output('image3_name', 'children')],
              [Input('power-button', 'on')])
def updateImage3(on):
    db_name = 'Joma Tech'
    db = df[(df['channelTitle']==db_name) & (df['tags'] != 0)]['tags']
    db_tags = []
    for i in db:
        for j in i:
            db_tags.append(j)
    
    if not on:
        db_bag_of_words = 'na'
    else:
        db_bag_of_words = ' '.join([str(item) for item in db_tags])
    
    img3 = io.BytesIO()        
    wordcloud = WordCloud(width=800, height=300, background_color="white").generate(db_bag_of_words)
    wordcloud.to_image().save(img3, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img3.getvalue()).decode()), db_name

@app.callback([Output('image4', 'src'),Output('image4_name', 'children')],
              [Input('power-button', 'on')])
def updateImage4(on):
    db_name = 'Ali Abdaal'
    db = df[(df['channelTitle']==db_name) & (df['tags'] != 0)]['tags']
    db_tags = []
    for i in db:
        for j in i:
            db_tags.append(j)
    
    if not on:
        db_bag_of_words = 'na'
    else:
        db_bag_of_words = ' '.join([str(item) for item in db_tags])
    
    img4 = io.BytesIO()        
    wordcloud = WordCloud(width=800, height=300, background_color="white").generate(db_bag_of_words)
    wordcloud.to_image().save(img4, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img4.getvalue()).decode()), db_name

@app.callback([Output('image5', 'src'),Output('image5_name', 'children')],
              [Input('power-button', 'on')])
def updateImage5(on):
    db_name = 'Graham Stephan'
    db = df[(df['channelTitle']==db_name) & (df['tags'] != 0)]['tags']
    db_tags = []
    for i in db:
        for j in i:
            db_tags.append(j)
    
    if not on:
        db_bag_of_words = 'na'
    else:
        db_bag_of_words = ' '.join([str(item) for item in db_tags])
    
    img5 = io.BytesIO()        
    wordcloud = WordCloud(width=800, height=300, background_color="white").generate(db_bag_of_words)
    wordcloud.to_image().save(img5, format='PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img5.getvalue()).decode()), db_name

if __name__ == '__main__':
    app.run_server(debug=True)


