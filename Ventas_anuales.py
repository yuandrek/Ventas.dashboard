

from dash import Dash, dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_auth
import pandas as pd

app = Dash()

usersAuth = [['vsanchez', '7005'], ['crojas', '1024']]
auth = dash_auth.BasicAuth(app, usersAuth)
server = app.server


df_ventas = pd.read_excel('Ventas.xlsx', sheet_name="Detalle")
df_ventasAcum = pd.read_excel('Ventas.xlsx', sheet_name="Acumulado")

mapbox_token = "pk.eyJ1IjoiaXZhbmxvc2FyIiwiYSI6ImNrZTJpdWN0NDA5cXUyem1oOGx3NGh1bGsifQ.wuhB2vmk4QGrciFWYygqaA"

# Visualización total de ventas a nivel de país

fig_mapa= go.Figure(go.Scattermapbox(
    lat = df_ventasAcum['Latitud'],
    lon = df_ventasAcum['Longitud'],
    mode='markers',
    text= df_ventasAcum['Suma Ingresos'],
    marker=go.scattermapbox.Marker(
        size=df_ventasAcum['Suma Ingresos']/40000,
        color=df_ventasAcum['Suma Ingresos']/40000
    )
))


fig_mapa.update_layout(
    autosize=True,
    hovermode='closest',
    title='Total de Ventas',
    mapbox=dict(
        accesstoken=mapbox_token,
        bearing=0,
        center=dict(
            lat=40.41,
            lon=-3.7
        ),
        pitch=0,
        zoom=2
    ),
)


app.layout = html.Div([

                html.Div([
                    html.Label('Rango de fechas'),
                    dcc.DatePickerRange(id='selector_fecha',start_date=df_ventas["Fecha compra"].min(),end_date=df_ventas["Fecha compra"].max())
                    ],style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
                
                html.Div([
                html.Label('País'),
                dcc.Dropdown(id='selector',
                    options=[{'label': i, 'value': i} for i in df_ventas['País'].unique()],
                    value='Germany'
                    )],style={'width': '45%', 'display': 'inline-block'}),


                html.Div([
                    dcc.Graph(id='barplot_ventas_seg')
                    ],style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),

                html.Div([
                    dcc.Graph(id='barplot_beneficio_cat')
                    ],style={'width': '33%', 'float': 'center', 'display': 'inline-block'}),

                html.Div([
                    dcc.Graph(id='lineplot_pedidos')
                    ],style={'width': '33%', 'float': 'right', 'display': 'inline-block'}),

                html.Div([
                        dcc.Graph(id='mapa_ventas', figure=fig_mapa)],
                        style={'width': '100%'})
])


# Actualiza gráfico de Ventas por Segmento

@app.callback(Output('barplot_ventas_seg', 'figure'),
    [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('selector', 'value')])

def actualizar_graph_ventas(fecha_min, fecha_max, seleccion):
    
    df_filtered = df_ventas[(df_ventas["Fecha compra"]>=fecha_min) & (df_ventas["Fecha compra"]<=fecha_max) & (df_ventas["País"]==seleccion)]
    df_agrupado = df_filtered.groupby("Segmento")["Importe"].agg("sum").to_frame(name = "Ingresos").reset_index()

    return{
        'data': [go.Bar(x=df_agrupado["Segmento"],
                        y=df_agrupado["Ingresos"])
                ],
        'layout': go.Layout(
            title="Ventas en cada Segmento de clientes",
            xaxis={'title': "Segmento"},
            yaxis={'title': "Total de Ingresos"},
            hovermode='closest'
        )}


# Actualiza gráfico de Ganancias por Categoría

@app.callback(Output('barplot_beneficio_cat', 'figure'),
    [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('selector', 'value'),Input('barplot_ventas_seg', 'hoverData')])

def actualizar_graph_beneficio(fecha_min, fecha_max, seleccion, hoverData):
    # Interactividad inter-gráfico hoverData
    index_hD = hoverData['points'][0]['x']
    
    filtered_df = df_ventas[(df_ventas["Fecha compra"]>=fecha_min) & (df_ventas["Fecha compra"]<=fecha_max) & (df_ventas["País"]==seleccion) & (df_ventas["Segmento"]==index_hD)]
    df_agrupado = filtered_df.groupby("Categoría")["Beneficio"].agg("sum").to_frame(name = "Beneficio").reset_index()

    return{
        'data': [go.Bar(x=df_agrupado["Categoría"],
                        y=df_agrupado["Beneficio"]
                        )],
        'layout': go.Layout(
            title="Ganancias por Categoría",
            xaxis={'title': "Categoría"},
            yaxis={'title': "Total de Beneficios"},
            hovermode='closest')}


# Actualiza gráfico de evolución cantidad de Pedidos en función del País y Fechas seleccionadas

@app.callback(Output('lineplot_pedidos', 'figure'),
    [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('selector', 'value'),Input('barplot_ventas_seg', 'hoverData')])

def actualizar_graph_pedidos(fecha_min, fecha_max, seleccion, hoverData):
    # Interactividad inter-gráfico hoverData
    index_hD = hoverData['points'][0]['x']
    
    filtered_df = df_ventas[(df_ventas["Fecha compra"]>=fecha_min) & (df_ventas["Fecha compra"]<=fecha_max) & (df_ventas["País"]==seleccion) & (df_ventas["Segmento"]==index_hD)]
    df_agrupado = filtered_df.groupby("Fecha compra")["Cantidad"].agg("sum").to_frame(name = "Cantidad").reset_index()

    return{
        'data': [go.Scatter(x=df_agrupado["Fecha compra"],
                            y=df_agrupado["Cantidad"],
                            mode="lines+markers"
                            )],
        'layout': go.Layout(
            title="Evolución de Cantidad de Pedidos solicitados",
            xaxis={'title': "Fecha"},
            yaxis={'title': "Cantidad"},
            hovermode='closest')}


if __name__ == '__main__':
    app.run_server(port=8000)