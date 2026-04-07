import streamlit as st
import requests

BASE_URL = "http://localhost:6000"

st.set_page_config(layout="wide")

# =========================
# SESSION STATE INIT
# =========================
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None


# =========================
# SIDEBAR (AUTH PANEL)
# =========================
with st.sidebar:
    st.title("Authentication")

    tab1, tab2 = st.tabs(["Login", "Demo Users"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(
                f"{BASE_URL}/token",
                json={"username": username, "password": password}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["access_token"]
                st.session_state.user = username
                st.session_state.role = data["role"]
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

    with tab2:
        st.write("user / pass")
        st.write("admin / admin")

    if st.session_state.user:
        st.success(f"Welcome, {st.session_state.user}")

    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.role = None


# =========================
# MAIN AREA
# =========================
st.title("Capstone AI Pipeline")
st.caption("Advanced AI Data Pipeline with Authentication & Monitoring")

if not st.session_state.token:
    st.warning("Please login from sidebar")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Navigation Tabs
tabs = st.tabs(["Query", "History", "Dashboard"] + (["Admin"] if st.session_state.role == "admin" else []))


# =========================
# TAB: QUERY
# =========================
with tabs[0]:
    st.header("Ask the AI")

    col1, col2 = st.columns([4, 1])

    question = st.text_input("Ask me anything about the data...")

    if st.button("🔍 Search"):
        if question:
            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{BASE_URL}/ask",
                    json={"question": question},
                    headers=headers
                )

                if res.status_code == 200:
                    data = res.json()

                    st.subheader("Answer")
                    st.write(data["answer"])

                    if data["cached"]:
                        st.warning("⚡ Cache Hit")
                    else:
                        st.success("🚀 Fresh Response")

                    st.info(f"⏱ Response Time: {data['response_time']:.3f}s")

                else:
                    st.error("Error fetching response")


# =========================
# TAB: HISTORY
# =========================
with tabs[1]:
    st.header("History")

    res = requests.get(f"{BASE_URL}/history", headers=headers)

    if res.status_code == 200:
        data = res.json()

        for item in data["history"]:
            st.markdown(f"**Q:** {item['question']}")
            st.markdown(f"**A:** {item['answer']}")
            st.markdown("---")
    else:
        st.error("Failed to fetch history")


# =========================
# TAB: DASHBOARD
# =========================
with tabs[2]:
    st.header("Dashboard")

    res = requests.get(f"{BASE_URL}/dashboard", headers=headers)

    if res.status_code == 200:
        data = res.json()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Queries", data["total_queries"])
        col2.metric("Total Users", data["total_users"])
        col3.metric("Cached Queries", data["cached_queries"])
        col4.metric("Avg Response Time", f"{data['avg_response_time']:.3f}s")

    else:
        st.error("Failed to fetch dashboard")


# =========================
# TAB: ADMIN
# =========================
if st.session_state.role == "admin":
    with tabs[3]:
        st.header("Admin Panel")

        res = requests.get(f"{BASE_URL}/admin/stats", headers=headers)

        if res.status_code == 200:
            data = res.json()

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Requests", data["total_requests"])
            col2.metric("Cached Queries", data["cached_queries"])
            col3.metric("Cache Size", data["cache_size"])
            col4.metric("Avg Response Time", f"{data['avg_response_time']:.3f}s")

        else:
            st.error("Admin access required")