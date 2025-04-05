import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

def visualize_data(data, sport):

    x_offsets = {
        'Gold' : -0.2,
        'Silver' : 0,
        'Bronze' : 0.2
            }

    traces = []
    for index, row in data.iterrows():

        percentages = {
            'Gold': row['Gold_Percentage'],
            'Silver': row['Silver_Percentage'],
            'Bronze': row['Bronze_Percentage']
        }


        sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        first, second, third = sorted_percentages
        
        #ordre de l'axe des x
        x_positions = {
            first[0]: 1,
            second[0]: 0,
            third[0]: 2
            }

        participation_traces = [
            go.Bar(
                y=[percentages[medal]],
                x=[row['Participation_Number'] + x_positions[medal] * 0.2],
                name=medal,
                marker=dict(color={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'}[medal]),
                showlegend=True if index == 0 else False,
                hovertemplate="Participation: %{x:.0f}<br><span style='display:block; text-align:center;'><b>%{y:.2f}%</b></span><extra></extra>"

            ) for medal, _ in sorted_percentages
            ]
        traces.extend(participation_traces)

        medal_emojis = {
            'Gold': '🏅',
            'Silver': '🥈',
            'Bronze': '🥉'
        }

        for medal, pos in zip(['Gold', 'Silver', 'Bronze'], [first, second, third]):
            traces.append(
                go.Scatter(
                    x=[row['Participation_Number'] + x_positions[medal] * 0.2],
                    y=[percentages[medal] + 0.2],
                    text=[medal_emojis[medal]],
                    mode="text",
                    showlegend=False
                )
            )

    layout = go.Layout(
        title="Podium of Gold, Silver, and Bronze Winning Chances per Participation (Swimming)",
        xaxis=dict(
            title="Participation Number",
            tickvals=data['Participation_Number'],
            ticktext=data['Participation_Number'].astype(str),
            range=[0.5, 4.5]
        ),
        yaxis=dict(title="Percentage (%)"),
        barmode="group",
        bargap=0.0,
        bargroupgap=0
        )

    fig = go.Figure(layout=layout)

    #color_map = ['gold', 'silver', '#cd7f32']

    fig.add_traces(
        traces
    )

    #fig.show()
    return fig