import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Page registration
dash.register_page(__name__, path="/overview")

# Load data
df = pd.read_excel("DataViz.xlsx", engine="openpyxl")

# Theme
colors_main = ['#A66DD4', '#4FD0E9']
chart_bg = '#121212'

# Usage & employment
usage_col = 'Օգտվում ե՞ք անկանխիկ վճարամիջոցներից '
df = df[df[usage_col].notna()]
df['Usage Type'] = df[usage_col].map({'Այո': 'Non-Cash', 'Ոչ': 'Cash'})

employment_col = "Աշխատում եք որպես"
df["Employment Status"] = df[employment_col].apply(
    lambda x: "Employed" if isinstance(x, str) and x.strip() not in ["Ոչ", "Չեմ աշխատում", ""] else "Unemployed"
)

storage_col = "Եթե Ձեր ամբողջ գումարը ստիպված լինեք պահել միայն կանխիկ կամ միայն անկանխիկ, ո՞ր եղանակը կնախընտրեիք"
reason_columns = [
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Տեղեկատվության կամ գիտելիքի պակաս)',
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Հեռախոսի կամ համակարգչի բացակայություն)',
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Ինտերնետի հասանելիություն)',
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Վստահելիության պակաս)',
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Անվտանգություն)',
    'Ի՞նչն է պատճառը, որ չեք օգտվում անկանխիկ վճարային ծառայություններից(Սովորություն)'
]

# Layout
layout = dbc.Container([
    html.H2("Behavioral Analysis of Cash vs Non-Cash Usage", className="text-center mt-3 mb-4", style={
        "color": "#A66DD4", "fontWeight": "bold", "fontSize": "32px"
    }),

    dbc.Row([
        dbc.Col([
            html.Label("Select Usage Type:", style={"color": "white"}),
            dcc.Dropdown(
                id="usage-type-selector",
                options=[{"label": i, "value": i} for i in df["Usage Type"].unique()],
                value="Cash",
                style={"color": "#000000"}
            )
        ], md=6),
        dbc.Col([
            html.Label("Select Employment Status:", style={"color": "white"}),
            dcc.Dropdown(
                id="employment-status-selector",
                options=[{"label": i, "value": i} for i in df["Employment Status"].unique()],
                value="Employed",
                style={"color": "#000000"}
            )
        ], md=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="storage-chart"), md=6),
        dbc.Col(dcc.Graph(id="barriers-chart"), md=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="transaction-comparison-chart"), md=12)
    ], className="mb-4")
], fluid=True)

