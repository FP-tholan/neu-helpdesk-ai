from database.init_db import init_db
from seed.seed_buildings import seed_buildings
from seed.seed_rooms import seed_rooms
from seed.seed_teams import seed_teams
from seed.seed_users import seed_users
from seed.seed_dispatch_rules import seed_dispatch_rules
from seed.seed_tickets import seed_tickets
from seed.seed_ticket_history import seed_ticket_history
from seed.seed_settings import seed_settings       



if __name__ == "__main__":
    init_db()
    seed_buildings()
    seed_rooms()
    seed_teams()
    seed_users()
    seed_dispatch_rules()
    seed_tickets()
    seed_ticket_history()
    seed_settings()
    print("DONE seed_all.")