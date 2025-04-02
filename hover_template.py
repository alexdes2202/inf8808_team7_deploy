'''
    Provides the template for the tooltips.
'''

def age_distribution_hover(mode="Absolute"):
    label = "Count" if mode == "Absolute" else "Percentage"
    value = "%{marker.size:.1f}" if mode == "Relative" else "%{marker.size:.0f}"
    return (
        "Year: %{x}<br>"
        "Age Group Midpoint: %{y}<br>"
        f"{label}: {value}<extra></extra>"
    )
    
    
def performance_sankey_hover(is_relative):
    label = "Count" if is_relative == False else "Percentage"
    country = "%{customdata[1]}"
    medal_type = "%{customdata[0]}"
    value = "%{value:.0f}" if is_relative == False else "%{value:.1f}%"
    return (
        f"Country: {country}<br>"
        f"{label} : {value} ({medal_type})<extra></extra>"
    )
    
def source_sankey_hover(is_relative):
    label = "Count" if is_relative == False else "Percentage"
    country = "%{customdata}"
    value = "%{value:.0f}" if is_relative == False else "%{value:.1f}%"
    return (
        f"Country: {country}<br>"
        f"{label} : {value}<extra></extra>"
    )

def medal_distribution_hover():
    label = "Count"
    value = "%{marker.size:.0f}"
    return (
        "Medal: %{x}<br>"
        "Age Group: %{y}<br>"
        f"{label}: {value}<extra></extra>"
    )