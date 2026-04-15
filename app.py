st.subheader("🌞 Sales Hierarchy (Sunburst)")

fig = px.sunburst(
    df,
    path=['Country', 'Description'],
    values='TotalPrice',
    title="Sales Distribution"
)

st.plotly_chart(fig, use_container_width=True)
