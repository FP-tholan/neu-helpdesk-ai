from database.db import SessionLocal
from models.dispatch_rule import DispatchRule


SEED_RULES = [
    # priority, category,        building_id, team_id
    (10, "COMPUTER",            None,        "T_IT"),
    (10, "WIFI",                None,        "T_IT"),
    (10, "CLEANING",            None,        "T_PSA"),
    (20, None,                  "BLD_A1",    "T_PSA"),
    (20, None,                  "BLD_A2",    "T_PSA"),
    (20, None,                  "BLD_B",     "T_QTTB"),
    (99, None,                  None,        "T_ADMIN"),
]


def seed_dispatch_rules():
    db = SessionLocal()
    try:
        for idx, (prio, cat, bld, team) in enumerate(SEED_RULES, start=1):
            rule_id = f"DR_{idx:03d}"
            if db.query(DispatchRule).filter(DispatchRule.id == rule_id).first():
                print(f"Skip: {rule_id}")
                continue
            db.add(DispatchRule(
                id=rule_id,
                priority=prio,
                category=cat,
                building_id=bld,
                team_id=team,
            ))
        db.commit()
        print("Dispatch rules seeded.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_dispatch_rules()