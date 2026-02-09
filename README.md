# LaLiga-2024-25-Analytics-
LaLiga 2024–25 Analytics is an interactive dashboard project that converts season match, team, and player data into insights. It offers leaderboards, team-style profiles, efficiency metrics (attack/defense), and trend views by team to support scouting, tactical review.


This README is designed to present your project as a professional-grade sports analytics tool. It covers the technical stack, the features you've built, and clear instructions for others (or your future self) to get it running.

---

# ⚽ LaLiga Insights: 2024/25 Analytics Command Center

LaLiga Insights is a professional-grade, full-stack data visualization platform that transforms raw football match and player data into actionable intelligence. Built with a **FastAPI** backend and a **React** frontend, it provides deep dives into team standings, player performance, and tactical trends.

## 🚀 Core Features

* **Live Standings & Season KPIs**: Real-time league table including Goal Difference and Points, supported by a Season Summary bar (Total Goals, Avg Goals/Match).
* **Points Progression Timeline**: A chronological line chart tracking the title race between giants like Barcelona, Real Madrid, and Atlético Madrid.
* **League Leaders Dashboard**: Side-by-side bar charts for Top Scorers (Golden Boot) and Top Assists.
* **Team Performance Metrics**: Visualization of Total Team Goals and a Home vs. Away Win distribution.
* **Head-to-Head Match Center**: Interactive tool to select two teams and compare their seasonal averages in goals, shots, and corners.
* **Scouting Radar**: A multi-dimensional radar chart to compare two players across metrics like Goals Per 90, Assists, and Playtime.
* **Discipline Heatmap**: A dynamic aggression tracker that uses color intensity to identify the most disciplined (or aggressive) teams in the league.

---

## 🛠️ Tech Stack

### **Backend**

* **Python / FastAPI**: High-performance API routing.
* **Pandas**: Data manipulation and aggregation of CSV/Excel files.
* **Uvicorn**: ASGI server implementation.

### **Frontend**

* **React.js**: Modern component-based UI.
* **Recharts**: Composable charting library for the Radar, Line, and Bar graphs.
* **Lucide-React**: Clean, consistent iconography.
* **Axios**: Promise-based HTTP client for API communication.

---

## 📁 Project Structure

```text
laliga_analysis/
├── backend/
│   ├── main.py            # FastAPI endpoints & logic
│   ├── data_manager.py     # Data cleaning engine (Pandas)
│   ├── LaLiga.csv         # Seasonal match data
│   └── player.xlsx        # Detailed player statistics
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main Dashboard UI
│   │   └── index.css      # Global styles & Inter font
│   └── package.json
└── README.md

```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

* Python 3.8+
* Node.js & npm

### 2. Backend Setup

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip install fastapi uvicorn pandas openpyxl

# Start the server
python -m uvicorn main:app --reload

```

*The API will be available at `http://127.0.0.1:8000`.*

### 3. Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install axios recharts lucide-react

# Start the dashboard
npm start

```

*The UI will be available at `http://localhost:3000`.*

---

## 📊 Data Requirements

The system expects two primary data sources:

1. **`LaLiga.csv`**: Must contain columns: `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, `HS`, `AS`, `HY`, `AY`, `HR`, `AR`.
2. **`player.xlsx`**: An FBRef-style export containing player names, squads, and metrics (Gls, Ast, Gls_Per90, etc.).

---

## 🎨 UI Design Philosophy

The dashboard utilizes a **Dark Mode** aesthetic (`#0f172a`) inspired by high-end sports betting and analytical platforms.

* **Accent Blue (`#3b82f6`)**: Primary actions and data points.
* **Golden Yellow (`#fbbf24`)**: Leadership and trophy-related metrics.
* **Aggression Red (`#ef4444`)**: Discipline and high-intensity alerts.

---

**Would you like me to add a "Contribution" section or specific "Deployment" instructions for platforms like Vercel or Heroku?**
