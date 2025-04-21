import plotly.graph_objs as go

def visualize_data(data):
    '''
        Creates a grouped bar chart with medal percentage breakdowns by participation number.
        Each group displays gold, silver, and bronze medal percentages in a podium effect

        args:
            data: The dataframe

        returns:
            fig: The grouped bar chart
    '''

    traces = []
    
    for index, row in data.iterrows():
        # Extract medal percentages and rank them from highest to lowest
        percentages = {
            'Gold': row['Gold_Percentage'],
            'Silver': row['Silver_Percentage'],
            'Bronze': row['Bronze_Percentage']
        }
        sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        first, second, third = sorted_percentages
        
        # Assign x-axis position shifts to group bars based on ranking
        x_positions = {
            first[0]: 1,
            second[0]: 0,
            third[0]: 2
            }

        # Create one bar trace per medal type for the current participation group
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

        # Add emoji annotations above each bar to represent medal types
        medal_emojis = {
            'Gold': '🏅',
            'Silver': '🥈',
            'Bronze': '🥉'
        }

        for medal, _ in zip(['Gold', 'Silver', 'Bronze'], [first, second, third]):
            traces.append(
                go.Scatter(
                    x=[row['Participation_Number'] + x_positions[medal] * 0.2],
                    y=[percentages[medal] + 0.2],
                    text=[medal_emojis[medal]],
                    mode="text",
                    showlegend=False
                )
            )

    # Set up the chart layout and styling
    layout = go.Layout(
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

    fig.add_traces(
        traces
    )
    
    return fig