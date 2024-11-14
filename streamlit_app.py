import streamlit as st
from datetime import datetime, timedelta

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'items' not in st.session_state:
    st.session_state.items = [{
        'id': 1,
        'name': 'Vintage Watch',
        'description': 'Classic timepiece in excellent condition',
        'current_bid': 100.0,
        'min_increment': 10.0,
        'end_time': (datetime.now() + timedelta(hours=24)).isoformat(),
        'image_url': 'https://via.placeholder.com/150',
        'highest_bidder': None
    }]

def validate_credentials(username, password):
    return len(username) >= 3 and len(password) >= 6

def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

def signup_user(username, password):
    if username not in st.session_state.users and validate_credentials(username, password):
        st.session_state.users[username] = password
        return True
    return False

def login_signup():
    with st.sidebar:
        st.header("Welcome")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if login_user(username, password):
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
        
        with tab2:
            new_username = st.text_input("Choose Username", key="signup_user")
            new_password = st.text_input("Choose Password", type="password", key="signup_pass")
            if st.button("Sign Up"):
                if signup_user(new_username, new_password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Invalid credentials or username taken")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.experimental_rerun()

def display_auctions():
    try:
        st.title("🎈 Online Auction")
        
        # Create tabs
        tab1, tab2 = st.tabs(["Active Auctions", "My Bids"])

        with tab1:
            if not st.session_state.items:
                st.info("No items available for auction")
                return

            cols = st.columns(3)
            for idx, item in enumerate(st.session_state.items):
                with cols[idx % 3]:
                    st.image(item['image_url'], use_column_width=True)
                    st.subheader(item['name'])
                    st.write(item['description'])
                    
                    try:
                        end_time = datetime.fromisoformat(item['end_time'])
                        time_left = end_time - datetime.now()
                        
                        if time_left.total_seconds() > 0:
                            st.write(f"Time left: {time_left.seconds//3600}h {(time_left.seconds//60)%60}m")
                            st.write(f"Current bid: ${item['current_bid']:.2f}")
                            
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
                                    st.success("Bid placed successfully!")
                                else:
                                    st.error("Bid too low")
                        else:
                            st.error("Auction ended")
                    except Exception as e:
                        st.error(f"Error displaying item: {str(e)}")

        with tab2:
            st.header("My Bids")
            if st.session_state.username:
                my_bids = [item for item in st.session_state.items 
                          if item.get('highest_bidder') == st.session_state.username]
                if my_bids:
                    for bid in my_bids:
                        st.write(f"Item: {bid['name']} - Your bid: ${bid['current_bid']:.2f}")
                else:
                    st.info("You haven't placed any bids yet")
            else:
                st.warning("Please login to see your bids")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        
# Main app flow
st.set_page_config(page_title="Online Auction", layout="wide")

if not st.session_state.authenticated:
    login_signup()
else:
    display_auctions()
    if st.sidebar.button("Logout"):
        logout()
