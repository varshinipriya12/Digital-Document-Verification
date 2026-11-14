import os
import sys
import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from database.mongodb import Database, _serialize_val, _deserialize_val, DiskPersistentDB
import mongomock

def test_disk_persistence():
    test_db_path = os.path.join(os.path.dirname(__file__), "data", "test_db.json")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    raw_mock = mongomock.MongoClient()["test_db"]
    pdb = DiskPersistentDB(raw_mock, test_db_path)

    users_col = pdb["users"]
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # 1. Test Insert
    users_col.insert_one({
        "_id": "user_123",
        "email": "test@example.com",
        "created_at": now
    })

    assert os.path.exists(test_db_path), "DB file was not created on insert"

    # 2. Test Reloading in a separate instance
    raw_mock2 = mongomock.MongoClient()["test_db"]
    pdb2 = DiskPersistentDB(raw_mock2, test_db_path)
    users_col2 = pdb2["users"]

    u = users_col2.find_one({"email": "test@example.com"})
    assert u is not None, "User was not found after reload"
    assert u["_id"] == "user_123", "User ID mismatch"
    assert isinstance(u["created_at"], datetime.datetime), "Datetime was not deserialized correctly"

    # 3. Test Update
    users_col2.update_one({"_id": "user_123"}, {"$set": {"full_name": "John Doe"}})

    # 4. Test Reload after Update
    raw_mock3 = mongomock.MongoClient()["test_db"]
    pdb3 = DiskPersistentDB(raw_mock3, test_db_path)
    u3 = pdb3["users"].find_one({"_id": "user_123"})
    assert u3["full_name"] == "John Doe", "Update failed to persist"

    # Clean up test file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("DiskPersistentDB unit tests PASSED [OK]")

if __name__ == "__main__":
    test_disk_persistence()
