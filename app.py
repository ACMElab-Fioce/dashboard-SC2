#pip install dash
#pip install pandas
#pip install openpyxl

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#--------------------------------------------------------


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import json
import requests

# Aplicativo do Flask
app = Dash(__name__, external_stylesheets=['./static/css/style.css'])  

# Base de dados
df = pd.read_excel("./database/ACMELab-SC2-Seq.xlsx")

# --------------------------------------------------------
# Cores
# --------------------------------------------------------
cores_repeticao = {
    "MELHOR REPETICAO": "#008744",
    "PIOR REPETICAO": "#d62d20",
    "CONTROLE": "#673888"
}

cores_laboratorios = {
    "CENTRO DE HEMATOLOGIA E HEMOTERAPIA DO CEARA (HEMOCE)": "#cc2a36",
    "UNIDADE DE APOIO AO DIAGNOSTICO DA COVID 19 (UNADIG)": "#00a0b0",
    "LABORATORIO CENTRAL DE SAUDE PUBLICA (LACEN)": "#bcd42a",
    "LABORATORIO ARGOS (ARGOS)": "#6a329f"
}

cores_qualidade = {
    "GOOD": "#88d8b0",
    "MEDIOCRE": "#ffcc5c",
    "BAD": "#ff6f69"
}

cores_variantes = {
    "OUTRAS": "#8b9dc3",
    "VOI ZETA (P.2-LIKE)": "#d3a625",
    "VOC GAMA (P.1-LIKE)": "#005b96",
    "VOC DELTA (B.1.617.2-LIKE)": "#008080",
    "VOC OMICRON (BA.1-LIKE)": "#be29ec"
}

cores_resultado = {
    "CONCLUSIVO": "#05d9e8",
    "INCONCLUSIVO": "#ff2a6d",
    "CONTROLE": "#d1f7ff"
}

cores_estados = [0, 'rgb(240,240,240)'], [0.1, 'rgb(200,200,200)'], [1, 'rgb(0,0,255)']

# -------------------------------
#Mapa
# -------------------------------
todos_estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 
                 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
                 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
                 'SP', 'SE', 'TO']

# ---------------------------------------------------------
# Listas para botões
# ---------------------------------------------------------
repe = list(df["melhor_repeticao"].unique())
repe.append("Todos")

labs = list(df["laboratorio"].dropna().unique())
labs.append("Todos")

lotes = list(df["lote"].unique())
lotes.append("Todos")

# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------
def create_layout():
    return html.Div(children=[
        html.Div(children=[html.H1(children='ACMELab dashboard')], className='centered-container'),
        
        html.Div(children=[
            html.Div(children=[
                html.H1(children='Quantitativo de sequenciamentos'),
                dcc.Dropdown(repe, value='Todos', id='botao_repeticoes'),
                dcc.Graph(id='quantitativo_repeticoes')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            html.Div(children=[
                html.H1(children='Origem das amostras'),
                dcc.Dropdown(labs, value='Todos', id='botao_laboratorios'),
                dcc.Graph(id='quantitativo_laboratorios')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        dcc.Dropdown(lotes, value='Todos', id='botao_lotes'),
        
        html.H1(children='Qualidade dos sequenciamentos'),
        html.Div(children=[
            html.Div(children=[
                dcc.Graph(id='qualidade_genomas_montados')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            html.Div(children=[
                dcc.Graph(id='qualidade_resultados')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.H1(children='Linhagens sequenciadas'),
        html.Div(children=[
            html.Div(children=[
                dcc.Graph(id="variantes_mensais")
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            html.Div(children=[
                dcc.Graph(id='quantitativo_variantes')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div(children=[
                dcc.Graph(id='mapa_variantes')
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ])

app.layout = create_layout()

# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
@app.callback(
    Output('quantitativo_repeticoes', 'figure'),
    Input('botao_repeticoes', 'value')
)
def update_fig1(value):
    contagem_repeticao = df.groupby(['lote', 'melhor_repeticao']).size().reset_index(name='Quantitativo')
    contagem_repeticao.columns = ['Lote', 'Melhor repeticao', 'Quantitativo']

    if value == "Todos":
        contagem_repeticao_filtrado = contagem_repeticao
    else:
        contagem_repeticao_filtrado = contagem_repeticao.loc[contagem_repeticao['Melhor repeticao'] == value, :]

    fig1 = px.bar(contagem_repeticao_filtrado, x='Lote', y='Quantitativo', color='Melhor repeticao', title='', color_discrete_map=cores_repeticao)
    fig1.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
        yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig1



@app.callback(
    Output('quantitativo_laboratorios', 'figure'),
    Input('botao_laboratorios', 'value')
)
def update_fig2(value):
    contagem_laboratorios = df.groupby(['lote', 'laboratorio']).size().reset_index(name='Quantitativo')
    contagem_laboratorios.columns = ['Lote', 'Laboratorio', 'Quantitativo']

    if value == "Todos":
        contagem_laboratorios_filtrado = contagem_laboratorios
    else:
        contagem_laboratorios_filtrado = contagem_laboratorios.loc[contagem_laboratorios['Laboratorio'] == value, :]

    fig2 = px.bar(contagem_laboratorios_filtrado, x='Lote', y='Quantitativo', color='Laboratorio', title='', color_discrete_map=cores_laboratorios)
    fig2.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
        yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig2



@app.callback(
    [Output('qualidade_genomas_montados', 'figure'),
     Output('qualidade_resultados', 'figure'),
     Output('variantes_mensais', 'figure'),
     Output('quantitativo_variantes', 'figure'),
     Output('mapa_variantes', 'figure')],
    [Input('botao_lotes', 'value')]
)
def update_qua1(value):
    if value == "Todos":
        df_filtrado = df
    else:
        df_filtrado = df.loc[df['lote'] == value, :]

    qua1 = px.scatter(df_filtrado, x='profundidade_media', y='cobertura', color='qualidade', color_discrete_map=cores_qualidade)
    qua1.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
        yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    qua2 = px.scatter(df_filtrado, x='profundidade_media', y='cobertura', color='resultado', color_discrete_map=cores_resultado)
    qua2.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
        yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    df2 = df_filtrado[(df_filtrado['resultado'] == 'CONCLUSIVO') & (df_filtrado['melhor_repeticao'] == 'MELHOR REPETICAO')]
    contagem_variantes_linhagens_filt = df2.groupby(['variante', 'linhagem']).size().reset_index(name='Quantitativo')
    contagem_variantes_linhagens_filt.columns = ['Variante', 'Linhagem', 'Quantitativo']

    var1 = px.sunburst(contagem_variantes_linhagens_filt, path=['Variante', 'Linhagem'], values='Quantitativo', color='Variante', color_discrete_map=cores_variantes)
    var1.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        margin=dict(l=40, r=40, t=40, b=40),
        sunburstcolorway=["white"]
    )

    contagem_variantes_filt = df2.groupby(['mes_coleta', 'variante']).size().reset_index(name='Quantitativo')
    contagem_variantes_filt.columns = ['Periodo', 'Variantes', 'Quantitativo']

    hist = px.bar(contagem_variantes_filt, x='Periodo', y='Quantitativo', color='Variantes', title='', color_discrete_map=cores_variantes)
    hist.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        xaxis=dict(title='Período', color='cyan', gridcolor='gray'),
        yaxis=dict(title='Quantitativo de variantes', color='cyan', gridcolor='gray'),
        margin=dict(l=40, r=40, t=40, b=40))
    
    df_estados = df_filtrado.dropna(subset=['localidade_amostra'])
    df_estados = df_estados.groupby('estado').size().reset_index(name='quantidade')
    df_estados_completo = pd.DataFrame(todos_estados, columns=['estado'])
    df_estados_final = pd.merge(df_estados_completo, df_estados, on='estado', how='left')
    df_estados_final['quantidade'] = df_estados_final['quantidade'].fillna(0)

    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson = requests.get(geojson_url).json()
  
    fig_estados = px.choropleth(
        df_estados_final,
        geojson=geojson,
        locations='estado', 
        featureidkey='properties.sigla',
        color='quantidade',  
        hover_name='estado', 
        hover_data={'quantidade': True}, 
        color_continuous_scale=cores_estados)
    
    fig_estados.update_geos(
        fitbounds="locations", 
        visible=False,
        bgcolor='black',           
        lakecolor='black',         
        landcolor='black',         
        oceancolor='black')
    
    fig_estados.update_layout(
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='cyan'),
        margin=dict(l=40, r=40, t=40, b=40))
    
    fig_estados.update_coloraxes(
        colorbar_title="Quantitativo")
    
    return qua1, qua2, var1, hist, fig_estados

# ---------------------------------------------------------
# Run Server
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
