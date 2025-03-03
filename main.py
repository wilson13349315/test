import streamlit as st
import sqlite3
import datetime
import smtplib
import pandas as pd
from email.mime.text import MIMEText


def init_db():
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_code TEXT,
                    borrower TEXT,
                    borrow_date TEXT,
                    due_date TEXT,
                    returned INTEGER DEFAULT 0,
                    email TEXT)''')
    conn.commit()
    conn.close()


def borrow_card(card_code, borrower, email, duration=14):
    borrow_date = datetime.date.today()
    due_date = borrow_date + datetime.timedelta(days=duration)
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO records (card_code, borrower, borrow_date, due_date, returned, email) VALUES (?, ?, ?, ?, 0, ?)",
        (card_code, borrower, borrow_date, due_date, email))
    conn.commit()
    conn.close()


def return_card(record_id):
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("UPDATE records SET returned = 1 WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def check_overdue():
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT id, borrower, due_date, email FROM records WHERE returned = 0")
    overdue_list = []
    today = datetime.date.today()
    for row in c.fetchall():
        due_date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()
        if due_date < today:
            overdue_list.append(row)
    conn.close()
    return overdue_list


def send_email(to_email, borrower, due_date):
    msg = MIMEText(
        f"Dear {borrower},\n\nYour borrowed swimming card is overdue since {due_date}. Please return it as soon as possible.")
    msg["Subject"] = "Swimming Card Overdue Reminder"
    msg["From"] = "your_email@example.com"
    msg["To"] = to_email

    with smtplib.SMTP("smtp.example.com", 587) as server:  # Change SMTP settings
        server.starttls()
        server.login("your_email@example.com", "your_password")  # Update credentials
        server.sendmail("your_email@example.com", to_email, msg.as_string())


def get_borrowing_history(card_code):
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT borrower, borrow_date, due_date, returned FROM records WHERE card_code = ?", (card_code,))
    history = c.fetchall()
    conn.close()
    return history


def get_available_cards():
    total_cards = {f"Card-{i + 1}" for i in range(10)}  # Assuming 10 cards in total
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT card_code FROM records WHERE returned = 0")
    borrowed_cards = {row[0] for row in c.fetchall()}
    conn.close()
    available_cards = sorted(list(total_cards - borrowed_cards))
    return available_cards


st.title("Company Swimming Card Tracker")
init_db()

menu = st.sidebar.selectbox("Menu", ["Borrow Card", "Return Card", "View Records", "Check Overdue", "View Card History",
                                     "Available Cards"])

if menu == "Borrow Card":
    available_cards = get_available_cards()
    if available_cards:
        card_code = st.selectbox("Card Code:", available_cards)
        borrower = st.text_input("Borrower's Name:")
        email = st.text_input("Borrower's Email:")
        duration = st.number_input("Borrow Duration (days):", min_value=1, max_value=14, value=14)
        if st.button("Confirm Borrowing"):
            borrow_card(card_code, borrower, email, duration)
            st.success("Borrowing Recorded!")
    else:
        st.write("No available cards for borrowing.")

elif menu == "Return Card":
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT id, card_code, borrower FROM records WHERE returned = 0")
    records = c.fetchall()
    conn.close()
    if records:
        record_id = st.selectbox("Select Borrowing Record to Return:", [f"{r[0]} - {r[1]} ({r[2]})" for r in records])
        if st.button("Return Card"):
            return_card(int(record_id.split()[0]))
            st.success("Card Returned!")
    else:
        st.write("No active borrowings.")

elif menu == "View Records":
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT card_code, borrower, borrow_date, due_date, returned FROM records")
    records = c.fetchall()
    conn.close()

    filter_option = st.radio("Filter Records:", ["All", "Returned", "Not Returned"])

    st.write("### Borrowing Records")
    filtered_records = [r for r in records if (filter_option == "All" or (filter_option == "Returned" and r[4]) or (
                filter_option == "Not Returned" and not r[4]))]
    for r in filtered_records:
        st.write(f"Card: {r[0]}, Borrower: {r[1]}, Borrowed: {r[2]}, Due: {r[3]}, Returned: {'Yes' if r[4] else 'No'}")

    df = pd.DataFrame(records, columns=["Card Code", "Borrower", "Borrow Date", "Due Date", "Returned"])
    df["Returned"] = df["Returned"].apply(lambda x: "Yes" if x else "No")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Records", csv, "swim_card_records.csv", "text/csv")

elif menu == "Check Overdue":
    overdue_list = check_overdue()
    if overdue_list:
        for record in overdue_list:
            st.write(f"Borrower: {record[1]}, Due: {record[2]}, Email: {record[3]}")
            if st.button(f"Send Reminder to {record[1]}", key=record[0]):
                send_email(record[3], record[1], record[2])
                st.success("Reminder Sent!")
    else:
        st.write("No overdue records.")

elif menu == "View Card History":
    card_code = st.selectbox("Select Card Code:", [f"Card-{i + 1}" for i in range(10)])
    if st.button("View History"):
        history = get_borrowing_history(card_code)
        if history:
            for h in history:
                st.write(f"Borrower: {h[0]}, Borrowed: {h[1]}, Due: {h[2]}, Returned: {'Yes' if h[3] else 'No'}")
        else:
            st.write("No history found.")

elif menu == "Available Cards":
    available_cards = get_available_cards()
    st.write("### Available Cards")
    for card in available_cards:
        st.write(card)
