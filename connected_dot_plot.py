import plotly.graph_objects as go
import plotly.express as px

def connected_dot_plot(event_counts, discipline):
    both_genders = event_counts[(event_counts["Men's"] > 0) & (event_counts["Women's"] > 0)]
    event_counts_melted = both_genders.melt(id_vars="Clean_Event", var_name="Gender", value_name="Count")
    event_counts_melted = event_counts_melted[event_counts_melted["Count"] > 0]

    # Creating the scatter plot
    fig5 = px.scatter(
        event_counts_melted,
        x="Count",
        y="Clean_Event",
        color="Gender",
        title=f"Number of Men's and Women's Participations in {discipline}",
        labels={"Clean_Event": "Event", "Count": "Number of Events"},
        color_discrete_map={"Men's": "blue", "Women's": "pink"},
        symbol="Gender"
    )


    # Adding lines between points to show the comparison between genders for each event
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

    # Configuring the layout of the plot
    fig5.update_layout(
        width=1000,
        height=700,
        yaxis_categoryorder="total ascending",
        xaxis_title="Number of Participants",
        yaxis_title="Category",
        legend_title="Gender",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=14),
        yaxis=dict(
            tickmode="array",
            tickvals=event_counts_melted["Clean_Event"].unique(),
        )
    )

    return fig5
