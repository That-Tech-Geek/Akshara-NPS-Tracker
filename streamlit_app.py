import streamlit as st
import pandas as pd
import altair as alt
import datetime

# File to store ticket data
DATA_FILE = "tickets.csv"

# Function to load dataset from a file
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["ID", "Issue", "Status", "Priority", "Date Submitted"])

# Function to save dataset to a file
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Load dataset
if "df" not in st.session_state:
    st.session_state.df = load_data()

# Set page configuration
st.set_page_config(page_title="Akshara Support", page_icon="🎫")

# Frontend for adding a ticket
st.title("🎫 Akshara Support")
st.write("Submit a support ticket using the form below. Your ticket will be processed by the support team.")

# Add a new ticket form
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted:
    if not issue.strip():
        st.warning("Please describe the issue before submitting.")
    else:
        # Generate new ticket ID
        recent_ticket_number = (
            int(max(st.session_state.df["ID"], default="TICKET-1000").split("-")[1])
            if len(st.session_state.df) > 0
            else 1000
        )
        ticket_id = f"TICKET-{recent_ticket_number + 1}"
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        new_ticket = {
            "ID": ticket_id,
            "Issue": issue.strip(),
            "Status": "Open",
            "Priority": priority,
            "Date Submitted": today,
        }

        # Update the dataset
        st.session_state.df = pd.concat(
            [pd.DataFrame([new_ticket]), st.session_state.df], ignore_index=True
        )

        # Save data to file
        save_data(st.session_state.df)

        # Show a success message
        st.success(f"Ticket {ticket_id} submitted successfully!")

# Backend for managing tickets
st.title("🔒 Backend Dashboard")

# Password protection
password = st.text_input("Enter password to access backend:", type="password")
if password != st.secrets["ADMIN_PASSWORD"]:  # Replace with your secure password
    st.warning("Enter the correct password to access this section.")
    st.stop()

st.success("Access granted to backend dashboard!")

# Display and edit tickets
if not st.session_state.df.empty:
    st.header("Existing Tickets")
    st.write(f"Number of tickets: `{len(st.session_state.df)}`")
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Open", "In Progress", "Closed"],
                required=True,
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                required=True,
            ),
        },
        disabled=["ID", "Date Submitted"],
    )
    st.session_state.df = edited_df

    # Save changes to file
    save_data(st.session_state.df)

    # Show statistics
    st.header("Statistics")
    col1, col2 = st.columns(2)
    num_open_tickets = len(edited_df[edited_df["Status"] == "Open"])
    col1.metric("Open Tickets", num_open_tickets)
    col2.metric("Total Tickets", len(edited_df))

    # Visualize ticket data
    if len(edited_df) > 0:
        st.write("##### Ticket Status Distribution")
        status_plot = (
            alt.Chart(edited_df)
            .mark_bar()
            .encode(
                x="Status:N",
                y="count():Q",
                color="Status:N",
            )
        )
        st.altair_chart(status_plot, use_container_width=True)

        st.write("##### Ticket Priority Distribution")
        priority_plot = (
            alt.Chart(edited_df)
            .mark_pie()
            .encode(theta="count():Q", color="Priority:N")
        )
        st.altair_chart(priority_plot, use_container_width=True)
else:
    st.info("No tickets available.")
