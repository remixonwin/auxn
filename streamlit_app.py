# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Auction Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample auction data
@st.cache_data
def load_auction_data():
    return pd.DataFrame({
        'id': range(1, 11),
        'title': [f"Auction {i}" for i in range(1, 11)],
        'category': ['Estate', 'Vehicle', 'Art', 'Estate', 'Industrial', 
                    'Jewelry', 'Vehicle', 'Estate', 'Art', 'Industrial'],
        'status': ['Live', 'Upcoming', 'Live', 'Ended', 'Live',
                  'Upcoming', 'Live', 'Upcoming', 'Live', 'Ended'],
        'items_count': [45, 1, 25, 120, 75, 10, 1, 85, 15, 50],
        'current_bid': [15000, 25000, 5000, 35000, 50000,
                       8000, 30000, 45000, 12000, 28000],
        'end_date': [(datetime.now() + timedelta(days=x)).strftime('%Y-%m-%d') 
                     for x in range(1, 11)],
        'lat': [40.7128, 34.0522, 41.8781, 29.7604, 39.9526,
                42.3601, 33.7490, 36.1627, 37.7749, 38.9072],
        'lon': [-74.0060, -118.2437, -87.6298, -95.3698, -75.1652,
                -71.0589, -84.3880, -86.7816, -122.4194, -77.0369],
        'location': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Philadelphia',
                    'Boston', 'Atlanta', 'Nashville', 'San Francisco', 'Washington DC']
    })

# Load data
auctions_df = load_auction_data()

# Sidebar filters
st.sidebar.header("Auction Filters")
status_filter = st.sidebar.multiselect(
    "Status",
    options=auctions_df['status'].unique(),
    default=auctions_df['status'].unique()
)

category_filter = st.sidebar.multiselect(
    "Category",
    options=auctions_df['category'].unique(),
    default=auctions_df['category'].unique()
)

# Main content
st.title("🔨 Auction Explorer")
st.markdown("Find auctions across the United States")

# Search bar
search = st.text_input("Search auctions...")

# Apply filters
filtered_auctions = auctions_df[
    (auctions_df['status'].isin(status_filter)) &
    (auctions_df['category'].isin(category_filter))
]

if search:
    filtered_auctions = filtered_auctions[
        filtered_auctions['title'].str.contains(search, case=False) |
        filtered_auctions['location'].str.contains(search, case=False)
    ]

# Map view
st.subheader("Auction Locations")
fig = px.scatter_mapbox(
    filtered_auctions,
    lat='lat',
    lon='lon',
    hover_name='title',
    hover_data=['status', 'category', 'items_count', 'current_bid'],
    color='status',
    size='items_count',
    size_max=15,
    zoom=3,
    center=dict(lat=39.8283, lon=-98.5795),  # Center of US
    mapbox_style='open-street-map'
)
st.plotly_chart(fig, use_container_width=True)

# Auction listings
st.subheader("Current Auctions")

# Generate random image URLs for demo purposes (replace with real auction images)
st.image("https://picsum.photos/800/400", caption="Featured Auction Items")
cols = st.columns(3)
for idx, auction in filtered_auctions.iterrows():
    with cols[idx % 3]:
        st.write("---")
        st.markdown(f"### {auction['title']}")
        # Display random auction image (replace with actual auction images)
        st.image(f"https://picsum.photos/400/300?random={auction['id']}", use_container_width=True)
        st.write(f"📍 {auction['location']}")
        st.write(f"📦 Items: {auction['items_count']}")
        st.write(f"💰 Current Bid: ${auction['current_bid']:,}")
        st.write(f"📅 Ends: {auction['end_date']}")
        
        status_color = {
            'Live': 'green',
            'Upcoming': 'blue',
            'Ended': 'red'
        }
        st.markdown(f"**Status:** :{status_color[auction['status']]}[{auction['status']}]")
        
        if auction['status'] == 'Live':
            st.button(f"Place Bid 🔨", key=f"bid_{auction['id']}")
        
        st.button(f"View Details", key=f"details_{auction['id']}")

# Footer
st.markdown("---")
st.markdown("Demo Auction Explorer - Built with Streamlit")