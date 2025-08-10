#!/usr/bin/env python3
"""
Check all database files to find the one with drummer data
"""
import sqlite3
import os
from pathlib import Path

def check_database(db_path):
    """Check a database file for drummer data"""
    try:
        if not os.path.exists(db_path):
            print(f" {db_path} - File not found")
            return None
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"[FOLDER] {db_path}")
        print(f"   Tables: {tables}")
        
        # Check for drummers table
        if 'drummers' in tables:
            cursor.execute("SELECT COUNT(*) FROM drummers")
            count = cursor.fetchone()[0]
            print(f"    Drummers: {count}")
            
            if count > 0:
                cursor.execute("SELECT name FROM drummers LIMIT 5")
                sample_drummers = [d[0] for d in cursor.fetchall()]
                print(f"   [DRUMS] Sample: {sample_drummers}")
                
                # Check for signature songs
                cursor.execute("SELECT name, signature_songs FROM drummers WHERE signature_songs IS NOT NULL AND signature_songs != '' LIMIT 3")
                drummers_with_songs = cursor.fetchall()
                if drummers_with_songs:
                    print(f"   [AUDIO] With songs: {len(drummers_with_songs)} drummers have signature songs")
                    for name, songs in drummers_with_songs:
                        print(f"      {name}: {songs[:100]}...")
                
                conn.close()
                return db_path
        else:
            print(f"    No 'drummers' table found")
            
        conn.close()
        return None
        
    except Exception as e:
        print(f" {db_path} - Error: {e}")
        return None

def main():
    print("[SEARCH] Checking all database files for drummer data...")
    print("="*60)
    
    # Database paths to check
    db_paths = [
        "D:/DrumTracKAI_v1.1.10/admin/drumtrackai.db",
        "D:/DrumTracKAI_v1.1.10/drumtrackai.db", 
        "D:/DrumTracKAI_v1.1.10/fixed add/delete/admin/drumtrackai.db",
        "D:/DrumTracKAI_v1.1.10/fixed add/delete/drumtrackai.db"
    ]
    
    valid_databases = []
    
    for db_path in db_paths:
        result = check_database(db_path)
        if result:
            valid_databases.append(result)
        print()
    
    print("="*60)
    print("[BAR_CHART] SUMMARY:")
    if valid_databases:
        print(f"[SUCCESS] Found {len(valid_databases)} database(s) with drummer data:")
        for db in valid_databases:
            print(f"   • {db}")
        print(f"\n[TARGET] RECOMMENDED: Use {valid_databases[0]} for real batch testing")
    else:
        print(" No databases found with drummer data")
        print("[IDEA] You may need to run the main application first to populate the database")

if __name__ == "__main__":
    main()
