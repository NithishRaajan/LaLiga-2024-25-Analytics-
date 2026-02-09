from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_manager import LaLigaDataManager, normalize_name 
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows React (localhost:3000) to talk to FastAPI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
P_PATH = r"d:\laliga_analysis\player.xlsx"
M_PATH = "LaLiga.csv"

manager = LaLigaDataManager(P_PATH, M_PATH)
players_df = manager.get_cleaned_players()
matches_df = manager.get_cleaned_matches()

@app.get("/players/compare")
def compare_players(p1: str, p2: str):
    s1, s2 = normalize_name(p1), normalize_name(p2)
    def find_player(search_term):
        res = players_df[players_df['search_name'].str.contains(search_term, na=False)]
        if res.empty: raise HTTPException(status_code=404, detail="Player not found")
        return res.iloc[0]

    p1_data = find_player(s1)
    p2_data = find_player(s2)

    metrics = ['Gls_Per90', 'Ast_Per90', 'Gls', 'Starts', 'MP']
    chart_data = []
    for m in metrics:
        max_val = players_df[m].max() if players_df[m].max() > 0 else 1
        chart_data.append({
            "subject": m.replace('_', ' '),
            "A": round((p1_data[m] / max_val) * 100, 1),
            "B": round((p2_data[m] / max_val) * 100, 1)
        })
    return {"player1": p1_data['Player'], "player2": p2_data['Player'], "chartData": chart_data}

@app.get("/teams/table")
def get_league_table():
    teams = sorted(matches_df['HomeTeam'].unique())
    table = []
    for t in teams:
        home = matches_df[matches_df['HomeTeam'] == t]
        away = matches_df[matches_df['AwayTeam'] == t]
        
        w = len(home[home['FTR']=='H']) + len(away[away['FTR']=='A'])
        d = len(home[home['FTR']=='D']) + len(away[away['FTR']=='D'])
        l = len(home[home['FTR']=='A']) + len(away[away['FTR']=='H'])
        gf = home['FTHG'].sum() + away['FTAG'].sum()
        ga = home['FTAG'].sum() + away['FTHG'].sum()
        
        table.append({
            "team": t, "gp": int(w+d+l), "w": int(w), "d": int(d), "l": int(l),
            "gf": int(gf), "ga": int(ga), "gd": int(gf-ga), "pts": int(3*w + d)
        })
    # Sort by Points, then Goal Difference
    return sorted(table, key=lambda x: (x['pts'], x['gd']), reverse=True)
@app.get("/teams/timeline")
def get_season_timeline():
    # Sort matches by date to ensure the timeline is chronological
    chronological_matches = matches_df.sort_values(by='Date')
    teams = matches_df['HomeTeam'].unique()
    
    timeline_data = []
    # Initialize point trackers for all teams
    team_points = {team: 0 for team in teams}
    
    # We group by date to show the "League Table" at each point in time
    unique_dates = chronological_matches['Date'].dt.strftime('%Y-%m-%d').unique()
    
    for date in unique_dates:
        day_matches = chronological_matches[chronological_matches['Date'].dt.strftime('%Y-%m-%d') == date]
        
        for _, match in day_matches.iterrows():
            home, away, result = match['HomeTeam'], match['AwayTeam'], match['FTR']
            
            if result == 'H':
                team_points[home] += 3
            elif result == 'A':
                team_points[away] += 3
            else:
                team_points[home] += 1
                team_points[away] += 1
        
        # Snapshot of all teams at this date
        entry = {"date": date}
        entry.update(team_points)
        timeline_data.append(entry)
        
    return timeline_data
@app.get("/teams/discipline")
def get_discipline_data():
    teams = matches_df['HomeTeam'].unique()
    discipline = []
    for t in teams:
        # Aggregate Home and Away fouls and cards
        h_data = matches_df[matches_df['HomeTeam'] == t]
        a_data = matches_df[matches_df['AwayTeam'] == t]
        
        fouls = int(h_data['HF'].sum() + a_data['AF'].sum())
        yellows = int(h_data['HY'].sum() + a_data['AY'].sum())
        reds = int(h_data['HR'].sum() + a_data['AR'].sum())
        
        # Calculate Aggression Score for heatmap intensity
        score = yellows + (reds * 3) + (fouls * 0.1)
        
        discipline.append({
            "team": t, "fouls": fouls, "yellows": yellows, "reds": reds, "score": round(score, 1)
        })
    return sorted(discipline, key=lambda x: x['score'], reverse=True)
