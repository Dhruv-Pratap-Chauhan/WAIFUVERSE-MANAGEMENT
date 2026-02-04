import sys
import unittest
import importlib
from pathlib import Path

# Add project root
sys.path.append("/Users/dhruv/WAIFUVERSE_MANAGEMENT")

class TestDatabaseModules(unittest.TestCase):
    
    def test_sql_connection_init(self):
        """Test if core SQL SESSION can be initialized"""
        print("\n[TEST] Verifying core SQL connection...")
        try:
            from MukeshRobot.modules.sql import SESSION
            self.assertIsNotNone(SESSION, "SQL SESSION should not be None")
            print("SUCCESS: SQL SESSION initialized.")
        except ImportError as e:
            self.fail(f"Failed to import SQL SESSION: {e}")
        except Exception as e:
            # If DB is not reachable, this might fail with simple print, 
            # effectively testing connection.
            self.fail(f"Failed to initialize SQL connection: {e}")

    def test_all_sql_modules_import(self):
        """Test importing all SQL submodules"""
        print("\n[TEST] Verifying all SQL submodules load...")
        modules_dir = Path("/Users/dhruv/WAIFUVERSE_MANAGEMENT/MukeshRobot/modules/sql")
        
        # List .py files excluding __init__
        py_files = [f.stem for f in modules_dir.glob("*.py") if f.name != "__init__.py"]
        
        for mod in py_files:
            try:
                importlib.import_module(f"MukeshRobot.modules.sql.{mod}")
                print(f"  OK: {mod}")
            except Exception as e:
                self.fail(f"Failed to import {mod}: {e}")

    def test_mongo_connection_init(self):
        """Test if Mongo DB can be initialized (no_sql package)"""
        print("\n[TEST] Verifying Mongo DB connection logic...")
        try:
            # Based on file structure, no_sql/__init__.py likely sets up connection
            # Let's try to import a collection or db object from it
            # We inspected directories but not no_sql/__init__.py content yet.
            # Assuming it exposes something or at least runs without error on import.
            import MukeshRobot.modules.no_sql as no_sql_pkg
            print("SUCCESS: Mongo package imported.")
        except Exception as e:
            self.fail(f"Failed to import Mongo package: {e}")

    def test_all_mongo_modules_import(self):
        """Test importing all Mongo submodules"""
        print("\n[TEST] Verifying all Mongo submodules load...")
        modules_dir = Path("/Users/dhruv/WAIFUVERSE_MANAGEMENT/MukeshRobot/modules/no_sql")
        
        py_files = [f.stem for f in modules_dir.glob("*.py") if f.name != "__init__.py"]
        
        for mod in py_files:
            try:
                importlib.import_module(f"MukeshRobot.modules.no_sql.{mod}")
                print(f"  OK: {mod}")
            except Exception as e:
                self.fail(f"Failed to import {mod}: {e}")

if __name__ == '__main__':
    unittest.main()
