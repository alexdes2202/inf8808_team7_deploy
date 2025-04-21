import plotly.graph_objects as go
import plotly.express as px
import preprocess.sport as sp
from style.theme import MALE, FEMALE

def connected_dot_plot(event_counts):
    '''
    Creates a connected dot plot to compare the number of men's and women's participations 
    for a sport's categories

    args:
        event_counts: The dataframe

    returns:
        fig5: The connected dot plot
    '''
    # Filter to include only events that have both men's and women's versions
    both_genders = event_counts[(event_counts["Men's"] > 0) & (event_counts["Women's"] > 0)]
    event_counts_melted = both_genders.melt(id_vars="Clean_Event", var_name="Gender", value_name="Count")
    event_counts_melted = event_counts_melted[event_counts_melted["Count"] > 0]

    # Create the base scatter plot
    fig5 = px.scatter(
        event_counts_melted,
        x="Count",
        y="Clean_Event",
        color="Gender",
        labels={"Clean_Event": "Event", "Count": "Number of Events"},
        color_discrete_map={"Men's": MALE, "Women's": FEMALE},
        symbol="Gender"
    )


    # Add lines between points to show the comparison between genders for each event
    for event in both_genders["Clean_Event"]:
        men_count = both_genders.loc[both_genders["Clean_Event"] == event, "Men's"].values[0]
        women_count = both_genders.loc[both_genders["Clean_Event"] == event, "Women's"].values[0]
        fig5.add_trace(go.Scatter(
            x=[men_count, women_count],
            y=[event, event],
            mode="lines",
            line=dict(color="gray", width=2, dash="dot"),
            showlegend=False
        ))

    # Customize layout: sizing, axis labels, font styling, and background
    fig5.update_layout(
        width=1000,
        height=700,
        yaxis_categoryorder="total ascending",
        xaxis_title="Number of Participants",
        yaxis_title="Category",
        legend_title=dict(
            text="Gender",
            font=dict(size=14)
        ),
        plot_bgcolor="#f0f0f0",
        paper_bgcolor="white",
        font=dict(size=14),
        xaxis=dict(
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            tickfont=dict(size=13),
            tickmode="array",
            tickvals=event_counts_melted["Clean_Event"].unique(),
        )

    )
    fig5.update_traces(marker=dict(size=10))

    return fig5

def connected_dot_plot_8(age_stats, age_stats_long, discipline):
    '''
    Creates a connected dot plot showing the age range (min to max) of athletes for each sport.
    The selected discipline is highlighted in red

    args:
        age_stats: The dataframe
        age_stats_long: The dataframe (long format)
        discipline: The selected sport

    returns:
        fig: The career length connected dot plot
    '''
    
    # Filter only relevant sports
    filtered_sports = [sport_.value for sport_ in sp.Sport]   
    age_stats = age_stats[age_stats['Sport'].isin(filtered_sports)].sort_values(by='Sport', ascending=False)
    age_stats_long = age_stats_long[age_stats_long['Sport'].isin(filtered_sports)].sort_values(by='Sport', ascending=False)
    
    # Create the base scatter plot for min and max ages
    fig = px.scatter(
        age_stats_long,
        x='Age (Years)',
        y='Sport',
        color='Age',
        symbol='Age',
        color_discrete_map={'Age_min': 'blue', 'Age_max': 'green'}
    )

    # Add dotted lines connecting min and max ages per sport
    for sport in age_stats['Sport']:
        subset = age_stats[age_stats['Sport'] == sport]
        if not subset.empty:
            min_val = subset['Age_min'].values[0]
            max_val = subset['Age_max'].values[0]
            # Highlight the selected discipline in red
            line_color = 'red' if sport.strip().lower() == discipline.strip().lower() else 'gray'
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[sport, sport],
                mode='lines',
                line=dict(color=line_color, dash='dot'),
                showlegend=False
            ))

    # Customize layout: size, template, and axis formatting
    fig.update_layout(
        xaxis_title='Age (Years)',
        yaxis_title='Sport',
        template='simple_white',
        width=1800,
        height=1000,
        yaxis=dict(
            tickmode='array',
        )
    )    
   
    return fig