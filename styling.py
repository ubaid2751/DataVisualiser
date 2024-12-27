def get_styling_instructions(user_input):
    """
    Generate styling instructions based on the user's input query.
    """
    if "pie chart" in user_input.lower():
        return """
        - Use a pastel color palette for the slices.
        - Display percentage values inside each slice in bold text.
        - Add a legend at the bottom, aligned horizontally.
        - Include a title centered above the chart.
        - Use slight 3D shading for a modern look.
        """
    elif "bar chart" in user_input.lower():
        return """
        - Use vibrant colors like blue, green, and orange for the bars.
        - Include gridlines for both axes in light gray.
        - Add value labels above each bar.
        - Set the background to light gray for better contrast.
        - Ensure bars have rounded corners for a polished look.
        """
    elif "scatter plot" in user_input.lower():
        return """
        - Use a black background for better contrast.
        - Scatter points should vary in size based on value.
        - Assign distinct colors to each category using a pastel palette.
        - Enable hover functionality to display details for each point.
        - Include gridlines in light gray for readability.
        """
    elif "line chart" in user_input.lower():
        return """
        - Use a white background with blue lines.
        - Add markers at each data point.
        - Use smooth curves instead of sharp edges.
        - Include gridlines and labels for both axes.
        - Make the chart interactive with zoom and pan features.
        """
    elif "correlation" in user_input.lower():
        return """
        - Use a diverging color palette from blue (low) to red (high).
        - Annotate each cell with its value.
        - Add a color bar to the side to indicate the scale.
        - Keep gridlines subtle for a clean look.
        - Ensure axis labels are rotated for better readability.
        """
    else:
        return """
        - Use a clean and minimalist design.
        - Use distinct colors for clarity.
        - Add appropriate axis labels and titles.
        - Include interactivity features like hover and zoom.
        - Ensure the visualization is visually appealing and easy to read.
        """