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


def get_borrowing_history(card_code):
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute("SELECT borrower, borrow_date, due_date, returned FROM records WHERE card_code = ?", (card_code,))
    history = c.fetchall()
    conn.close()
    return history


def get_available_cards():
    conn = sqlite3.connect("swim_cards.db")
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT card_code FROM records WHERE returned = 1 OR card_code NOT IN (SELECT card_code FROM records WHERE returned = 0)")
    available_cards = [row[0] for row in c.fetchall()]
    conn.close()
    return available_cards


st.title("Company Swimming Card Tracker")
init_db()

menu = st.sidebar.selectbox("Menu", ["Borrow Card", "Return Card", "View Records", "Check Overdue", "View Card History",
                                     "Available Cards"])

if menu == "Check Overdue":
    overdue_list = check_overdue()
    if overdue_list:
        selected_ids = []
        for record in overdue_list:
            selected = st.checkbox(f"{record[1]} - Due: {record[2]}", key=record[0])
            if selected:
                selected_ids.append(record)
        if st.button("Send Bulk Reminders") and selected_ids:
            for record in selected_ids:
                send_email(record[3], record[1], record[2])
            st.success("Bulk reminders sent!")
    else:
        st.write("No overdue records.")
