import streamlit as st
import sqlite3
import datetime
import smtplib
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


def borrow_card(card_code, borrower, email):
    borrow_date = datetime.date.today()
    due_date = borrow_date + datetime.timedelta(weeks=2)
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("INSERT INTO records (card_code, borrower, borrow_date, due_date, email) VALUES (?, ?, ?, ?, ?)",
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
    msg["From"] = "your_email@example.com"  # Change this to your email
    msg["To"] = to_email

    with smtplib.SMTP("smtp.example.com", 587) as server:  # Change SMTP settings
        server.starttls()
        server.login("your_email@example.com", "your_password")  # Update credentials
        server.sendmail("your_email@example.com", to_email, msg.as_string())


st.title("Company Swimming Card Tracker")
init_db()

menu = st.sidebar.selectbox("Menu", ["Borrow Card", "Return Card", "View Records", "Check Overdue"])

if menu == "Borrow Card":
    card_code = st.text_input("Card Code:")
    borrower = st.text_input("Borrower's Name:")
    email = st.text_input("Borrower's Email:")
    if st.button("Confirm Borrowing"):
        borrow_card(card_code, borrower, email)
        st.success("Borrowing Recorded!")

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
    st.write("### Borrowing Records")
    for r in records:
        st.write(f"Card: {r[0]}, Borrower: {r[1]}, Borrowed: {r[2]}, Due: {r[3]}, Returned: {'Yes' if r[4] else 'No'}")

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
