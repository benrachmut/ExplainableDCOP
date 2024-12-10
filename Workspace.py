import plotly.graph_objects as go

# Sample data for multiple curves
x = [1, 2, 3, 4, 5]
y1 = [10, 20, 30, 40, 50]
y2 = [15, 25, 35, 45, 55]
y3 = [5, 15, 25, 35, 45]

info1 = ["Curve 1 - A", "Curve 1 - B", "Curve 1 - C", "Curve 1 - D", "Curve 1 - E"]
info2 = ["Curve 2 - A", "Curve 2 - B", "Curve 2 - C", "Curve 2 - D", "Curve 2 - E"]
info3 = ["Curve 3 - A", "Curve 3 - B", "Curve 3 - C", "Curve 3 - D", "Curve 3 - E"]

# Create the figure
fig = go.Figure()

# Add the first curve
fig.add_trace(go.Scatter(
    x=x, y=y1,
    mode='lines+markers',
    hovertemplate='<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Info:</b> %{text}',
    text=info1,
    name='Curve 1'
))

# Add the second curve
fig.add_trace(go.Scatter(
    x=x, y=y2,
    mode='lines+markers',
    hovertemplate='<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Info:</b> %{text}',
    text=info2,
    name='Curve 2'
))

# Add the third curve
fig.add_trace(go.Scatter(
    x=x, y=y3,
    mode='lines+markers',
    hovertemplate='<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Info:</b> %{text}',
    text=info3,
    name='Curve 3'
))

# Customize the layout
fig.update_layout(
    title="Interactive Graph with Multiple Curves",
    xaxis_title="X-Axis",
    yaxis_title="Y-Axis",
    template="plotly_white",
    legend_title="Curves"
)

# Show the figure
fig.show()
