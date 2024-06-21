#pip install dash
#pip install pandas
#pip install openpyxl

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#--------------------------------------------------------
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.cbook as cbook
import seaborn as sns
import dash_bootstrap_components as dbc
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
import requests

#Aplicativo do Flask
app = Dash(__name__, external_stylesheets=['./static/css/style.css']) 

#Base de dados
df = pd.read_excel("./database/ACMELab-SC2-Seq.xlsx")

#--------------------------------------------------------
#Sub-databases
#--------------------------------------------------------
#Repetições
contagem_repeticao = df.groupby(['lote', 'melhor_repeticao']).size().reset_index(name='Quantitativo')
contagem_repeticao.columns = ['Lote', 'Melhor repetição', 'Quantitativo']

#Laboratórios
contagem_laboratorios = df.groupby(['lote', 'laboratorio']).size().reset_index(name='Quantitativo')
contagem_laboratorios.columns = ['Lote', 'Laboratorio', 'Quantitativo']

#Remover as inconclusivas + variantes e linhagens
df2 = df[(df['resultado'] == 'CONCLUSIVO') & (df['melhor_repeticao'] == 'MELHOR REPETICAO')]

#Contagem de variantes por tempo
contagem_variantes = df2.groupby(['mes_coleta', 'variante']).size().reset_index(name='Quantitativo')
contagem_variantes.columns = ['Periodo', 'Variantes', 'Quantitativo']

#---------------------------------------------------------


#--------------------------------------------------------
#Cores
#--------------------------------------------------------
cores_repeticao = {
    "MELHOR REPETICAO": "#008744",
    "PIOR REPETICAO": "#d62d20",
    "CONTROLE": "#673888"}


cores_laboratorios = {
    "CENTRO DE HEMATOLOGIA E HEMOTERAPIA DO CEARA (HEMOCE)": "#cc2a36",
    "UNIDADE DE APOIO AO DIAGNOSTICO DA COVID 19 (UNADIG)": "#00a0b0",
    "LABORATORIO CENTRAL DE SAUDE PUBLICA (LACEN)": "#bcd42a",
    "LABORATORIO ARGOS (ARGOS)": "#6a329f"}

cores_qualidade = {
    "GOOD": "#88d8b0",
    "MEDIOCRE": "#ffcc5c",
    "BAD": "#ff6f69"}

cores_variantes = {
    "OUTRAS": "#8b9dc3",
    "VOI ZETA (P.2-LIKE)": "#d3a625",
    "VOC GAMA (P.1-LIKE)": "#005b96",    
    "VOC DELTA (B.1.617.2-LIKE)": "#008080",
    "VOC OMICRON (BA.1-LIKE)": "#be29ec"  }

cores_estados = [0, 'rgb(240,240,240)'], [0.1, 'rgb(200,200,200)'], [1, 'rgb(0,0,255)']

cores_resultado = {
    "CONCLUSIVO": "#05d9e8",
    "INCONCLUSIVO": "#ff2a6d",
    "CONTROLE": "#d1f7ff"}
#---------------------------------------------------------

# -------------------------------
#Mapa
# -------------------------------
todos_estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 
                 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
                 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
                 'SP', 'SE', 'TO']

df_etados = df.dropna(subset=['localidade_amostra'])
df_etados = df_etados.groupby('estado').size().reset_index(name='quantidade')

df_estados_completo = pd.DataFrame(todos_estados, columns=['estado'])

df_etados_final = pd.merge(df_estados_completo, df_etados, on='estado', how='left')
df_etados_final['quantidade'] = df_etados_final['quantidade'].fillna(0)


geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson = requests.get(geojson_url).json()

# Criar o mapa coroplético
fig_estados = px.choropleth(
    df_etados_final,
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


# -------------------------------
#Histograma do período
# -------------------------------
hist = px.bar(contagem_variantes, x='Periodo', y='Quantitativo', color='Variantes', title='', color_discrete_map=cores_variantes)
hist.update_layout(
    showlegend=False,
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='cyan'),
    xaxis=dict(title='Período', color='cyan', gridcolor='gray'),
    yaxis=dict(title='Quantitativo de variantes', color='cyan', gridcolor='gray'),
    margin=dict(l=40, r=40, t=40, b=40))

# -------------------------------
#Listas para botões
# -------------------------------
repe = list(contagem_repeticao["Melhor repetição"].unique())
repe.append("Todos")

labs = list(contagem_laboratorios["Laboratorio"].unique())
labs.append("Todos")

lotes = list(df["lote"].unique())
lotes.append("Todos")

varlin = list(df2["lote"].unique())
varlin.append("Todos")

# -------------------------------