@app.get("/matches/compare")
def compare_teams(t1: str, t2: str):
    """Aggregates match stats for a Head-to-Head comparison"""
    def get_team_averages(team_name):
        # Filter all matches where this team played
        t_matches = matches_df[(matches_df['HomeTeam'] == team_name) | (matches_df['AwayTeam'] == team_name)]
        if t_matches.empty:
            raise HTTPException(status_code=404, detail=f"Team {team_name} not found")
        
        # Calculate averages for key metrics
        # If Home, use Home stats; if Away, use Away stats
        goals = (t_matches.apply(lambda x: x['FTHG'] if x['HomeTeam'] == team_name else x['FTAG'], axis=1)).mean()
        shots = (t_matches.apply(lambda x: x['HS'] if x['HomeTeam'] == team_name else x['AS'], axis=1)).mean()
        shots_ot = (t_matches.apply(lambda x: x['HST'] if x['HomeTeam'] == team_name else x['AST'], axis=1)).mean()
        corners = (t_matches.apply(lambda x: x['HC'] if x['HomeTeam'] == team_name else x['AC'], axis=1)).mean()
        
        return {"goals": round(goals, 2), "shots": round(shots, 2), "shots_ot": round(shots_ot, 2), "corners": round(corners, 2)}

    team1_stats = get_team_averages(t1)
    team2_stats = get_team_averages(t2)
    
    # Format for a Bar Chart
    metrics = ["goals", "shots", "shots_ot", "corners"]
    chart_data = []
    for m in metrics:
        chart_data.append({
            "metric": m.replace('_', ' ').upper(),
            "TeamA": team1_stats[m],
            "TeamB": team2_stats[m]
        })
        
    return {"team1": t1, "team2": t2, "data": chart_data}
@app.get("/players/top-scorers-chart")
def get_top_scorers_chart():
    # Sort by Goals descending and take top 10
    top_scorers = players_df.sort_values(by='Gls', ascending=False).head(10)
    
    # Format for Recharts
    chart_data = []
    for _, row in top_scorers.iterrows():
        chart_data.append({
            "name": row['Player'],
            "goals": int(row['Gls']),
            "team": row['Squad']
        })
    return chart_data
@app.get("/players/top-assists-chart")
def get_top_assists_chart():
    # Sort by Assists descending and take top 10
    top_playmakers = players_df.sort_values(by='Ast', ascending=False).head(10)
    
    chart_data = []
    for _, row in top_playmakers.iterrows():
        chart_data.append({
            "name": row['Player'],
            "assists": int(row['Ast']),
            "team": row['Squad']
        })
    return chart_data
@app.get("/teams/goals-scored")
def get_team_goals():
    # Summing goals scored by each team across all matches
    teams = matches_df['HomeTeam'].unique()
    data = []
    for t in teams:
        h_goals = matches_df[matches_df['HomeTeam'] == t]['FTHG'].sum()
        a_goals = matches_df[matches_df['AwayTeam'] == t]['FTAG'].sum()
        data.append({"team": t, "goals": int(h_goals + a_goals)})
    
    # Sort by goals descending
    return sorted(data, key=lambda x: x['goals'], reverse=True)

@app.get("/teams/home-away-wins")
def get_home_away_wins():
    teams = matches_df['HomeTeam'].unique()
    data = []
    for t in teams:
        home_wins = len(matches_df[(matches_df['HomeTeam'] == t) & (matches_df['FTR'] == 'H')])
        away_wins = len(matches_df[(matches_df['AwayTeam'] == t) & (matches_df['FTR'] == 'A')])
        data.append({
            "team": t, 
            "homeWins": home_wins, 
            "awayWins": away_wins,
            "total": home_wins + away_wins
        })
    # Sort by total wins descending
    return sorted(data, key=lambda x: x['total'], reverse=True)

@app.get("/season/stats")
def get_season_stats():
    total_matches = len(matches_df.dropna(subset=['FTR']))
    total_goals = int(matches_df['FTHG'].sum() + matches_df['FTAG'].sum())
    avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
    
    return {
        "season": "2024/25",
        "totalMatches": total_matches,
        "totalGoals": total_goals,
        "avgGoals": avg_goals
    }