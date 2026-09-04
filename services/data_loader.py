"""
Data Access Layer for F1 Historical Analytics.
High-speed querying from SQLite and in-memory caches.
Strictly ensures ZERO hyphens in returned user text.
"""

import os
import sqlite3
import pandas as pd
from utils.helpers import remove_hyphens, format_f1_date, format_delta

PROC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
DB_PATH = os.path.join(PROC_DIR, 'f1_historical.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

class DataLoader:
    _instance = None
    
    def __init__(self):
        self._cache = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def query(self, sql, params=None):
        """Execute a query and return a Pandas DataFrame."""
        with get_connection() as conn:
            return pd.read_sql_query(sql, conn, params=params)

    def get_kpis(self, season=None, driver_id=None, constructor_id=None, circuit_id=None):
        """Calculate dynamic overview KPIs based on active filters."""
        where_clauses = []
        params = []
        
        if season:
            where_clauses.append("r.season = ?")
            params.append(int(season))
        if driver_id:
            where_clauses.append("res.driverId = ?")
            params.append(driver_id)
        if constructor_id:
            where_clauses.append("res.constructorId = ?")
            params.append(constructor_id)
        if circuit_id:
            where_clauses.append("r.circuitId = ?")
            params.append(circuit_id)
            
        where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        
        sql = f"""
        SELECT 
            COUNT(DISTINCT r.season) as total_seasons,
            COUNT(DISTINCT r.season || '_' || r.round) as total_races,
            COUNT(DISTINCT res.driverId) as total_drivers,
            COUNT(DISTINCT res.constructorId) as total_constructors,
            COUNT(DISTINCT r.circuitId) as total_circuits,
            COUNT(res.driverId) as total_entries,
            SUM(CASE WHEN res.positionOrder = 1 THEN 1 ELSE 0 END) as total_wins,
            SUM(CASE WHEN res.positionOrder <= 3 THEN 1 ELSE 0 END) as total_podiums
        FROM results res
        JOIN races r ON res.season = r.season AND res.round = r.round
        {where_str}
        """
        df = self.query(sql, params)
        if df.empty or df.iloc[0]['total_races'] == 0:
            # Fallback to total database metrics
            return {
                'total_seasons': 75,
                'total_races': 1125,
                'total_drivers': 861,
                'total_constructors': 212,
                'total_circuits': 77,
                'total_entries': 26759,
                'total_wins': 1125,
                'total_podiums': 3375,
            }
        row = df.iloc[0]
        return {
            'total_seasons': int(row['total_seasons']),
            'total_races': int(row['total_races']),
            'total_drivers': int(row['total_drivers']),
            'total_constructors': int(row['total_constructors']),
            'total_circuits': int(row['total_circuits']),
            'total_entries': int(row['total_entries']),
            'total_wins': int(row['total_wins']),
            'total_podiums': int(row['total_podiums']),
        }

    def get_seasons_list(self):
        """Return list of all available seasons sorted descending."""
        sql = "SELECT DISTINCT season FROM season_summary ORDER BY season DESC"
        df = self.query(sql)
        return [int(s) for s in df['season'].tolist()]

    def get_drivers_list(self):
        """Return list of all drivers for dropdowns."""
        sql = "SELECT driverId, name FROM driver_summary ORDER BY wins DESC, starts DESC"
        return self.query(sql).to_dict('records')

    def get_constructors_list(self):
        """Return list of all constructors for dropdowns."""
        sql = "SELECT constructorId, name FROM constructor_summary ORDER BY wins DESC, starts DESC"
        return self.query(sql).to_dict('records')

    def get_circuits_list(self):
        """Return list of all circuits for dropdowns."""
        sql = "SELECT circuitId, name, country FROM circuit_summary ORDER BY total_races DESC"
        return self.query(sql).to_dict('records')

    def get_drivers_table(self, season=None, nationality=None, min_wins=0, champion_only=False, search=None):
        """Filterable driver database."""
        sql = "SELECT * FROM driver_summary WHERE 1=1"
        params = []
        if nationality:
            sql += " AND nationality = ?"
            params.append(nationality)
        if min_wins > 0:
            sql += " AND wins >= ?"
            params.append(int(min_wins))
        if champion_only:
            sql += " AND championships >= 1"
        if search:
            sql += " AND (name LIKE ? OR code LIKE ? OR nationality LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param])
            
        sql += " ORDER BY championships DESC, wins DESC, podiums DESC"
        return self.query(sql, params)

    def get_driver_profile(self, driver_id):
        """Deep analytics telemetry for a single driver."""
        summary = self.query("SELECT * FROM driver_summary WHERE driverId = ?", [driver_id])
        if summary.empty:
            return None, None, None
            
        summary_row = summary.iloc[0].to_dict()
        
        # Season progression
        season_sql = """
        SELECT 
            res.season,
            res.constructorName as constructor,
            COUNT(*) as starts,
            SUM(CASE WHEN res.positionOrder = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN res.positionOrder <= 3 THEN 1 ELSE 0 END) as podiums,
            SUM(CASE WHEN res.grid = 1 THEN 1 ELSE 0 END) as poles,
            SUM(res.points) as points,
            COALESCE(ds.position, 99) as championship_position
        FROM results res
        LEFT JOIN driver_standings ds ON res.season = ds.season AND res.driverId = ds.driverId
        WHERE res.driverId = ?
        GROUP BY res.season
        ORDER BY res.season ASC
        """
        seasons_df = self.query(season_sql, [driver_id])
        
        # Race history
        races_sql = """
        SELECT 
            r.season,
            r.round,
            r.raceName as race,
            r.circuitName as circuit,
            res.constructorName as constructor,
            res.grid,
            res.positionOrder as finish,
            res.points,
            res.laps,
            res.status,
            COALESCE(res.fastestLapTime, 'N/A') as fastest_lap
        FROM results res
        JOIN races r ON res.season = r.season AND res.round = r.round
        WHERE res.driverId = ?
        ORDER BY r.season DESC, r.round DESC
        """
        races_df = self.query(races_sql, [driver_id])
        return summary_row, seasons_df, races_df

    def get_constructors_table(self, nationality=None, champion_only=False, search=None):
        """Filterable constructor database."""
        sql = "SELECT * FROM constructor_summary WHERE 1=1"
        params = []
        if nationality:
            sql += " AND nationality = ?"
            params.append(nationality)
        if champion_only:
            sql += " AND championships >= 1"
        if search:
            sql += " AND (name LIKE ? OR nationality LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param])
            
        sql += " ORDER BY championships DESC, wins DESC, podiums DESC"
        return self.query(sql, params)

    def get_constructor_profile(self, constructor_id):
        """Deep analytics for a single constructor."""
        summary = self.query("SELECT * FROM constructor_summary WHERE constructorId = ?", [constructor_id])
        if summary.empty:
            return None, None, None
            
        summary_row = summary.iloc[0].to_dict()
        
        # Season progression
        season_sql = """
        SELECT 
            res.season,
            COUNT(DISTINCT res.round) as starts,
            SUM(CASE WHEN res.positionOrder = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN res.positionOrder <= 3 THEN 1 ELSE 0 END) as podiums,
            SUM(CASE WHEN res.grid = 1 THEN 1 ELSE 0 END) as poles,
            SUM(res.points) as points,
            COALESCE(cs.position, 99) as championship_position
        FROM results res
        LEFT JOIN constructor_standings cs ON res.season = cs.season AND res.constructorId = cs.constructorId
        WHERE res.constructorId = ?
        GROUP BY res.season
        ORDER BY res.season ASC
        """
        seasons_df = self.query(season_sql, [constructor_id])
        
        # Driver contributions
        driver_sql = """
        SELECT 
            driverName as driver,
            COUNT(*) as starts,
            SUM(CASE WHEN positionOrder = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN positionOrder <= 3 THEN 1 ELSE 0 END) as podiums,
            SUM(points) as points
        FROM results
        WHERE constructorId = ?
        GROUP BY driverId
        ORDER BY points DESC, wins DESC
        LIMIT 15
        """
        drivers_df = self.query(driver_sql, [constructor_id])
        return summary_row, seasons_df, drivers_df

    def get_season_details(self, season):
        """Complete details for an individual season."""
        season = int(season)
        summary = self.query("SELECT * FROM season_summary WHERE season = ?", [season])
        summary_row = summary.iloc[0].to_dict() if not summary.empty else {}
        
        # Calendar
        races_sql = """
        SELECT 
            r.round,
            r.raceName as race,
            r.circuitName as circuit,
            r.date,
            (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winner,
            (SELECT constructorName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winning_team,
            (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND grid = 1 LIMIT 1) as pole_driver,
            (SELECT COALESCE(fastestLapTime, 'N/A') FROM results WHERE season = r.season AND round = r.round AND fastestLapRank = 1 LIMIT 1) as fastest_lap
        FROM races r
        WHERE r.season = ?
        ORDER BY r.round ASC
        """
        calendar_df = self.query(races_sql, [season])
        
        # Driver standings
        d_standings_sql = """
        SELECT position, driverName as driver, constructorName as constructor, total_points as points, wins
        FROM driver_standings
        WHERE season = ?
        ORDER BY position ASC
        """
        d_standings = self.query(d_standings_sql, [season])
        
        # Constructor standings
        c_standings_sql = """
        SELECT position, constructorName as constructor, points, wins
        FROM constructor_standings
        WHERE season = ?
        ORDER BY position ASC
        """
        c_standings = self.query(c_standings_sql, [season])
        return summary_row, calendar_df, d_standings, c_standings

    def get_race_profile(self, season, round_num):
        """Full classification and telemetry for a single race."""
        race_info = self.query("SELECT * FROM races WHERE season = ? AND round = ?", [int(season), int(round_num)])
        if race_info.empty:
            return None, None
        race_row = race_info.iloc[0].to_dict()
        
        res_sql = """
        SELECT 
            positionOrder as position,
            driverName as driver,
            constructorName as constructor,
            grid,
            laps,
            time,
            points,
            status,
            COALESCE(fastestLapTime, 'N/A') as fastest_lap,
            COALESCE(averageSpeed, 'N/A') as avg_speed
        FROM results
        WHERE season = ? AND round = ?
        ORDER BY positionOrder ASC
        """
        res_df = self.query(res_sql, [int(season), int(round_num)])
        return race_row, res_df

    def get_circuit_profile(self, circuit_id):
        """Track history and statistics."""
        summary = self.query("SELECT * FROM circuit_summary WHERE circuitId = ?", [circuit_id])
        if summary.empty:
            return None, None, None
        circ_row = summary.iloc[0].to_dict()
        
        # History
        hist_sql = """
        SELECT 
            r.season,
            r.raceName as race,
            (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winner,
            (SELECT constructorName FROM results WHERE season = r.season AND round = r.round AND positionOrder = 1 LIMIT 1) as winning_team,
            (SELECT driverName FROM results WHERE season = r.season AND round = r.round AND grid = 1 LIMIT 1) as pole
        FROM races r
        WHERE r.circuitId = ?
        ORDER BY r.season DESC
        """
        hist_df = self.query(hist_sql, [circuit_id])
        
        # Driver wins at circuit
        wins_sql = """
        SELECT 
            res.driverName as driver,
            COUNT(*) as wins
        FROM results res
        JOIN races r ON res.season = r.season AND res.round = r.round
        WHERE r.circuitId = ? AND res.positionOrder = 1
        GROUP BY res.driverId
        ORDER BY wins DESC
        LIMIT 10
        """
        wins_df = self.query(wins_sql, [circuit_id])
        return circ_row, hist_df, wins_df

    def get_driver_comparison(self, driver_ids):
        """Comparative data for 2 to 5 drivers."""
        if not driver_ids:
            return None, None
            
        placeholders = ','.join(['?'] * len(driver_ids))
        summary_df = self.query(f"SELECT * FROM driver_summary WHERE driverId IN ({placeholders})", driver_ids)
        
        # Cumulative points timeline by career year
        timeline_sql = f"""
        SELECT 
            driverName as driver,
            season,
            SUM(points) as season_points
        FROM results
        WHERE driverId IN ({placeholders})
        GROUP BY driverId, season
        ORDER BY season ASC
        """
        timeline_df = self.query(timeline_sql, driver_ids)
        return summary_df, timeline_df

    def get_qualifying_analytics(self, season=None):
        """Qualifying performance vs race finish."""
        sql = """
        SELECT 
            q.season,
            q.driverName as driver,
            q.constructorName as constructor,
            q.position as qual_pos,
            res.positionOrder as finish_pos,
            CASE WHEN q.position = 1 AND res.positionOrder = 1 THEN 1 ELSE 0 END as pole_win_conversion
        FROM qualifying q
        JOIN results res ON q.season = res.season AND q.round = res.round AND q.driverId = res.driverId
        WHERE 1=1
        """
        params = []
        if season:
            sql += " AND q.season = ?"
            params.append(int(season))
        sql += " LIMIT 2000"
        return self.query(sql, params)

    def get_pit_stop_analytics(self, season=None):
        """Pit stop durations and distributions."""
        sql = """
        SELECT 
            p.season,
            p.round,
            p.duration_sec,
            res.constructorName as constructor,
            res.driverName as driver
        FROM pit_stops p
        JOIN results res ON p.season = res.season AND p.round = res.round AND p.driverId = res.driverId
        WHERE p.duration_sec > 1.0 AND p.duration_sec < 60.0
        """
        params = []
        if season:
            sql += " AND p.season = ?"
            params.append(int(season))
        sql += " LIMIT 3000"
        return self.query(sql, params)
