# QueueEase - Flask Quick Start

## 🚀 Super Simple Setup!

### Step 1: Make sure Flask is installed
```bash
pip install flask
```

### Step 2: Run the Customer App
```bash
python customer_app_flask.py
```
Open your browser to: **http://localhost:5000**

### Step 3: Run the Restaurant Dashboard (in a NEW terminal/command prompt)
```bash
python restaurant_dashboard_flask.py
```
Open your browser to: **http://localhost:5001**

## 🎯 Demo Flow

1. **Open Customer App** (localhost:5000)
   - Browse restaurants
   - Click "Join Queue" on any restaurant
   - See your live position

2. **Open Restaurant Dashboard** (localhost:5001)
   - Go to "Queue Management" tab
   - See the customer you just added!
   - Click "Call Next Customer"
   - Click ✅ "Seat" to seat them
   - Watch the queue update in real-time

## ✨ Features

### Customer App:
- 🔍 **Discover**: Browse restaurants with live queue info
- 📋 **My Queue**: Real-time position tracking (updates every 5 seconds)
- 📜 **History**: Past queue entries

### Restaurant Dashboard:
- 📊 **Dashboard**: Stats overview
- 👥 **Queue Management**: Manage customers, call next, seat, mark no-shows
- 📈 **Analytics**: Performance metrics

## 💡 Tips

- Open both apps side-by-side in different browser tabs
- Join a queue in the customer app, then switch to dashboard to manage it
- The queue position auto-updates every 5 seconds
- Add walk-in customers from the dashboard

## 🛠️ Troubleshooting

**"Address already in use" error?**
- Make sure you're running the apps on different ports (5000 and 5001)
- Or stop the other app first

**Flask not found?**
```bash
pip install flask
```

**Templates not found?**
- Make sure the `templates` folder is in the same directory as the .py files

Enjoy your presentation! 🎉
