import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd 
import numpy as np 
import plotly.graph_objs as go 

pd.options.plotting.backend = "plotly"

df = pd.read_csv('./FD_NAIS_2019.csv', delimiter=';', low_memory=False)
df = df.drop(labels=['ACCOUCHR', 'DEPDOM', 'DEPNAIS', 'SITUATMR', 'SITUATPR', 'TUCOM'], axis=1)

df_sex = pd.DataFrame({"Sexe":['Male', 'Femelle'], "Nombre":[385038, 368345], "Cat":["M", "F"]})
fig_sex = px.bar(df_sex, x='Sexe', y='Nombre', color='Cat', barmode='group')

fig_month = df['MNAIS'].value_counts().plot.area(title="Nombre de naissance en fonction du mois de l'année.", labels=dict(index='Mois', value='Nombre de naissance', variable='Naissances'))

fig_pie = px.pie(df['MNAIS'].value_counts(), values=df['MNAIS'].value_counts().values, labels=df['MNAIS'].value_counts().index, title='Répartition des Naissances en fonction du mois')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True


# Set the app.layout
app.layout = html.Div([dcc.Tabs(id='tabs', value='tab-1', children=[dcc.Tab(label='Tab one', value='tab-1'),
                dcc.Tab(label='Tab two', value='tab-2'),
                dcc.Tab(label='Tab Three', value='tab-3'),
                dcc.Tab(label='Tab Four', value='tab-4')]),html.Div(id='tabs-content')])

# Callback to control the tab content
@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(dash_table.DataTable(id='table-sorting-filtering', columns=[{'name':i, 'id':i, 'deletable':True} for i in df.columns],
                style_table={'overflowX':'scroll'}, style_cell={'height':'90', 'minWidth':'140px', 'width':'140px', 'maxWidth':'140px',
                'whiteSpace':'normal'}, page_current=0, page_size=50, page_action='custom', filter_action='custom', filter_query='', 
                sort_action='custom', sort_mode='multi', sort_by=[]))
    elif tab == 'tab-2':
        return html.Div([dcc.Graph(id='sex',figure=fig_sex)])
    elif tab == 'tab-3':
        return html.Div([dcc.Graph(id='month', figure=fig_month)])
    elif tab == 'tab-4':
        return html.Div([dcc.Graph(id='pie', figure=fig_pie)])

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                return name, operator_type[0].strip(), value
    return [None] * 3

@app.callback(Output('table-sorting-filtering', 'data'),[Input('table-sorting-filtering', "page_current"),Input('table-sorting-filtering', "page_size"),Input('table-sorting-filtering', 'sort_by'),Input('table-sorting-filtering', 'filter_query')])
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

        if len(sort_by):
            dff = dff.sort_values([col['column_id'] for col in sort_by],ascending=[col['direction'] == 'asc'for col in sort_by],inplace=False)

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)   