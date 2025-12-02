"""Quick script to populate teams in database."""
from src.database import get_session, Team, init_database

# NBA teams
nba_teams = [
    ("Los Angeles Lakers", "LAL"),
    ("Golden State Warriors", "GSW"),
    ("Boston Celtics", "BOS"),
    ("Miami Heat", "MIA"),
    ("Chicago Bulls", "CHI"),
    ("New York Knicks", "NYK"),
    ("Philadelphia 76ers", "PHI"),
    ("Brooklyn Nets", "BKN"),
    ("Milwaukee Bucks", "MIL"),
    ("Toronto Raptors", "TOR"),
    ("Indiana Pacers", "IND"),
    ("Cleveland Cavaliers", "CLE"),
    ("Detroit Pistons", "DET"),
    ("Orlando Magic", "ORL"),
    ("Charlotte Hornets", "CHA"),
    ("Washington Wizards", "WAS"),
    ("Atlanta Hawks", "ATL"),
    ("Dallas Mavericks", "DAL"),
    ("Houston Rockets", "HOU"),
    ("San Antonio Spurs", "SAS"),
    ("Memphis Grizzlies", "MEM"),
    ("New Orleans Pelicans", "NOP"),
    ("Oklahoma City Thunder", "OKC"),
    ("Denver Nuggets", "DEN"),
    ("Utah Jazz", "UTA"),
    ("Portland Trail Blazers", "POR"),
    ("Minnesota Timberwolves", "MIN"),
    ("Sacramento Kings", "SAC"),
    ("Phoenix Suns", "PHX"),
    ("Los Angeles Clippers", "LAC"),
]

def populate_teams():
    init_database()
    db = get_session()
    
    try:
        added_count = 0
        existing_count = 0
        
        for team_name, abbreviation in nba_teams:
            # Check if team exists
            existing = db.query(Team).filter_by(abbreviation=abbreviation).first()
            if not existing:
                team = Team(team_name=team_name, abbreviation=abbreviation)
                db.add(team)
                print(f"✅ Added: {team_name} ({abbreviation})")
                added_count += 1
            else:
                print(f"ℹ️  Already exists: {team_name} ({abbreviation})")
                existing_count += 1
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"✅ Successfully populated teams!")
        print(f"   Added: {added_count} new teams")
        print(f"   Already existed: {existing_count} teams")
        print(f"   Total: {len(nba_teams)} teams")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("NBA Teams Database Population")
    print("="*60)
    print()
    populate_teams()

