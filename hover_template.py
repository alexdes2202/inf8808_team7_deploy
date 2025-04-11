'''
    Provides the template for the tooltips.
'''

def age_distribution_hover(mode="Absolute"):
    '''
        Sets the template for the hover tooltips in the age distribution charts.

        The label displayed is either "Count" or "Percentage" depending on the selected mode.

        Args:
            mode: Display mode, either "Absolute" or "Relative"
        Returns:
            The hover template
    '''
    label = "Count" if mode == "Absolute" else "Percentage"
    value = "%{marker.size:.1f}" if mode == "Relative" else "%{marker.size:.0f}"
    return (
        "Year: %{x}<br>"
        "Age Group Midpoint: %{y}<br>"
        f"{label}: {value}<extra></extra>"
    )
    
    
def performance_sankey_hover(is_relative):
    '''
        Sets the hover template for the performance Sankey diagram.

        The tooltip shows country, medal type, and value (count or percentage).

        Args:
            is_relative: Whether the values shown are relative (percentage) or absolute (count)

        Returns:
            The hover template
    '''
    label = "Count" if is_relative == False else "Percentage"
    country = "%{customdata[1]}"
    medal_type = "%{customdata[0]}"
    value = "%{value:.0f}" if is_relative == False else "%{value:.1f}%"
    return (
        f"Country: {country}<br>"
        f"{label} : {value} ({medal_type})<extra></extra>"
    )
    
def source_sankey_hover(is_relative):
    '''
        Sets the hover template for the source (left side) nodes in the Sankey diagram.

        Displays the country name and either count or percentage based on the mode.

        Args:
            is_relative: Whether the values shown are relative (percentage) or absolute (count)

        Returns:
            The hover template
    '''
    label = "Count" if is_relative == False else "Percentage"
    country = "%{customdata}"
    value = "%{value:.0f}" if is_relative == False else "%{value:.1f}%"
    return (
        f"Country: {country}<br>"
        f"{label} : {value}<extra></extra>"
    )

def medal_distribution_hover():
    '''
        Sets the template for the hover tooltips in the medal distribution bubble chart.

        Displays the medal type, age group, and number of medalists.

        Returns:
            The hover template
    '''
    label = "Count"
    value = "%{marker.size:.0f}"
    return (
        "Medal: %{x}<br>"
        "Age Group: %{y}<br>"
        f"{label}: {value}<extra></extra>"
    )