# -------------------------------
#Layout
# -------------------------------
#Quantitativo
app.layout = html.Div(children=[
    html.Div(children=[html.H1(children='ACMELab dashboard')], className='centered-container'),

    html.Div(children=[
        html.Div(children=[
            html.H1(children='Quantitativo de sequenciamentos'),
            dcc.Dropdown(repe, value='Todos', id='Botão repetições'),  
            dcc.Graph(id='Quantitativo de repetições')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div(children=[
            html.H1(children='Origem das amostras'),
            dcc.Dropdown(labs, value='Todos', id='Botão laboratórios'), 
            dcc.Graph(id='Quantitativo de laboratórios')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),


    #Qualidade
    html.H1(children='Qualidade dos sequenciamentos'),
    dcc.Dropdown(lotes, value='Todos', id='Lotes'), 
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='Qualidade dos genomas montados')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div(children=[
            dcc.Graph(id='Qualidade dos resultados')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    

    #Linhagens
    html.H1(children='Linhagens sequenciadas'),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id="Variantes mensais", figure = hist)
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div(children=[
            dcc.Dropdown(varlin, value='Todos', id='qualidade'), 
            dcc.Graph(id='Quantitativo de variantes')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
    #Mapa colorimétrico
    html.H1(children='Quantitativo estadual por coleta'),
    dcc.Graph(id="Mapa de coletas", figure = fig_estados)])



#---------------------------------------------
#APLICAÇÃO
#---------------------------------------------
@app.callback(
    Output('Quantitativo de repetições', 'figure'),
    Input('Botão repetições', 'value'))

def update_fig1(value):
    if value == "Todos":
        fig1 = px.bar(contagem_repeticao, x='Lote', y='Quantitativo', color='Melhor repetição', title='', color_discrete_map=cores_repeticao)
        fig1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40))

    else:
        contagem_repeticao_filtrado = contagem_repeticao.loc[contagem_repeticao['Melhor repetição'] == value, :]

        fig1 = px.bar(contagem_repeticao_filtrado, x='Lote', y='Quantitativo', color='Melhor repetição', title='', color_discrete_map=cores_repeticao)
        fig1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40))
    return fig1

@app.callback(
    Output('Quantitativo de laboratórios', 'figure'),
    Input('Botão laboratórios', 'value'))

def update_fig2(value):
    if value == "Todos":
        fig2 = px.bar(contagem_laboratorios, x='Lote', y='Quantitativo', color='Laboratorio', title='', color_discrete_map=cores_laboratorios)
        fig2.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40))
    else:
        contagem_laboratorios_filtrado = contagem_laboratorios.loc[contagem_laboratorios['Laboratorio'] ==  value, :]

        fig2 = px.bar(contagem_laboratorios_filtrado, x='Lote', y='Quantitativo', color='Laboratorio', title='', color_discrete_map=cores_laboratorios)
        fig2.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Lote', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Quantitativo', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40))    
    return fig2


@app.callback(
    [Output('Qualidade dos genomas montados', 'figure'),
     Output('Qualidade dos resultados', 'figure')],
    [Input('Lotes', 'value')])

def update_qua1(value):
    if value == "Todos":
        qua1 = px.scatter(df, x='profundidade_media', y='cobertura', color='qualidade', color_discrete_map=cores_qualidade)
        qua1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40))  
        
        qua2 = px.scatter(df, x='profundidade_media', y='cobertura', color='resultado', color_discrete_map=cores_resultado)
        qua2.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40)) 
    else:
        df_filtrado = df.loc[df['lote'] ==  value, :]

        qua1 = px.scatter(df_filtrado, x='profundidade_media', y='cobertura', color='qualidade', color_discrete_map=cores_qualidade)
        qua1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40)) 
        
        qua2 = px.scatter(df_filtrado, x='profundidade_media', y='cobertura', color='resultado', color_discrete_map=cores_resultado)
        qua2.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40)) 
    return qua1, qua2

@app.callback(
    Output('Quantitativo de variantes', 'figure'),
    Input('qualidade', 'value'))

def update_qua2(value):
    if value == "Todos":
        contagem_variantes_linhagens = df2.groupby(['variante', 'linhagem']).size().reset_index(name='Quantitativo')
        contagem_variantes_linhagens.columns = ['Variante', 'Linhagem', 'Quantitativo']

        var1 = px.sunburst(contagem_variantes_linhagens, path=['Variante', 'Linhagem'], values='Quantitativo', color='Variante', color_discrete_map=cores_variantes)
        var1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40),
                sunburstcolorway=["white"]) 
    else:
        df2_filtrado = df2.loc[df2['lote'] ==  value, :]

        contagem_variantes_linhagens_filt = df2_filtrado.groupby(['variante', 'linhagem']).size().reset_index(name='Quantitativo')
        contagem_variantes_linhagens_filt.columns = ['Variante', 'Linhagem', 'Quantitativo']

        var1 = px.sunburst(contagem_variantes_linhagens_filt, path=['Variante', 'Linhagem'], values='Quantitativo', color='Variante', color_discrete_map=cores_variantes)
        var1.update_layout(
                showlegend=False,
                paper_bgcolor='black',
                plot_bgcolor='black',
                font=dict(color='cyan'),
                xaxis=dict(title='Profundidade média', color='cyan', gridcolor='gray'),
                yaxis=dict(title='Cobertura genômica', color='cyan', gridcolor='gray'),
                margin=dict(l=40, r=40, t=40, b=40)) 
    return var1

#------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)