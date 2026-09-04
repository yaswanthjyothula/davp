"""
Data pipeline script: builds cleaned relational SQLite database and summary tables.
Enforces ZERO hyphens across all computed values, names, dates, and labels.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.helpers import remove_hyphens, format_f1_date

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
PROC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
DB_PATH = os.path.join(PROC_DIR, 'f1_historical.db')

os.makedirs(PROC_DIR, exist_ok=True)

def build_f1_database():
    print("Beginning F1 Historical Data Pipeline...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Circuits
    circuits_df = pd.read_csv(os.path.join(RAW_DIR, 'circuits.csv'))
    circuits_df['circuitName'] = circuits_df['circuitName'].apply(remove_hyphens)
    circuits_df['locality'] = circuits_df['locality'].apply(remove_hyphens)
    circuits_df['country'] = circuits_df['country'].apply(remove_hyphens)
    circuits_df.to_sql('circuits', conn, if_exists='replace', index=False)
    print(f"Circuits loaded: {len(circuits_df)}")

    # 2. Constructors
    constructors_df = pd.read_csv(os.path.join(RAW_DIR, 'constructors.csv'))
    constructors_df['constructorName'] = constructors_df['constructorName'].apply(remove_hyphens)
    constructors_df['nationality'] = constructors_df['nationality'].apply(remove_hyphens)
    constructors_df.to_sql('constructors', conn, if_exists='replace', index=False)
    print(f"Constructors loaded: {len(constructors_df)}")

    # 3. Drivers
    drivers_df = pd.read_csv(os.path.join(RAW_DIR, 'drivers.csv'))
    drivers_df['fullName'] = (drivers_df['givenName'] + ' ' + drivers_df['familyName']).apply(remove_hyphens)
    drivers_df['givenName'] = drivers_df['givenName'].apply(remove_hyphens)
    drivers_df['familyName'] = drivers_df['familyName'].apply(remove_hyphens)
    drivers_df['nationality'] = drivers_df['nationality'].apply(remove_hyphens)
    drivers_df['dateOfBirth'] = drivers_df['dateOfBirth'].apply(format_f1_date)
    drivers_df['permanentNumber'] = drivers_df['permanentNumber'].fillna('N/A').astype(str).replace(r'\.0$', '', regex=True)
    drivers_df['code'] = drivers_df['code'].fillna('N/A')
    drivers_df.to_sql('drivers', conn, if_exists='replace', index=False)
    print(f"Drivers loaded: {len(drivers_df)}")

    # 4. Races
    races_df = pd.read_csv(os.path.join(RAW_DIR, 'races.csv'))
    races_df['raceName'] = races_df['raceName'].apply(remove_hyphens)
    races_df['date'] = races_df['date'].apply(format_f1_date)
    races_df.to_sql('races', conn, if_exists='replace', index=False)
    print(f"Races loaded: {len(races_df)}")

    # 5. Results
    results_df = pd.read_csv(os.path.join(RAW_DIR, 'race_results.csv'), low_memory=False)
    results_df['driverName'] = results_df['driverName'].apply(remove_hyphens)
    results_df['constructorName'] = results_df['constructorName'].apply(remove_hyphens)
    results_df['status'] = results_df['status'].apply(remove_hyphens)
    results_df['points'] = pd.to_numeric(results_df['points'], errors='coerce').fillna(0.0)
    results_df['grid'] = pd.to_numeric(results_df['grid'], errors='coerce').fillna(0).astype(int)
    results_df['positionOrder'] = pd.to_numeric(results_df['position'], errors='coerce').fillna(999).astype(int)
    results_df.to_sql('results', conn, if_exists='replace', index=False)
    print(f"Race results loaded: {len(results_df)}")

    # 6. Qualifying
    qual_df = pd.read_csv(os.path.join(RAW_DIR, 'qualifying_results.csv'))
    qual_df['driverName'] = qual_df['driverName'].apply(remove_hyphens)
    qual_df['constructorName'] = qual_df['constructorName'].apply(remove_hyphens)
    qual_df['position'] = pd.to_numeric(qual_df['position'], errors='coerce').fillna(99).astype(int)
    qual_df.to_sql('qualifying', conn, if_exists='replace', index=False)
    print(f"Qualifying loaded: {len(qual_df)}")

    # 7. Sprint Results
    sprint_df = pd.read_csv(os.path.join(RAW_DIR, 'sprint_results.csv'))
    sprint_df['driverName'] = sprint_df['driverName'].apply(remove_hyphens)
    sprint_df['constructorName'] = sprint_df['constructorName'].apply(remove_hyphens)
    sprint_df['points'] = pd.to_numeric(sprint_df['points'], errors='coerce').fillna(0.0)
    sprint_df.to_sql('sprint_results', conn, if_exists='replace', index=False)
    print(f"Sprint results loaded: {len(sprint_df)}")

    # 8. Pitstops
    pit_df = pd.read_csv(os.path.join(RAW_DIR, 'pitstops.csv'))
    pit_df['duration_sec'] = pd.to_numeric(pit_df['duration'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce').fillna(0.0)
    pit_df.to_sql('pit_stops', conn, if_exists='replace', index=False)
    print(f"Pit stops loaded: {len(pit_df)}")

    # 9. Status
    status_df = pd.read_csv(os.path.join(RAW_DIR, 'status.csv'))
    status_df['status'] = status_df['status'].apply(remove_hyphens)
    status_df.to_sql('status', conn, if_exists='replace', index=False)

    # 10. Seasons
    seasons_raw = pd.read_csv(os.path.join(RAW_DIR, 'seasons.csv'))
    seasons_raw.to_sql('seasons', conn, if_exists='replace', index=False)

    # 10. Generate Driver Standings across all seasons
    print("Computing Driver Standings...")
    # Group by season, round, driver to calculate cumulative points and positions
    season_driver_pts = results_df.groupby(['season', 'driverId', 'driverName', 'constructorName'])['points'].sum().reset_index()
    # Add sprint points where available
    sprint_pts = sprint_df.groupby(['season', 'driverId'])['points'].sum().reset_index().rename(columns={'points': 'sprint_points'})
    season_driver_pts = pd.merge(season_driver_pts, sprint_pts, on=['season', 'driverId'], how='left')
    season_driver_pts['sprint_points'] = season_driver_pts['sprint_points'].fillna(0.0)
    season_driver_pts['total_points'] = season_driver_pts['points'] + season_driver_pts['sprint_points']
    
    # Wins
    driver_wins = results_df[results_df['positionOrder'] == 1].groupby(['season', 'driverId']).size().reset_index(name='wins')
    season_driver_pts = pd.merge(season_driver_pts, driver_wins, on=['season', 'driverId'], how='left')
    season_driver_pts['wins'] = season_driver_pts['wins'].fillna(0).astype(int)
    
    # Rank positions
    season_driver_pts['position'] = season_driver_pts.groupby('season')['total_points'].rank(ascending=False, method='min').astype(int)
    season_driver_pts = season_driver_pts.sort_values(['season', 'position'])
    season_driver_pts.to_sql('driver_standings', conn, if_exists='replace', index=False)

    # 11. Generate Constructor Standings across all seasons
    print("Computing Constructor Standings...")
    season_const_pts = results_df.groupby(['season', 'constructorId', 'constructorName'])['points'].sum().reset_index()
    const_wins = results_df[results_df['positionOrder'] == 1].groupby(['season', 'constructorId']).size().reset_index(name='wins')
    season_const_pts = pd.merge(season_const_pts, const_wins, on=['season', 'constructorId'], how='left')
    season_const_pts['wins'] = season_const_pts['wins'].fillna(0).astype(int)
    season_const_pts['position'] = season_const_pts.groupby('season')['points'].rank(ascending=False, method='min').astype(int)
    season_const_pts = season_const_pts.sort_values(['season', 'position'])
    season_const_pts.to_sql('constructor_standings', conn, if_exists='replace', index=False)

    # 12. Precalculate Driver Summary (All Time Stats)
    print("Computing Driver All Time Summaries...")
    # Driver champions list (position 1 in driver standings for each season)
    champions = season_driver_pts[season_driver_pts['position'] == 1].groupby('driverId').size().to_dict()
    
    d_summary = []
    # Merge driver info with results
    driver_records = results_df.groupby('driverId')
    for driver_id, group in driver_records:
        d_info = drivers_df[drivers_df['driverId'] == driver_id]
        if d_info.empty:
            continue
        d_row = d_info.iloc[0]
        starts = len(group)
        wins = int((group['positionOrder'] == 1).sum())
        podiums = int((group['positionOrder'] <= 3).sum())
        poles = int((group['grid'] == 1).sum())
        total_pts = float(group['points'].sum())
        # Fastest laps
        fl_count = 0
        if 'fastestLapRank' in group.columns:
            fl_count = int((pd.to_numeric(group['fastestLapRank'], errors='coerce') == 1).sum())
        
        # DNFs (status not Finished and not +X Laps)
        dnfs = int((~group['status'].str.lower().str.contains('finished|lap', na=False)).sum())
        
        # Career years
        seasons = group['season'].unique()
        career_start = int(seasons.min())
        career_end = int(seasons.max())
        career_years = f"{career_start} to {career_end}" if career_start != career_end else str(career_start)
        
        win_rate = round((wins / max(starts, 1)) * 100, 1)
        podium_rate = round((podiums / max(starts, 1)) * 100, 1)
        dnf_rate = round((dnfs / max(starts, 1)) * 100, 1)
        
        finished_pos = group[group['positionOrder'] <= 30]['positionOrder']
        avg_finish = round(float(finished_pos.mean()), 1) if not finished_pos.empty else 0.0
        grid_pos = group[group['grid'] > 0]['grid']
        avg_grid = round(float(grid_pos.mean()), 1) if not grid_pos.empty else 0.0
        
        champs = champions.get(driver_id, 0)
        
        d_summary.append({
            'driverId': driver_id,
            'name': d_row['fullName'],
            'code': d_row['code'],
            'number': d_row['permanentNumber'],
            'nationality': d_row['nationality'],
            'dateOfBirth': d_row['dateOfBirth'],
            'career_start': career_start,
            'career_end': career_end,
            'career_years': career_years,
            'starts': starts,
            'wins': wins,
            'podiums': podiums,
            'poles': poles,
            'fastest_laps': fl_count,
            'points': total_pts,
            'dnfs': dnfs,
            'win_rate': win_rate,
            'podium_rate': podium_rate,
            'dnf_rate': dnf_rate,
            'avg_finish': avg_finish,
            'avg_grid': avg_grid,
            'championships': champs,
        })
    
    driver_summary_df = pd.DataFrame(d_summary)
    driver_summary_df.to_sql('driver_summary', conn, if_exists='replace', index=False)
    print(f"Driver summary created: {len(driver_summary_df)}")

    # 13. Precalculate Constructor Summary (All Time Stats)
    print("Computing Constructor All Time Summaries...")
    const_champions = season_const_pts[season_const_pts['position'] == 1].groupby('constructorId').size().to_dict()
    
    c_summary = []
    const_records = results_df.groupby('constructorId')
    for c_id, group in const_records:
        c_info = constructors_df[constructors_df['constructorId'] == c_id]
        if c_info.empty:
            continue
        c_row = c_info.iloc[0]
        # Count unique races entered
        race_starts = group[['season', 'round']].drop_duplicates().shape[0]
        wins = int((group['positionOrder'] == 1).sum())
        podiums = int((group['positionOrder'] <= 3).sum())
        poles = int((group['grid'] == 1).sum())
        total_pts = float(group['points'].sum())
        seasons = group['season'].unique()
        c_start = int(seasons.min())
        c_end = int(seasons.max())
        career_years = f"{c_start} to {c_end}" if c_start != c_end else str(c_start)
        
        c_summary.append({
            'constructorId': c_id,
            'name': c_row['constructorName'],
            'nationality': c_row['nationality'],
            'first_year': c_start,
            'last_year': c_end,
            'career_years': career_years,
            'total_seasons': len(seasons),
            'starts': race_starts,
            'wins': wins,
            'podiums': podiums,
            'poles': poles,
            'points': total_pts,
            'championships': const_champions.get(c_id, 0),
        })
    
    const_summary_df = pd.DataFrame(c_summary)
    const_summary_df.to_sql('constructor_summary', conn, if_exists='replace', index=False)
    print(f"Constructor summary created: {len(const_summary_df)}")

    # 14. Precalculate Circuit Summary
    print("Computing Circuit Summaries...")
    circ_summary = []
    for c_id, group in races_df.groupby('circuitId'):
        c_info = circuits_df[circuits_df['circuitId'] == c_id]
        if c_info.empty:
            continue
        c_row = c_info.iloc[0]
        seasons = group['season'].unique()
        circ_summary.append({
            'circuitId': c_id,
            'name': c_row['circuitName'],
            'locality': c_row['locality'],
            'country': c_row['country'],
            'lat': float(c_row['lat']),
            'long': float(c_row['long']),
            'first_race': int(seasons.min()),
            'last_race': int(seasons.max()),
            'total_races': len(group),
            'career_years': f"{int(seasons.min())} to {int(seasons.max())}",
        })
    circ_summary_df = pd.DataFrame(circ_summary)
    circ_summary_df.to_sql('circuit_summary', conn, if_exists='replace', index=False)
    print(f"Circuit summary created: {len(circ_summary_df)}")

    # 15. Precalculate Season Summary
    print("Computing Season Summaries...")
    season_summary = []
    for s_year, group in races_df.groupby('season'):
        s_results = results_df[results_df['season'] == s_year]
        s_d_standings = season_driver_pts[season_driver_pts['season'] == s_year]
        s_c_standings = season_const_pts[season_const_pts['season'] == s_year]
        
        d_champ = s_d_standings.iloc[0]['driverName'] if not s_d_standings.empty else 'N/A'
        c_champ = s_c_standings.iloc[0]['constructorName'] if not s_c_standings.empty else 'N/A'
        
        season_summary.append({
            'season': int(s_year),
            'total_races': len(group),
            'total_drivers': s_results['driverId'].nunique(),
            'total_constructors': s_results['constructorId'].nunique(),
            'driver_champion': d_champ,
            'constructor_champion': c_champ,
            'total_points': float(s_results['points'].sum()),
        })
    season_summary_df = pd.DataFrame(season_summary).sort_values('season')
    season_summary_df.to_sql('season_summary', conn, if_exists='replace', index=False)
    print(f"Season summary created: {len(season_summary_df)}")

    # Create Indexes for fast querying
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_season ON results(season);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_driver ON results(driverId);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_const ON results(constructorId);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_races_season ON races(season);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ds_season ON driver_standings(season);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cs_season ON constructor_standings(season);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_qual_season ON qualifying(season);")
    conn.commit()
    conn.close()
    print("F1 Historical Database Pipeline completed successfully!")

if __name__ == '__main__':
    build_f1_database()
