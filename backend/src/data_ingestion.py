"""
Data ingestion module for NBA Predictor.
Handles fetching data from basketball-reference and odds APIs.
"""
import pandas as pd
import requests
from datetime import datetime, timedelta
from basketball_reference_scraper import teams, seasons, schedule, box_scores
from sqlalchemy.orm import Session
from src.database import (
    get_session, Team, Game, TeamBoxScore, Odds, init_database
)
from src.config import ODDS_API_KEY, ODDS_API_BASE_URL
import time
from typing import List, Dict, Optional


class DataIngestor:
    """Handles all data ingestion tasks."""
    
    def __init__(self):
        self.session = get_session()
        init_database()  # Ensure tables exist
    
    def _get_or_create_team(self, team_name: str, abbreviation: str) -> Team:
        """Get existing team or create new one."""
        team = self.session.query(Team).filter_by(abbreviation=abbreviation).first()
        if not team:
            team = Team(team_name=team_name, abbreviation=abbreviation)
            self.session.add(team)
            self.session.commit()
            self.session.refresh(team)
        return team
    
    def _create_game_id(self, date: datetime, home_abbr: str, away_abbr: str) -> str:
        """Create unique game ID."""
        return f"{date.strftime('%Y-%m-%d')}-{home_abbr}-{away_abbr}"
    
    def fetch_historical_games_and_stats(self, start_season: int = 2010, end_season: int = None):
        """
        Fetch historical games and statistics from basketball-reference.
        
        Args:
            start_season: First season to fetch (e.g., 2010 for 2010-2011 season)
            end_season: Last season to fetch (defaults to current season)
        """
        if end_season is None:
            end_season = datetime.now().year
        
        print(f"Fetching historical data from {start_season} to {end_season}...")
        
        for season in range(start_season, end_season + 1):
            print(f"Processing season {season}...")
            try:
                # Get schedule for the season
                df = schedule(season)
                
                if df is None or df.empty:
                    print(f"No data found for season {season}")
                    continue
                
                # Process each game
                for idx, row in df.iterrows():
                    try:
                        date_str = row.get('DATE', '')
                        if not date_str:
                            continue
                        
                        # Parse date
                        try:
                            game_date = pd.to_datetime(date_str).date()
                        except:
                            continue
                        
                        # Get team abbreviations
                        visitor = str(row.get('VISITOR', '')).strip()
                        home = str(row.get('HOME', '')).strip()
                        
                        if not visitor or not home:
                            continue
                        
                        # Get or create teams
                        visitor_team = self._get_or_create_team(visitor, visitor)
                        home_team = self._get_or_create_team(home, home)
                        
                        # Create game ID
                        game_id = self._create_game_id(
                            datetime.combine(game_date, datetime.min.time()),
                            home_team.abbreviation,
                            visitor_team.abbreviation
                        )
                        
                        # Check if game already exists
                        existing_game = self.session.query(Game).filter_by(game_id=game_id).first()
                        if existing_game:
                            continue
                        
                        # Get scores if available
                        visitor_score = None
                        home_score = None
                        if 'VISITOR_PTS' in row and pd.notna(row['VISITOR_PTS']):
                            visitor_score = int(row['VISITOR_PTS'])
                        if 'HOME_PTS' in row and pd.notna(row['HOME_PTS']):
                            home_score = int(row['HOME_PTS'])
                        
                        # Create game
                        game = Game(
                            game_id=game_id,
                            date=game_date,
                            home_team_id=home_team.team_id,
                            away_team_id=visitor_team.team_id,
                            home_score=home_score,
                            away_score=visitor_score,
                            season=season,
                            game_type="regular"  # Could be enhanced to detect playoffs
                        )
                        self.session.add(game)
                        self.session.commit()
                        
                        # Fetch box scores if game is completed
                        if visitor_score is not None and home_score is not None:
                            try:
                                self._fetch_and_store_box_scores(game_id, game_date, visitor_team, home_team)
                            except Exception as e:
                                print(f"Error fetching box scores for {game_id}: {e}")
                        
                        # Rate limiting
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"Error processing game {idx} in season {season}: {e}")
                        continue
                
                print(f"Completed season {season}")
                time.sleep(1)  # Rate limiting between seasons
                
            except Exception as e:
                print(f"Error processing season {season}: {e}")
                continue
        
        print("Historical data ingestion complete!")
    
    def _fetch_and_store_box_scores(self, game_id: str, game_date, visitor_team: Team, home_team: Team):
        """Fetch and store box scores for a completed game."""
        try:
            # Fetch box scores
            box_score_df = box_scores(game_date, visitor_team.abbreviation, home_team.abbreviation)
            
            if box_score_df is None or box_score_df.empty:
                return
            
            # Process visitor team box score
            if visitor_team.abbreviation in box_score_df.index:
                visitor_stats = box_score_df.loc[visitor_team.abbreviation]
                self._create_box_score(game_id, visitor_team.team_id, False, visitor_stats)
            
            # Process home team box score
            if home_team.abbreviation in box_score_df.index:
                home_stats = box_score_df.loc[home_team.abbreviation]
                self._create_box_score(game_id, home_team.team_id, True, home_stats)
            
            self.session.commit()
            
        except Exception as e:
            print(f"Error in _fetch_and_store_box_scores: {e}")
            raise
    
    def _create_box_score(self, game_id: str, team_id: int, is_home: bool, stats: pd.Series):
        """Create a TeamBoxScore record from stats series."""
        # Check if box score already exists
        existing = self.session.query(TeamBoxScore).filter_by(
            game_id=game_id, team_id=team_id
        ).first()
        if existing:
            return
        
        box_score = TeamBoxScore(
            game_id=game_id,
            team_id=team_id,
            is_home=is_home,
            fg=int(stats.get('FG', 0)) if pd.notna(stats.get('FG')) else 0,
            fga=int(stats.get('FGA', 0)) if pd.notna(stats.get('FGA')) else 0,
            fg_pct=float(stats.get('FG%', 0)) if pd.notna(stats.get('FG%')) else 0.0,
            fg3=int(stats.get('3P', 0)) if pd.notna(stats.get('3P')) else 0,
            fg3a=int(stats.get('3PA', 0)) if pd.notna(stats.get('3PA')) else 0,
            fg3_pct=float(stats.get('3P%', 0)) if pd.notna(stats.get('3P%')) else 0.0,
            ft=int(stats.get('FT', 0)) if pd.notna(stats.get('FT')) else 0,
            fta=int(stats.get('FTA', 0)) if pd.notna(stats.get('FTA')) else 0,
            ft_pct=float(stats.get('FT%', 0)) if pd.notna(stats.get('FT%')) else 0.0,
            orb=int(stats.get('ORB', 0)) if pd.notna(stats.get('ORB')) else 0,
            drb=int(stats.get('DRB', 0)) if pd.notna(stats.get('DRB')) else 0,
            trb=int(stats.get('TRB', 0)) if pd.notna(stats.get('TRB')) else 0,
            ast=int(stats.get('AST', 0)) if pd.notna(stats.get('AST')) else 0,
            stl=int(stats.get('STL', 0)) if pd.notna(stats.get('STL')) else 0,
            blk=int(stats.get('BLK', 0)) if pd.notna(stats.get('BLK')) else 0,
            tov=int(stats.get('TOV', 0)) if pd.notna(stats.get('TOV')) else 0,
            pf=int(stats.get('PF', 0)) if pd.notna(stats.get('PF')) else 0,
            pts=int(stats.get('PTS', 0)) if pd.notna(stats.get('PTS')) else 0,
            plus_minus=int(stats.get('+/-', 0)) if pd.notna(stats.get('+/-')) else 0,
        )
        self.session.add(box_score)
    
    def fetch_historical_odds(self, csv_path: str = "data/historical_odds.csv"):
        """
        Load historical odds from CSV file and populate odds table.
        
        Args:
            csv_path: Path to CSV file with historical odds data
        """
        try:
            df = pd.read_csv(csv_path)
            print(f"Loading odds from {csv_path}...")
            
            for idx, row in df.iterrows():
                try:
                    game_id = row.get('game_id')
                    if not game_id:
                        continue
                    
                    # Check if game exists
                    game = self.session.query(Game).filter_by(game_id=game_id).first()
                    if not game:
                        continue
                    
                    # Create odds record
                    odds = Odds(
                        game_id=game_id,
                        bookmaker=row.get('bookmaker', 'unknown'),
                        home_team_spread=float(row.get('home_spread')) if pd.notna(row.get('home_spread')) else None,
                        home_team_spread_odds=int(row.get('home_spread_odds')) if pd.notna(row.get('home_spread_odds')) else None,
                        away_team_spread=float(row.get('away_spread')) if pd.notna(row.get('away_spread')) else None,
                        away_team_spread_odds=int(row.get('away_spread_odds')) if pd.notna(row.get('away_spread_odds')) else None,
                        home_team_moneyline=int(row.get('home_moneyline')) if pd.notna(row.get('home_moneyline')) else None,
                        away_team_moneyline=int(row.get('away_moneyline')) if pd.notna(row.get('away_moneyline')) else None,
                        over_under_total=float(row.get('over_under')) if pd.notna(row.get('over_under')) else None,
                        over_odds=int(row.get('over_odds')) if pd.notna(row.get('over_odds')) else None,
                        under_odds=int(row.get('under_odds')) if pd.notna(row.get('under_odds')) else None,
                    )
                    self.session.add(odds)
                    
                except Exception as e:
                    print(f"Error processing odds row {idx}: {e}")
                    continue
            
            self.session.commit()
            print("Historical odds loaded successfully!")
            
        except FileNotFoundError:
            print(f"Historical odds file not found at {csv_path}. Skipping...")
        except Exception as e:
            print(f"Error loading historical odds: {e}")
    
    def fetch_upcoming_games(self, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming games for the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of game dictionaries
        """
        current_season = datetime.now().year
        try:
            df = schedule(current_season)
            upcoming_games = []
            
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)
            
            for idx, row in df.iterrows():
                try:
                    date_str = row.get('DATE', '')
                    if not date_str:
                        continue
                    
                    game_date = pd.to_datetime(date_str).date()
                    if today <= game_date <= end_date:
                        upcoming_games.append({
                            'date': game_date,
                            'visitor': row.get('VISITOR', ''),
                            'home': row.get('HOME', '')
                        })
                except:
                    continue
            
            return upcoming_games
            
        except Exception as e:
            print(f"Error fetching upcoming games: {e}")
            return []
    
    def _map_odds_api_team_to_db_team(self, odds_api_team_name: str) -> Optional[Team]:
        """
        Map The Odds API team name to our database team.
        The Odds API uses full team names like "Los Angeles Lakers" or "LA Lakers".
        """
        # Common mappings for The Odds API team names to our abbreviations
        team_mappings = {
            # Full names
            "Los Angeles Lakers": "LAL",
            "LA Lakers": "LAL",
            "Golden State Warriors": "GSW",
            "Boston Celtics": "BOS",
            "Miami Heat": "MIA",
            "Chicago Bulls": "CHI",
            "New York Knicks": "NYK",
            "Philadelphia 76ers": "PHI",
            "Brooklyn Nets": "BKN",
            "Milwaukee Bucks": "MIL",
            "Toronto Raptors": "TOR",
            "Indiana Pacers": "IND",
            "Cleveland Cavaliers": "CLE",
            "Detroit Pistons": "DET",
            "Orlando Magic": "ORL",
            "Charlotte Hornets": "CHA",
            "Washington Wizards": "WAS",
            "Atlanta Hawks": "ATL",
            "Dallas Mavericks": "DAL",
            "Houston Rockets": "HOU",
            "San Antonio Spurs": "SAS",
            "Memphis Grizzlies": "MEM",
            "New Orleans Pelicans": "NOP",
            "Oklahoma City Thunder": "OKC",
            "Denver Nuggets": "DEN",
            "Utah Jazz": "UTA",
            "Portland Trail Blazers": "POR",
            "Minnesota Timberwolves": "MIN",
            "Sacramento Kings": "SAC",
            "Phoenix Suns": "PHX",
            "LA Clippers": "LAC",
            "Los Angeles Clippers": "LAC",
            # Variations
            "Lakers": "LAL",
            "Warriors": "GSW",
            "Celtics": "BOS",
            "Heat": "MIA",
            "Bulls": "CHI",
            "Knicks": "NYK",
            "76ers": "PHI",
            "Nets": "BKN",
            "Bucks": "MIL",
            "Raptors": "TOR",
        }
        
        # Try direct mapping first
        if odds_api_team_name in team_mappings:
            abbr = team_mappings[odds_api_team_name]
            return self.session.query(Team).filter_by(abbreviation=abbr).first()
        
        # Try case-insensitive search in database
        team = self.session.query(Team).filter(
            Team.team_name.ilike(f"%{odds_api_team_name}%")
        ).first()
        
        if not team:
            # Try abbreviation match
            team = self.session.query(Team).filter(
                Team.abbreviation.ilike(f"%{odds_api_team_name}%")
            ).first()
        
        return team
    
    def _parse_odds_api_response(self, game_data: dict, game_date: datetime.date) -> List[Odds]:
        """
        Parse The Odds API response and create Odds records.
        
        Args:
            game_data: Single game data from The Odds API
            game_date: Date of the game
            
        Returns:
            List of Odds objects
        """
        odds_records = []
        
        try:
            # Extract game information
            home_team_name = game_data.get('home_team', '')
            away_team_name = game_data.get('away_team', '')
            
            # Map to our database teams
            home_team = self._map_odds_api_team_to_db_team(home_team_name)
            away_team = self._map_odds_api_team_to_db_team(away_team_name)
            
            if not home_team or not away_team:
                print(f"Could not map teams: {home_team_name} vs {away_team_name}")
                return odds_records
            
            # Create game ID
            game_id = self._create_game_id(
                datetime.combine(game_date, datetime.min.time()),
                home_team.abbreviation,
                away_team.abbreviation
            )
            
            # Check if game exists, create if not
            game = self.session.query(Game).filter_by(game_id=game_id).first()
            if not game:
                game = Game(
                    game_id=game_id,
                    date=game_date,
                    home_team_id=home_team.team_id,
                    away_team_id=away_team.team_id,
                    season=game_date.year if game_date.month >= 10 else game_date.year - 1
                )
                self.session.add(game)
                self.session.commit()
            
            # Process bookmakers
            bookmakers = game_data.get('bookmakers', [])
            
            for bookmaker_data in bookmakers:
                bookmaker_name = bookmaker_data.get('title', 'unknown')
                
                # Extract markets
                markets = bookmaker_data.get('markets', [])
                
                # Initialize odds values
                home_moneyline = None
                away_moneyline = None
                home_spread = None
                home_spread_odds = None
                away_spread = None
                away_spread_odds = None
                over_under = None
                over_odds = None
                under_odds = None
                
                for market in markets:
                    market_key = market.get('key', '')
                    
                    if market_key == 'h2h':  # Moneyline
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome.get('name') == home_team_name:
                                home_moneyline = int(outcome.get('price', 0))
                            elif outcome.get('name') == away_team_name:
                                away_moneyline = int(outcome.get('price', 0))
                    
                    elif market_key == 'spreads':  # Point spreads
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            name = outcome.get('name', '')
                            point = outcome.get('point', 0)
                            price = int(outcome.get('price', 0))
                            
                            if name == home_team_name:
                                home_spread = float(point)
                                home_spread_odds = price
                            elif name == away_team_name:
                                away_spread = float(point)
                                away_spread_odds = price
                    
                    elif market_key == 'totals':  # Over/Under
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            name = outcome.get('name', '').lower()
                            point = outcome.get('point', 0)
                            price = int(outcome.get('price', 0))
                            
                            if 'over' in name:
                                over_under = float(point)
                                over_odds = price
                            elif 'under' in name:
                                if over_under is None:
                                    over_under = float(point)
                                under_odds = price
                
                # Check if odds already exist for this game and bookmaker
                existing = self.session.query(Odds).filter_by(
                    game_id=game_id,
                    bookmaker=bookmaker_name
                ).first()
                
                if existing:
                    # Update existing odds
                    existing.home_team_moneyline = home_moneyline
                    existing.away_team_moneyline = away_moneyline
                    existing.home_team_spread = home_spread
                    existing.home_team_spread_odds = home_spread_odds
                    existing.away_team_spread = away_spread
                    existing.away_team_spread_odds = away_spread_odds
                    existing.over_under_total = over_under
                    existing.over_odds = over_odds
                    existing.under_odds = under_odds
                    existing.fetched_at = datetime.now().date()
                else:
                    # Create new odds record
                    odds = Odds(
                        game_id=game_id,
                        bookmaker=bookmaker_name,
                        home_team_moneyline=home_moneyline,
                        away_team_moneyline=away_moneyline,
                        home_team_spread=home_spread,
                        home_team_spread_odds=home_spread_odds,
                        away_team_spread=away_spread,
                        away_team_spread_odds=away_spread_odds,
                        over_under_total=over_under,
                        over_odds=over_odds,
                        under_odds=under_odds
                    )
                    odds_records.append(odds)
                    self.session.add(odds)
        
        except Exception as e:
            print(f"Error parsing odds data: {e}")
        
        return odds_records
    
    def fetch_historical_odds_from_api(self, start_date: datetime.date, end_date: datetime.date):
        """
        Fetch historical odds from The Odds API.
        The Odds API provides historical data since mid-2020.
        
        Args:
            start_date: Start date for historical odds
            end_date: End date for historical odds
        """
        if not ODDS_API_KEY or ODDS_API_KEY == "YOUR_API_KEY_HERE":
            print("ODDS_API_KEY not configured. Skipping historical odds fetch.")
            return
        
        print(f"Fetching historical odds from {start_date} to {end_date}...")
        
        current_date = start_date
        total_odds_fetched = 0
        
        while current_date <= end_date:
            try:
                # The Odds API historical endpoint
                url = f"{ODDS_API_BASE_URL}/sports/basketball_nba/odds-history"
                params = {
                    "apiKey": ODDS_API_KEY,
                    "regions": "us",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                    "date": current_date.isoformat()
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                # Check rate limits
                if response.status_code == 429:
                    print(f"Rate limit reached. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    print(f"No odds data for {current_date}")
                    current_date += timedelta(days=1)
                    time.sleep(1)  # Rate limiting
                    continue
                
                # Process each game
                for game_data in data:
                    odds_records = self._parse_odds_api_response(game_data, current_date)
                    total_odds_fetched += len(odds_records)
                
                self.session.commit()
                print(f"Fetched odds for {current_date}: {len(data)} games")
                
                # Rate limiting - The Odds API free plan allows 500 requests/month
                time.sleep(2)  # Be conservative with API calls
                
                current_date += timedelta(days=1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching odds for {current_date}: {e}")
                time.sleep(5)  # Wait before retrying
                continue
            except Exception as e:
                print(f"Unexpected error for {current_date}: {e}")
                current_date += timedelta(days=1)
                continue
        
        print(f"Historical odds fetch complete! Total odds records: {total_odds_fetched}")
    
    def fetch_live_odds(self, game_date: Optional[datetime] = None):
        """
        Fetch current/live odds from The Odds API for games on a specific date.
        
        Args:
            game_date: Date to fetch odds for (defaults to today)
        """
        if not ODDS_API_KEY or ODDS_API_KEY == "YOUR_API_KEY_HERE":
            print("ODDS_API_KEY not configured. Skipping live odds fetch.")
            return
        
        if game_date is None:
            game_date = datetime.now()
        
        if isinstance(game_date, datetime):
            game_date = game_date.date()
        
        try:
            # The Odds API endpoint for current NBA odds
            url = f"{ODDS_API_BASE_URL}/sports/basketball_nba/odds"
            params = {
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso"
            }
            
            # If specific date requested, use odds-history endpoint
            if game_date != datetime.now().date():
                url = f"{ODDS_API_BASE_URL}/sports/basketball_nba/odds-history"
                params["date"] = game_date.isoformat()
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print(f"No odds data available for {game_date}")
                return
            
            total_odds = 0
            for game_data in data:
                odds_records = self._parse_odds_api_response(game_data, game_date)
                total_odds += len(odds_records)
            
            self.session.commit()
            print(f"Fetched {total_odds} odds records for {game_date}")
                    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching live odds: {e}")
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    print("Rate limit exceeded. Please wait before making more requests.")
                elif e.response.status_code == 401:
                    print("Invalid API key. Please check your ODDS_API_KEY.")
        except Exception as e:
            print(f"Error processing live odds: {e}")
    
    def update_daily_data(self):
        """
        Daily update function for cron job.
        - Fetches yesterday's completed games and updates database
        - Fetches today's odds from The Odds API
        """
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now()
        
        print(f"Updating data for {yesterday.date()}...")
        
        # Fetch yesterday's games (if any are missing)
        # This would involve checking which games from yesterday are in the DB
        # and fetching box scores for any that are missing
        
        # Fetch today's odds from The Odds API
        print("Fetching today's odds from The Odds API...")
        self.fetch_live_odds(today)
        
        print("Daily update complete!")
    
    def close(self):
        """Close database session."""
        self.session.close()


if __name__ == "__main__":
    ingestor = DataIngestor()
    # Example: Fetch historical data
    # ingestor.fetch_historical_games_and_stats(2020, 2024)
    ingestor.close()

