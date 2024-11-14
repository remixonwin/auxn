import streamlit as st
from datetime import datetime, timedelta

# Initialize session state
if 'items' not in st.session_state:
    st.session_state.items = [
        {
            'id': 1,
            'name': 'Vintage Watch',
            'description': 'Classic timepiece in excellent condition',
            'current_bid': 100,
            'min_increment': 10,
            'end_time': datetime.now() + timedelta(hours=24),
            'image_url': 'https://via.placeholder.com/150'
        }
    ]

# Page config
st.set_page_config(page_title="Online Auction", layout="wide")

# Main header
st.title("🎈 Online Auction")

# Create tabs
tab1, tab2 = st.tabs(["Active Auctions", "My Bids"])

with tab1:
    # Display items in grid
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.items):
        with cols[idx % 3]:
            st.image(item['image_url'], use_column_width=True)
            st.subheader(item['name'])
            st.write(item['description'])
            
            # Time remaining
            time_left = item['end_time'] - datetime.now()
            st.write(f"Time left: {time_left.seconds//3600}h {(time_left.seconds//60)%60}m")
            
            # Current bid and input
            st.write(f"Current bid: ${item['current_bid']}")
            new_bid = st.number_input(
                "Your bid",
                min_value=item['current_bid'] + item['min_increment'],
                step=item['min_increment'],
                key=f"bid_{item['id']}"
            )
            
            if st.button("Place Bid", key=f"btn_{item['id']}"):
                if new_bid >= item['current_bid'] + item['min_increment']:
                    item['current_bid'] = new_bid
                    st.success(f"Bid placed successfully! Current bid: ${new_bid}")
                else:
                    st.error("Bid must be higher than current bid + minimum increment")

with tab2:
    st.info("Coming soon: Track your bidding history here!")

# Footer
st.markdown("---")
st.caption("© 2024 Online Auction Platform")