@dash.callback(
    Output("storage-chart", "figure"),
    Output("barriers-chart", "figure"),
    Output("transaction-comparison-chart", "figure"),
    Input("usage-type-selector", "value"),
    Input("employment-status-selector", "value")
)
def update_charts(usage_type, employment_status):
    filtered = df[(df["Usage Type"] == usage_type) & (df["Employment Status"] == employment_status)]

    # Pie chart for storage
    if filtered[storage_col].notna().sum() > 0:
        storage_counts = filtered[storage_col].value_counts().reset_index()
        storage_counts.columns = ['Storage Preference', 'Count']
        fig_storage = px.pie(storage_counts, names='Storage Preference', values='Count', hole=0.5,
                             color_discrete_sequence=colors_main)
        fig_storage.update_layout(title="Preferred Storage Method",
                                  paper_bgcolor=chart_bg, font_color='white')
    else:
        fig_storage = px.bar(title="No storage data available")
        fig_storage.update_layout(paper_bgcolor=chart_bg, font_color='white')

    # Bubble chart for barriers
    if filtered.empty:
        fig_barriers = px.bar(title="No barrier data available")
        fig_barriers.update_layout(paper_bgcolor=chart_bg, font_color='white')
    else:
        total = len(filtered)
        counts = []
        for col in reason_columns:
            label = col.split("(")[-1].rstrip(")")
            if col in filtered.columns:
                count = filtered[col].apply(lambda x: isinstance(x, str) and x.strip() != "").sum()
                percent = round(100 * count / total, 1) if total > 0 else 0
                counts.append({"Reason": label, "Percent": percent})

        df_barriers = pd.DataFrame(counts)

        if df_barriers.empty or df_barriers["Percent"].sum() == 0:
            fig_barriers = px.bar(title="No selected barriers")
            fig_barriers.update_layout(paper_bgcolor=chart_bg, font_color='white')
        else:
            fig_barriers = px.scatter(
                df_barriers,
                x="Percent",
                y="Reason",
                size="Percent",
                color="Percent",
                color_continuous_scale=colors_main,
                size_max=50,
                hover_name="Reason"
            )
            fig_barriers.update_layout(
                title="Barriers to Non-Cash Usage",
                paper_bgcolor=chart_bg,
                font_color='white',
                yaxis_title="",
                xaxis_title="Percent",
                margin=dict(t=40, b=60, l=120)
            )

    # New transaction comparison chart
    banking_cols = {
        'Ներհայաստանյան փոխանցումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ բանկինգի բջջային հավելվածով(Ներհայաստանյան փոխանցումներ)',
        'Միջպետական փոխանցումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ բանկինգի բջջային հավելվածով(Միջպետական փոխանցումներ)',
        'Վճարումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ բանկինգի բջջային հավելվածով(Վաճարումներ)',
        'Օնլայն գնումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ բանկինգի բջջային հավելվածով(Օնլայն գնումներ)',
        'Կոմունալների վճարում': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ բանկինգի բջջային հավելվածով(Կոմունալների վճարում)'
    }

    wallet_cols = {
        'Ներհայաստանյան փոխանցումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ էլեկտրոնային դրամապանակ բջջային հավելվածներով(Ներհայաստանյան փոխանցումներ)',
        'Միջպետական փոխանցումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ էլեկտրոնային դրամապանակ բջջային հավելվածներով(Միջպետական փոխանցումներ)',
        'Վճարումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ էլեկտրոնային դրամապանակ բջջային հավելվածներով(Վճարումներ)',
        'Օնլայն գնումներ': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ էլեկտրոնային դրամապանակ բջջային հավելվածներով(Օնլայն գնումներ)',
        'Կոմունալների վճարում': 'Խնդրում եմ թվարկեք այն անկանխիկ գործարքները, որոնք իրականացնում եք առցանց՝ էլեկտրոնային դրամապանակ բջջային հավելվածներով(Կոմունալների վճարում)'
    }

    total_banking = df[list(banking_cols.values())].notnull().sum().sum()
    total_wallet = df[list(wallet_cols.values())].notnull().sum().sum()

    banking_percent = {key: (df[col].notnull().sum() / total_banking * 100) if total_banking else 0 for key, col in banking_cols.items()}
    wallet_percent = {key: (df[col].notnull().sum() / total_wallet * 100) if total_wallet else 0 for key, col in wallet_cols.items()}

    data_tx = pd.DataFrame({
        'Գործարքի Տեսակը': list(banking_cols.keys()),
        'Բանկային հավելված (%)': list(banking_percent.values()),
        'Էլեկտրոնային դրամապանակ (%)': list(wallet_percent.values())
    })

    data_tx = data_tx[(data_tx['Բանկային հավելված (%)'] > 0) | (data_tx['Էլեկտրոնային դրամապանակ (%)'] > 0)]
    melted_tx = data_tx.melt(
        id_vars='Գործարքի Տեսակը',
        var_name='Օգտագործման Տեսակը',
        value_name='Տոկոս'
    )

    fig_tx = px.scatter(
        melted_tx,
        x='Տոկոս',
        y='Գործարքի Տեսակը',
        color='Օգտագործման Տեսակը',
        size='Տոկոս',
        size_max=50,
        text=melted_tx['Տոկոս'].map(lambda x: f'{x:.1f}%'),
        color_discrete_sequence=['#A66DD4', '#4FD0E9'],
        title='Անկանխիկ Գործարքների Համեմատություն'
    )
    fig_tx.update_layout(
        xaxis_title='Տոկոս (%)',
        yaxis_title='Գործարքի Տեսակը',
        paper_bgcolor=chart_bg,
        plot_bgcolor=chart_bg,
        font_color='white',
        margin=dict(t=70, l=100, r=40, b=60),
        legend=dict(
            title='Օգտագործման Տեսակը',
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=13)
        )
    )
    fig_tx.update_traces(textposition='top center')

    return fig_storage, fig_barriers, fig_tx