# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = None

# Page config
st.set_page_config(
    page_title="Auction Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sample auction data
@st.cache_data
def load_auction_data():
    # US State capitals data
    state_data = {
        'state': [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ],
        'city': [
            'Montgomery', 'Juneau', 'Phoenix', 'Little Rock', 'Sacramento', 'Denver', 'Hartford', 'Dover', 'Tallahassee', 'Atlanta',
            'Honolulu', 'Boise', 'Springfield', 'Indianapolis', 'Des Moines', 'Topeka', 'Frankfort', 'Baton Rouge', 'Augusta', 'Annapolis',
            'Boston', 'Lansing', 'St. Paul', 'Jackson', 'Jefferson City', 'Helena', 'Lincoln', 'Carson City', 'Concord', 'Trenton',
            'Santa Fe', 'Albany', 'Raleigh', 'Bismarck', 'Columbus', 'Oklahoma City', 'Salem', 'Harrisburg', 'Providence', 'Columbia',
            'Pierre', 'Nashville', 'Austin', 'Salt Lake City', 'Montpelier', 'Richmond', 'Olympia', 'Charleston', 'Madison', 'Cheyenne'
        ],
        'lat': [
            32.3792, 58.3019, 33.4484, 34.7465, 38.5816, 39.7392, 41.7658, 39.1582, 30.4383, 33.7490,
            21.3069, 43.6150, 39.7817, 39.7684, 41.5868, 39.0473, 38.2009, 30.4515, 44.3107, 38.9784,
            42.3601, 42.7325, 44.9537, 32.2988, 38.5767, 46.5891, 40.8258, 39.1638, 43.2081, 40.2206,
            35.6869, 42.6526, 35.7796, 46.8083, 39.9612, 35.4676, 44.9429, 40.2732, 41.8240, 34.0007,
            44.3683, 36.1627, 30.2672, 40.7608, 44.2601, 37.5407, 47.0379, 38.3498, 43.0731, 41.1399
        ],
        'lon': [
            -86.3077, -134.4197, -112.0740, -92.2896, -121.4944, -104.9903, -72.6734, -75.5244, -84.2807, -84.3880,
            -157.8583, -116.2023, -89.6501, -86.1581, -93.6250, -95.6752, -84.8733, -91.1871, -69.7795, -76.4922,
            -71.0589, -84.5555, -93.0900, -90.1848, -92.1735, -112.0391, -96.6852, -119.7674, -71.5376, -74.7699,
            -105.9372, -73.7562, -78.6382, -100.7837, -82.9988, -97.5164, -123.0351, -76.8867, -71.4128, -81.0348,
            -100.3510, -86.7816, -97.7431, -111.8910, -72.5754, -77.4360, -122.9007, -81.6326, -89.4012, -104.8202
        ]
    }
    
    # Generate random auction data for each state
    categories = ['Estate', 'Vehicle', 'Art', 'Industrial', 'Jewelry']
    statuses = ['Live', 'Upcoming', 'Ended']
    
    return pd.DataFrame({
        'id': range(1, 51),
        'title': [f"Auction in {city}" for city in state_data['city']],
        'category': [categories[i % len(categories)] for i in range(50)],
        'status': [statuses[i % len(statuses)] for i in range(50)],
        'items_count': [random.randint(1, 200) for _ in range(50)],
        'current_bid': [random.randint(5000, 100000) for _ in range(50)],
        'end_date': [(datetime.now() + timedelta(days=x)).strftime('%Y-%m-%d') 
                     for x in range(1, 51)],
        'lat': state_data['lat'],
        'lon': state_data['lon'],
        'location': [f"{city}, {state}" for city, state in zip(state_data['city'], state_data['state'])]
    })

# Load data
auctions_df = load_auction_data()

# Initialize surplus links
if 'surplus_links' not in st.session_state:
    st.session_state.surplus_links = {}
    try:
        with open('surplus_links.txt', 'r') as f:
            for line in f:
                state, link = line.strip().split(',')
                if state not in st.session_state.surplus_links:
                    st.session_state.surplus_links[state] = []
                if link not in st.session_state.surplus_links[state]:
                    st.session_state.surplus_links[state].append(link)
    except FileNotFoundError:
        pass

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

if st.session_state['current_page'] is None:
    # Main auction listings page
    st.subheader("Current Auctions")
    st.image("https://picsum.photos/800/400", caption="Featured Auction Items")
    
    cols = st.columns(3)
    for idx, auction in filtered_auctions.iterrows():
        with cols[idx % 3]:
            st.write("---")
            st.markdown(f"### {auction['title']}")
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
            
            state = auction['location'].split(', ')[1]
            if st.button(f"View {state} Details", key=f"details_{auction['id']}"):
                st.session_state['current_page'] = state
                st.rerun()

else:
    # State details page
    state = st.session_state['current_page']
    st.title(f"Auctions in {state}")
    
    if st.button("← Back to All Auctions"):
        st.session_state['current_page'] = None
        st.rerun()
    
    state_auctions = filtered_auctions[filtered_auctions['location'].str.endswith(state)]
    for _, auction in state_auctions.iterrows():
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        # Add link to Wikipedia for each state
        # Dictionary of state abbreviations to full names
        state_names = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
            'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
            'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
            'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New_Hampshire',
            'NJ': 'New_Jersey', 'NM': 'New_Mexico', 'NY': 'New_York', 'NC': 'North_Carolina',
            'ND': 'North_Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
            'RI': 'Rhode_Island', 'SC': 'South_Carolina', 'SD': 'South_Dakota', 'TN': 'Tennessee',
            'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
            'WV': 'West_Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
        }
        # Display all stored surplus links for this state
        # Always show the link submit box
        with st.form(key=f'surplus_form_{state}'):
            new_link = st.text_input("Add surplus auction link:")
            submit = st.form_submit_button("Submit")
            if submit and new_link:
                try:
                    # Get the page title
                    response = requests.get(new_link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_title = soup.title.string if soup.title else "Untitled Page"

                    if state not in st.session_state.surplus_links:
                        st.session_state.surplus_links[state] = []
                    if new_link not in st.session_state.surplus_links[state]:
                        st.session_state.surplus_links[state].append(new_link)
                        # Save to file with title
                        with open('surplus_links.txt', 'a') as f:
                            f.write(f"{state},{new_link},{page_title}\n")
                        st.success("Link added successfully!")
                except Exception as e:
                    st.error("Could not fetch page title. Please check the URL.")

        # Display existing surplus links
        if state in st.session_state.surplus_links and st.session_state.surplus_links[state]:
            st.markdown("### Surplus Auction Links:")
            for idx, link in enumerate(st.session_state.surplus_links[state], 1):
                st.markdown(f"{idx}. [{state} Surplus Auction #{idx}]({link})")

        # Add basic state info link
        full_state_name = state_names[state]
        with col1:
            # Use state capitol images instead of random images
            state = auction['location'].split(', ')[1]
            capitol_image = f"https://placehold.co/400x300/lightgray/darkgray?text={state}+Capitol"
            st.markdown(f"[![{state} State Capitol]({capitol_image})](https://en.wikipedia.org/wiki/{full_state_name})")
            st.caption(f"{state} State Capitol")

        
        with col2:
            st.markdown(f"### {auction['title']}")
            st.write(f"📍 {auction['location']}")
            st.write(f"Category: {auction['category']}")
            st.write(f"Items: {auction['items_count']}")
            st.write(f"Current Bid: ${auction['current_bid']:,}")
            st.write(f"Ends: {auction['end_date']}")
            
            if auction['status'] == 'Live':
                st.button(f"Place Bid 🔨", key=f"state_bid_{auction['id']}")

# Footer
st.markdown("---")
