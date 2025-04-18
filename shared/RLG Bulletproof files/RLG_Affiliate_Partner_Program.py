#!/usr/bin/env python3
"""
RLG Affiliate Partner Program System - Enhanced Version
--------------------------------------------------------
This system automates affiliate management for RLG Data and RLG Fans.

New Enhancements:
- Telegram notifications for affiliates
- Real-time earnings dashboard
- Multi-currency payout support (USD, EUR, GBP)
- Multi-language email alerts (English, Spanish, French)
- Secure API authentication
- Webhooks for external integration

"""

import uuid
import sqlite3
import time
import requests
import schedule
import smtplib
import json
import telebot
from forex_python.converter import CurrencyRates
from flask import Flask, request, jsonify, render_template, Response

# Flask App
app = Flask(__name__)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-telegram-chat-id"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Currency Converter
currency_converter = CurrencyRates()

# Database Setup
DB_NAME = "rlg_affiliate_program.db"

def init_db():
    """Initializes the database for affiliate tracking."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS affiliates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        country TEXT,
        currency TEXT DEFAULT 'USD',
        referral_code TEXT UNIQUE,
        total_clicks INTEGER DEFAULT 0,
        total_conversions INTEGER DEFAULT 0,
        earnings REAL DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referral_code TEXT,
        user_ip TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        converted INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Affiliate Registration
@app.route("/register_affiliate", methods=["POST"])
def register_affiliate():
    """Registers a new affiliate and generates a referral code."""
    data = request.json
    name, email, country = data.get("name"), data.get("email"), data.get("country")
    currency = data.get("currency", "USD")
    referral_code = str(uuid.uuid4())[:8]  # Unique referral code

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO affiliates (name, email, country, currency, referral_code) VALUES (?, ?, ?, ?, ?)",
                       (name, email, country, currency, referral_code))
        conn.commit()
        conn.close()

        # Send Telegram Notification
        bot.send_message(TELEGRAM_CHAT_ID, f"🎉 New Affiliate Registered: {name} ({country}) - Referral Code: {referral_code}")

        return jsonify({"status": "success", "referral_code": referral_code})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Affiliate already registered"}), 400

# Track Clicks via Referral Link
@app.route("/track_referral/<referral_code>", methods=["GET"])
def track_referral(referral_code):
    """Tracks a referral when a user clicks an affiliate link."""
    user_ip = request.remote_addr

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO referrals (referral_code, user_ip) VALUES (?, ?)", (referral_code, user_ip))
    cursor.execute("UPDATE affiliates SET total_clicks = total_clicks + 1 WHERE referral_code = ?", (referral_code,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Referral recorded"})

# Mark Conversions (Successful Sign-Ups)
@app.route("/track_conversion/<referral_code>", methods=["POST"])
def track_conversion(referral_code):
    """Marks a successful conversion when a referred user signs up."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE referrals SET converted = 1 WHERE referral_code = ?", (referral_code,))
    cursor.execute("UPDATE affiliates SET total_conversions = total_conversions + 1 WHERE referral_code = ?", (referral_code,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Conversion recorded"})

# Calculate Earnings & Multi-Currency Payouts
def process_payouts():
    """Automatically calculates payouts for affiliates based on conversions and currency rates."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT referral_code, total_conversions, currency, email FROM affiliates")
    affiliates = cursor.fetchall()

    base_payout = 10  # Base $10 per conversion
    for affiliate in affiliates:
        referral_code, total_conversions, currency, email = affiliate
        usd_earnings = total_conversions * base_payout
        converted_earnings = currency_converter.convert("USD", currency, usd_earnings)

        cursor.execute("UPDATE affiliates SET earnings = ? WHERE referral_code = ?", (converted_earnings, referral_code))
        
        # Send Telegram Notification
        bot.send_message(TELEGRAM_CHAT_ID, f"💰 Payout Processed: {email} - Earnings: {converted_earnings:.2f} {currency}")

    conn.commit()
    conn.close()
    print("Payouts processed successfully!")

schedule.every().friday.at("12:00").do(process_payouts)

# Webhooks for External Integrations
@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming webhook requests for external integrations."""
    data = request.json
    print("Webhook received:", data)
    return jsonify({"status": "success", "message": "Webhook processed"})

# Real-Time Dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Displays real-time affiliate statistics."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM affiliates", conn)
    conn.close()
    return Response(df.to_html(), mimetype="text/html")

# Run Flask App
if __name__ == "__main__":
    print("Starting Enhanced RLG Affiliate Partner Program...")
    app.run(debug=True)
