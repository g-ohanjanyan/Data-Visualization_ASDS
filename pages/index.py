import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page registration
dash.register_page(__name__, path="/")

# Load and clean data
df = pd.read_excel("DataViz.xlsx", engine="openpyxl")
usage_col = 'Օգտվում ե՞ք անկանխիկ վճարամիջոցներից '
region_col = 'Մարզ'
gender_col = 'Պատասխանողի սեռը'
income_col = 'Ձեր միջին ամսական եկամտի միջնակայքը'
df = df[df[usage_col].notna()]
df['Usage Type'] = df[usage_col].map({'Այո': 'Non-Cash', 'Ոչ': 'Cash'})
df['Region'] = df[region_col]
df['Gender'] = df[gender_col]
df['Income Group'] = df[income_col]

# Stats
total_resp = len(df)
noncash_count = (df['Usage Type'] == 'Non-Cash').sum()
cash_count = total_resp - noncash_count

# Final Color Palette
colors_main = ['#A66DD4', '#4FD0E9']  
chart_bg = '#121212'

# KPI Card
def kpi_card(value, label):
    return dbc.Card([
        html.H2(value, style={
            "fontWeight": "bold", "fontSize": "30px",
            "background": "linear-gradient(90deg, #A66DD4, #4FD0E9)",
            "WebkitBackgroundClip": "text",
            "WebkitTextFillColor": "transparent"
        }),
        html.P(label, className="text-white")
    ],
    className="text-center p-3",
    style={
        "backgroundColor": "#1a1a1a",
        "borderRadius": "10px",
        "height": "100%",
        "boxShadow": "0 4px 10px rgba(0,0,0,0.4)"
    })

# Donut chart
usage_counts = df['Usage Type'].value_counts().reset_index()
usage_counts.columns = ['Usage Type', 'Count']
fig_donut = go.Figure(data=[go.Pie(
    labels=usage_counts['Usage Type'],
    values=usage_counts['Count'],
    hole=0.5,
    marker_colors=colors_main
)])
fig_donut.update_layout(
    annotations=[dict(text=str(total_resp), x=0.5, y=0.5, font_size=22, showarrow=False)],
    showlegend=True,
    height=400,
    paper_bgcolor=chart_bg,
    font_color='white'
)

# Gender donut (dynamic)
gender_usage = df.groupby(['Gender', 'Usage Type']).size().reset_index(name='Count')

def create_gender_figure(usage_type):
    subset = gender_usage[gender_usage['Usage Type'] == usage_type]
    fig = px.pie(
        subset,
        names='Gender',
        values='Count',
        hole=0.5,
        color_discrete_sequence=colors_main
    )
    fig.update_layout(
        height=400,
        paper_bgcolor=chart_bg,
        font_color='white',
        margin=dict(t=20, b=20),
        showlegend=False
    )
    return fig

# Region bar chart
grouped = df.groupby(['Region', usage_col]).size().unstack(fill_value=0)
grouped_pct = grouped.div(grouped.sum(axis=1), axis=0) * 100
yes_pct = grouped_pct.get("Այո", pd.Series()).reset_index(name="Percent")
yes_pct = yes_pct.sort_values("Percent", ascending=True)
fig_region = px.bar(
    yes_pct,
    x="Percent",
    y="Region",
    orientation='h',
    text="Percent",
    color="Percent",
    color_continuous_scale=colors_main
)
fig_region.update_layout(
    title="Non-Cash Usage by Region",
    template='plotly_dark',
    font_color='white',
    height=400,
    paper_bgcolor=chart_bg,
    coloraxis_showscale=False,
    margin=dict(t=40, b=20)
)
fig_region.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

# Income line chart
income_order = [
    'Մինչև 100 000 դրամ',
    '101 001 - 200 000 դրամ',
    '201 000 - 500 000 դրամ',
    '501 000 - 1,000 000 դրամ',
    '1,001 000 դրամ և ավել'
]
df['Income Group'] = pd.Categorical(df['Income Group'], categories=income_order, ordered=True)
income_usage = df.groupby(['Income Group', 'Usage Type']).size().reset_index(name='Count')
fig_income = px.line(
    income_usage,
    x='Income Group',
    y='Count',
    color='Usage Type',
    markers=True,
    line_shape='spline',
    color_discrete_map={
        'Non-Cash': colors_main[0],
        'Cash': colors_main[1]
    }
)
fig_income.update_layout(
    title='Cash vs Non-Cash Usage by Income Group',
    height=400,
    paper_bgcolor=chart_bg,
    plot_bgcolor=chart_bg,
    font_color='white'
)

# Shared graph card style
graph_card_style = {
    "padding": "10px",
    "borderRadius": "15px",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.4)",
    "backgroundColor": chart_bg
}

# Layout
layout = dbc.Container([
    html.H2("Payment Dashboard", className="text-center mt-3 mb-4", style={
        "color": "#A66DD4",
        "fontWeight": "bold",
        "fontSize": "34px"
    }),

    dbc.Row([
        dbc.Col(kpi_card("801", "Survey Respondents"), md=2),
        dbc.Col(kpi_card("2023", "Survey Year"), md=2),
        dbc.Col(kpi_card("Nationwide", "Coverage"), md=2),
        dbc.Col(kpi_card(str(noncash_count), "Non-Cash Users"), md=2),
        dbc.Col(kpi_card(str(cash_count), "Cash Users"), md=2)
    ], className="mb-4 justify-content-center"),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_donut), body=True, style=graph_card_style), md=6),
        dbc.Col(dbc.Card([
            html.Label("Select Usage Type:", style={"color": "white", "marginTop": "10px"}),
            dcc.Dropdown(
                id='usage-type-dropdown',
                options=[{'label': i, 'value': i} for i in ['Cash', 'Non-Cash']],
                value='Cash',
                style={"color": "#000000"}
            ),
            dcc.Graph(id='gender-pie-chart')
        ], body=True, style=graph_card_style), md=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_region), body=True, style=graph_card_style), md=6),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_income), body=True, style=graph_card_style), md=6)
    ])
], fluid=True)

# Callback for gender donut toggle
@dash.callback(
    Output('gender-pie-chart', 'figure'),
    Input('usage-type-dropdown', 'value')
)
def update_gender_chart(usage_type):
    return create_gender_figure(usage_type)
