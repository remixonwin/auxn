import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# Basic page config
st.set_page_config(page_title="Auction Explorer", layout="wide")

# Generate sample data
@st.cache_data
def load_auction_data():
    states = ['CA', 'NY', 'TX', 'FL', 'IL']  # Reduced to 5 states
    cities = ['Sacramento', 'Albany', 'Austin', 'Tallahassee', 'Springfield']
    lats = [38.5816, 42.6526, 30.2672, 30.4383, 39.7817]
    lons = [-121.4944, -73.7562, -97.7431, -84.2807, -89.6501]
    
    return pd.DataFrame({
        'title': [f"Auction in {city}" for city in cities],
        'category': ['Estate', 'Vehicle', 'Art', 'Industrial', 'Jewelry'],
        'status': ['Live', 'Upcoming', 'Ended', 'Live', 'Upcoming'],
        'items_count': [random.randint(1, 100) for _ in range(5)],
        'current_bid': [random.randint(5000, 50000) for _ in range(5)],
        'end_date': [(datetime.now() + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, 6)],
        'lat': lats,
        'lon': lons,
        'location': [f"{city}, {state}" for city, state in zip(cities, states)]
    })

# Load data and create filters
auctions_df = load_auction_data()
status_filter = st.sidebar.multiselect("Status", auctions_df['status'].unique(), default=auctions_df['status'].unique())
category_filter = st.sidebar.multiselect("Category", auctions_df['category'].unique(), default=auctions_df['category'].unique())

# Main content
st.title("🔨 Auction Explorer")
filtered_auctions = auctions_df[
    (auctions_df['status'].isin(status_filter)) &
    (auctions_df['category'].isin(category_filter))
]

# Map
fig = px.scatter_mapbox(
    filtered_auctions,
    lat='lat', lon='lon',
    hover_name='title',
    color='status',
    size='items_count',
    zoom=3,
    center=dict(lat=39.8283, lon=-98.5795),
    mapbox_style='open-street-map'
)
st.plotly_chart(fig, use_container_width=True)

# Auction listings
cols = st.columns(3)
for idx, auction in filtered_auctions.iterrows():
    with cols[idx % 3]:
        st.markdown(f"### {auction['title']}")
        st.write(f"📍 {auction['location']}")
        st.write(f"💰 ${auction['current_bid']:,}")
        st.write(f"📅 {auction['end_date']}")
        if auction['status'] == 'Live':
            st.button(f"Bid 🔨", key=f"bid_{idx}")
