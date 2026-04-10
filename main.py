import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

#  CUSTOM UI 
st.markdown("""
<style>

.main {
background-color: #0E1117;
}

.stMetric {
background-color: #1c1f26;
padding: 15px;
border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# DATABASE 
conn = sqlite3.connect("expense.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    expense_date TEXT
)
""")

conn.commit()

# LOAD DATA
cursor.execute("SELECT * FROM expenses")
data = cursor.fetchall()

df = pd.DataFrame(
    data,
    columns=["ID", "Amount", "Category", "Description", "Date"]
)

total_expense = df["Amount"].sum() if not df.empty else 0
total_entries = len(df)
avg_expense = total_expense / total_entries if total_entries > 0 else 0


# SIDEBAR


st.sidebar.title("💰 Expense Tracker")

st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Total Spending", f"₹ {total_expense}")
st.sidebar.metric("Transactions", total_entries)

st.sidebar.markdown("---")

category_filter = st.sidebar.selectbox(
    "🔎 Filter by Category",
    ["All", "Food", "Travel", "Shopping", "Bills", "Other"]
)

st.sidebar.markdown("---")

# Download CSV
if not df.empty:

    csv = df.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        "⬇ Download Data",
        csv,
        "expenses.csv",
        "text/csv"
    )

st.sidebar.markdown("---")

# Reset Database
if st.sidebar.button("⚠ Reset Database"):

    cursor.execute("DELETE FROM expenses")

    conn.commit()

    st.sidebar.success("Database Cleared")

    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Built using Streamlit")


#TITLE

st.title("📊 Expense Dashboard")
st.markdown("---")



#METRICS


col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💵 Total Spending", f"₹ {total_expense}")

with col2:
    st.metric("📊 Total Transactions", total_entries)

with col3:
    st.metric("📈 Avg Expense", f"₹ {round(avg_expense,2)}")

st.markdown("---")


#  FILTER


filtered_df = df.copy()

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["Category"] == category_filter]


#  CHARTS


if not filtered_df.empty:

    col1, col2 = st.columns(2)

    category_data = filtered_df.groupby("Category")["Amount"].sum()

    with col1:
        st.subheader("📊 Spending by Category")
        st.bar_chart(category_data)

    with col2:
        st.subheader("🥧 Category Distribution")

        fig, ax = plt.subplots()

        ax.pie(
            category_data,
            labels=category_data.index,
            autopct='%1.1f%%',
            startangle=90
        )

        ax.axis("equal")

        st.pyplot(fig)


    #    MONTHLY SPENDING


    st.subheader("📅 Monthly Spending")

    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])

    monthly = filtered_df.groupby(
        filtered_df["Date"].dt.to_period("M")
    )["Amount"].sum()

    monthly.index = monthly.index.astype(str)

    st.line_chart(monthly)

  
    #  INSIGHTS SECTION


    st.subheader("🧠 Spending Insights")

    highest = filtered_df.loc[filtered_df["Amount"].idxmax()]
    top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()

    st.success(f"💡 Highest Expense: ₹{highest['Amount']} on {highest['Category']}")
    st.info(f"📊 Most spending category: {top_category}")
    st.warning(f"📅 Total Transactions: {len(filtered_df)}")

else:

    st.info("Add your first expense to see analytics 📊")

st.markdown("---")


#   ADD EXPENSE


col1, col2 = st.columns([1,2])

with col1:

    st.subheader("➕ Add Expense")

    amount = st.number_input("Amount", min_value=0.0)

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills", "Other"]
    )

    description = st.text_input("Description")

    expense_date = st.date_input("Date")

    if st.button("Add Expense"):

        cursor.execute(
            "INSERT INTO expenses (amount, category, description, expense_date) VALUES (?, ?, ?, ?)",
            (amount, category, description, str(expense_date))
        )

        conn.commit()

        st.success("Expense Added Successfully ✅")

        st.rerun()


#  VIEW EXPENSES


with col2:

    st.subheader("📋 All Expenses")

    if not filtered_df.empty:

        display_df = filtered_df.copy()

        display_df = display_df.drop(columns=["ID"])

        display_df.reset_index(drop=True, inplace=True)

        display_df.index += 1

        st.dataframe(display_df, use_container_width=True)

    else:

        st.info("No expenses added yet.")

st.markdown("---")


#  DELETE EXPENSE


st.subheader("🗑 Delete Expense")

if not df.empty:

    selected_id = st.selectbox("Select ID to Delete", df["ID"])

    if st.button("Delete Expense"):

        cursor.execute(
            "DELETE FROM expenses WHERE id = ?",
            (selected_id,)
        )

        conn.commit()

        st.success("Deleted Successfully ✅")

        st.rerun()

else:

    st.info("Nothing to delete.")