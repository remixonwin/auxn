import streamlit as st
from datetime import datetime, timedelta
import json
import os

# Initialize session states
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'items' not in st.session_state:
    st.session_state.items = [
        {
            'id': 1,
            'name': 'Vintage Watch',
            'description': 'Classic timepiece in excellent condition',
            'current_bid': 100.0,
            'min_increment': 10.0,
            'end_time': (datetime.now() + timedelta(hours=24)).isoformat(),
            'image_url': 'https://via.placeholder.com/150',
            'highest_bidder': None
        }
    ]

def validate_credentials(username, password):
    if len(username) < 3 or len(password) < 6:
        return False
    return True

def login_signup():
    with st.sidebar:
        st.header("Welcome")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with tab2:
            new_username = st.text_input("Choose Username", key="signup_user")
            new_password = st.text_input("Choose Password", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Sign Up"):
                if new_username in st.session_state.users:
                    st.error("Username already exists")
                elif not validate_credentials(new_username, new_password):
                    st.error("Username must be at least 3 characters and password at least 6 characters")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    st.session_state.users[new_username] = new_password
                    st.success("Account created! Please login.")

# Page configuration
st.set_page_config(page_title="Online Auction", layout="wide")

if not st.session_state.authenticated:
    login_signup()
else:
    st.title("🎈 Online Auction")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Active Auctions", "My Bids"])

    with tab1:
        try:
            # Display items in grid
            cols = st.columns(3)
            for idx, item in enumerate(st.session_state.items):
                with cols[idx % 3]:
                    st.image(item['image_url'], use_column_width=True)
                    st.subheader(item['name'])
                    st.write(item['description'])
                    
                    # Time remaining
                    end_time = datetime.fromisoformat(item['end_time'])
                    time_left = end_time - datetime.now()
                    
                    if time_left.total_seconds() > 0:
                        st.write(f"Time left: {time_left.seconds//3600}h {(time_left.seconds//60)%60}m")
                        
                        # Current bid and input
                        st.write(f"Current bid: ${item['current_bid']:.2f}")
                        st.write(f"Minimum increment: ${item['min_increment']:.2f}")
                        
                        new_bid = st.number_input(
                            "Your bid",
                            min_value=float(item['current_bid'] + item['min_increment']),
                            step=float(item['min_increment']),
                            key=f"bid_{item['id']}"
                        )
                        
                        if st.button("Place Bid", key=f"btn_{item['id']}"):
                            if new_bid >= item['current_bid'] + item['min_increment']:
                                item['current_bid'] = new_bid
                                item['highest_bidder'] = st.session_state.username
                                st.success(f"Bid placed successfully! Current bid: ${new_bid:.2f}")
                            else:
                                st.error("Bid must be higher than current bid + minimum increment")
                    else:
                        st.error("Auction ended")
                        if item['highest_bidder']:
                            st.write(f"Won by: {item['highest_bidder']}")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    with tab2:
        st.header("My Bids")
        my_bids = [item for item in st.session_state.items if item['highest_bidder'] == st.session_state.username]
        if my_bids:
            for bid in my_bids:
                st.write(f"Item: {bid['name']} - Current bid: ${bid['current_bid']:.2f}")
        else:
            st.info("You haven't placed any bids yet")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# Footer
st.markdown("---")
st.caption("© 2024 Online Auction Platform")
