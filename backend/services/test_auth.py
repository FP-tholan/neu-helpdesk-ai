from database.db import SessionLocal
from services.auth_service import authenticate_user


db = SessionLocal()

try:
    # Test 1: Email + password đúng
    user = authenticate_user(
        db,
        "student@neu.edu.vn",
        "123456"
    )

    if user:
        print("TEST 1 PASS: Login successful")
        print(f"User: {user.email} | Role: {user.role}")
    else:
        print("TEST 1 FAIL")

    # Test 2: Password sai
    user = authenticate_user(
        db,
        "student@neu.edu.vn",
        "wrongpassword"
    )

    if user is None:
        print("TEST 2 PASS: Wrong password rejected")
    else:
        print("TEST 2 FAIL")

    # Test 3: Email không tồn tại
    user = authenticate_user(
        db,
        "unknown@neu.edu.vn",
        "123456"
    )

    if user is None:
        print("TEST 3 PASS: Unknown email rejected")
    else:
        print("TEST 3 FAIL")

    # Test 4: Account bị khóa
    user = authenticate_user(
        db,
        "locked@neu.edu.vn",
        "123456"
    )

    if user is None:
        print("TEST 4 PASS: Locked account rejected")
    else:
        print("TEST 4 FAIL")

finally:
    db.close()