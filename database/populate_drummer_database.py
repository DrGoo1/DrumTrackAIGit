#!/usr/bin/env python3
"""
Populate Drummer Database with Authentic Profiles
================================================

Creates and populates the main database with famous drummer profiles
and their signature songs for real batch analysis testing.
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

def create_drummer_database():
    """Create and populate the drummer database with authentic profiles"""
    
    # Target database location (same as CentralDatabaseService uses)
    target_dir = os.path.expanduser("~/DrumTracKAI/database")
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "drum_tracks.db")
    
    print(f"Creating drummer database at: {target_path}")
    
    # Famous drummers with signature songs (based on memories of working DrummersWidget)
    famous_drummers = [
        {
            'name': 'John Bonham',
            'band': 'Led Zeppelin',
            'genre': 'Rock',
            'signature_songs': [
                {'title': 'When the Levee Breaks', 'artist': 'Led Zeppelin'},
                {'title': 'Moby Dick', 'artist': 'Led Zeppelin'},
                {'title': 'Good Times Bad Times', 'artist': 'Led Zeppelin'},
                {'title': 'Kashmir', 'artist': 'Led Zeppelin'},
                {'title': 'Black Dog', 'artist': 'Led Zeppelin'}
            ]
        },
        {
            'name': 'Neil Peart',
            'band': 'Rush',
            'genre': 'Progressive Rock',
            'signature_songs': [
                {'title': 'Tom Sawyer', 'artist': 'Rush'},
                {'title': 'YYZ', 'artist': 'Rush'},
                {'title': 'Limelight', 'artist': 'Rush'},
                {'title': 'Freewill', 'artist': 'Rush'},
                {'title': '2112 Overture', 'artist': 'Rush'}
            ]
        },
        {
            'name': 'Dave Grohl',
            'band': 'Foo Fighters',
            'genre': 'Alternative Rock',
            'signature_songs': [
                {'title': 'Everlong', 'artist': 'Foo Fighters'},
                {'title': 'The Pretender', 'artist': 'Foo Fighters'},
                {'title': 'My Hero', 'artist': 'Foo Fighters'},
                {'title': 'Learn to Fly', 'artist': 'Foo Fighters'},
                {'title': 'Smells Like Teen Spirit', 'artist': 'Nirvana'}
            ]
        },
        {
            'name': 'Lars Ulrich',
            'band': 'Metallica',
            'genre': 'Heavy Metal',
            'signature_songs': [
                {'title': 'One', 'artist': 'Metallica'},
                {'title': 'Master of Puppets', 'artist': 'Metallica'},
                {'title': 'Enter Sandman', 'artist': 'Metallica'},
                {'title': 'For Whom the Bell Tolls', 'artist': 'Metallica'},
                {'title': 'Battery', 'artist': 'Metallica'}
            ]
        },
        {
            'name': 'Stewart Copeland',
            'band': 'The Police',
            'genre': 'Rock/Reggae',
            'signature_songs': [
                {'title': 'Roxanne', 'artist': 'The Police'},
                {'title': 'Message in a Bottle', 'artist': 'The Police'},
                {'title': 'Every Breath You Take', 'artist': 'The Police'},
                {'title': 'Walking on the Moon', 'artist': 'The Police'},
                {'title': 'Synchronicity II', 'artist': 'The Police'}
            ]
        },
        {
            'name': 'Keith Moon',
            'band': 'The Who',
            'genre': 'Rock',
            'signature_songs': [
                {'title': 'Baba O\'Riley', 'artist': 'The Who'},
                {'title': 'Won\'t Get Fooled Again', 'artist': 'The Who'},
                {'title': 'My Generation', 'artist': 'The Who'},
                {'title': 'Behind Blue Eyes', 'artist': 'The Who'},
                {'title': 'Pinball Wizard', 'artist': 'The Who'}
            ]
        },
        {
            'name': 'Ringo Starr',
            'band': 'The Beatles',
            'genre': 'Rock/Pop',
            'signature_songs': [
                {'title': 'Come Together', 'artist': 'The Beatles'},
                {'title': 'A Day in the Life', 'artist': 'The Beatles'},
                {'title': 'Tomorrow Never Knows', 'artist': 'The Beatles'},
                {'title': 'Rain', 'artist': 'The Beatles'},
                {'title': 'Ticket to Ride', 'artist': 'The Beatles'}
            ]
        },
        {
            'name': 'Danny Carey',
            'band': 'Tool',
            'genre': 'Progressive Metal',
            'signature_songs': [
                {'title': 'Schism', 'artist': 'Tool'},
                {'title': 'Forty Six & 2', 'artist': 'Tool'},
                {'title': 'The Pot', 'artist': 'Tool'},
                {'title': 'Lateralus', 'artist': 'Tool'},
                {'title': 'Pneuma', 'artist': 'Tool'}
            ]
        },
        {
            'name': 'Buddy Rich',
            'band': 'Buddy Rich Big Band',
            'genre': 'Jazz',
            'signature_songs': [
                {'title': 'West Side Story Medley', 'artist': 'Buddy Rich Big Band'},
                {'title': 'Caravan', 'artist': 'Buddy Rich Big Band'},
                {'title': 'Channel One Suite', 'artist': 'Buddy Rich Big Band'},
                {'title': 'Norwegian Wood', 'artist': 'Buddy Rich Big Band'},
                {'title': 'Mercy, Mercy', 'artist': 'Buddy Rich Big Band'}
            ]
        },
        {
            'name': 'Gene Krupa',
            'band': 'Gene Krupa Orchestra',
            'genre': 'Jazz/Swing',
            'signature_songs': [
                {'title': 'Sing, Sing, Sing', 'artist': 'Benny Goodman Orchestra'},
                {'title': 'Drummin\' Man', 'artist': 'Gene Krupa Orchestra'},
                {'title': 'Let Me Off Uptown', 'artist': 'Gene Krupa Orchestra'},
                {'title': 'After You\'ve Gone', 'artist': 'Gene Krupa Orchestra'},
                {'title': 'Rockin\' Chair', 'artist': 'Gene Krupa Orchestra'}
            ]
        },
        {
            'name': 'Travis Barker',
            'band': 'Blink-182',
            'genre': 'Pop Punk',
            'signature_songs': [
                {'title': 'Dammit', 'artist': 'Blink-182'},
                {'title': 'What\'s My Age Again?', 'artist': 'Blink-182'},
                {'title': 'All the Small Things', 'artist': 'Blink-182'},
                {'title': 'I Miss You', 'artist': 'Blink-182'},
                {'title': 'First Date', 'artist': 'Blink-182'}
            ]
        },
        {
            'name': 'Chad Smith',
            'band': 'Red Hot Chili Peppers',
            'genre': 'Alternative Rock/Funk',
            'signature_songs': [
                {'title': 'Under the Bridge', 'artist': 'Red Hot Chili Peppers'},
                {'title': 'Give It Away', 'artist': 'Red Hot Chili Peppers'},
                {'title': 'Californication', 'artist': 'Red Hot Chili Peppers'},
                {'title': 'By the Way', 'artist': 'Red Hot Chili Peppers'},
                {'title': 'Can\'t Stop', 'artist': 'Red Hot Chili Peppers'}
            ]
        },
        {
            'name': 'Mike Portnoy',
            'band': 'Dream Theater',
            'genre': 'Progressive Metal',
            'signature_songs': [
                {'title': 'Pull Me Under', 'artist': 'Dream Theater'},
                {'title': 'Metropolis Pt. 1', 'artist': 'Dream Theater'},
                {'title': 'The Dance of Eternity', 'artist': 'Dream Theater'},
                {'title': 'As I Am', 'artist': 'Dream Theater'},
                {'title': 'Panic Attack', 'artist': 'Dream Theater'}
            ]
        },
        {
            'name': 'Phil Collins',
            'band': 'Genesis',
            'genre': 'Progressive Rock/Pop',
            'signature_songs': [
                {'title': 'In the Air Tonight', 'artist': 'Phil Collins'},
                {'title': 'I Can\'t Dance', 'artist': 'Genesis'},
                {'title': 'Land of Confusion', 'artist': 'Genesis'},
                {'title': 'Invisible Touch', 'artist': 'Genesis'},
                {'title': 'Turn It On Again', 'artist': 'Genesis'}
            ]
        },
        {
            'name': 'Carter Beauford',
            'band': 'Dave Matthews Band',
            'genre': 'Alternative Rock/Jazz Fusion',
            'signature_songs': [
                {'title': 'Ants Marching', 'artist': 'Dave Matthews Band'},
                {'title': 'What Would You Say', 'artist': 'Dave Matthews Band'},
                {'title': 'Tripping Billies', 'artist': 'Dave Matthews Band'},
                {'title': 'Crash Into Me', 'artist': 'Dave Matthews Band'},
                {'title': 'Two Step', 'artist': 'Dave Matthews Band'}
            ]
        },
        {
            'name': 'Joey Jordison',
            'band': 'Slipknot',
            'genre': 'Nu Metal',
            'signature_songs': [
                {'title': 'Wait and Bleed', 'artist': 'Slipknot'},
                {'title': 'Duality', 'artist': 'Slipknot'},
                {'title': 'Before I Forget', 'artist': 'Slipknot'},
                {'title': 'Psychosocial', 'artist': 'Slipknot'},
                {'title': 'The Heretic Anthem', 'artist': 'Slipknot'}
            ]
        },
        {
            'name': 'Gene Hoglan',
            'band': 'Death/Testament',
            'genre': 'Death Metal',
            'signature_songs': [
                {'title': 'Crystal Mountain', 'artist': 'Death'},
                {'title': 'Pull the Plug', 'artist': 'Death'},
                {'title': 'The Practice of Composure', 'artist': 'Testament'},
                {'title': 'Into the Pit', 'artist': 'Testament'},
                {'title': 'Symbolic', 'artist': 'Death'}
            ]
        },
        {
            'name': 'Matt Cameron',
            'band': 'Pearl Jam/Soundgarden',
            'genre': 'Grunge',
            'signature_songs': [
                {'title': 'Black', 'artist': 'Pearl Jam'},
                {'title': 'Alive', 'artist': 'Pearl Jam'},
                {'title': 'Black Hole Sun', 'artist': 'Soundgarden'},
                {'title': 'Spoonman', 'artist': 'Soundgarden'},
                {'title': 'Jeremy', 'artist': 'Pearl Jam'}
            ]
        },
        {
            'name': 'Jeff Porcaro',
            'band': 'Toto',
            'genre': 'Rock/Pop',
            'signature_songs': [
                {'title': 'Rosanna', 'artist': 'Toto'},
                {'title': 'Africa', 'artist': 'Toto'},
                {'title': 'Hold the Line', 'artist': 'Toto'},
                {'title': 'I Won\'t Hold You Back', 'artist': 'Toto'},
                {'title': 'Georgy Porgy', 'artist': 'Toto'}
            ]
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()
        
        # Create drummers table (matching CentralDatabaseService schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drummers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        print("Created drummers table")
        
        # Insert drummer data
        inserted_count = 0
        for drummer_data in famous_drummers:
            drummer_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Convert signature songs to JSON string
            signature_songs_json = json.dumps(drummer_data['signature_songs'])
            
            # Create description with band, genre, and signature songs
            description_data = {
                'band': drummer_data['band'],
                'genre': drummer_data['genre'],
                'signature_songs': drummer_data['signature_songs']
            }
            description_json = json.dumps(description_data)
            
            cursor.execute('''
                INSERT INTO drummers (id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                drummer_id,
                drummer_data['name'],
                description_json,
                now,
                now
            ))
            
            inserted_count += 1
            print(f"  Added: {drummer_data['name']} ({drummer_data['band']}) - {len(drummer_data['signature_songs'])} songs")
        
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM drummers")
        total_count = cursor.fetchone()[0]
        
        print(f"\nSUCCESS: Created database with {total_count} drummers")
        
        # Show sample data
        cursor.execute("SELECT name, description FROM drummers LIMIT 3")
        samples = cursor.fetchall()
        
        print("\nSample data:")
        for name, description_json in samples:
            description = json.loads(description_json)
            band = description['band']
            songs = description['signature_songs']
            print(f"  {name} ({band}) - {len(songs)} signature songs")
            for song in songs[:2]:  # Show first 2 songs
                print(f"    - {song['title']} by {song['artist']}")
        
        conn.close()
        
        return target_path, total_count
        
    except Exception as e:
        print(f"ERROR creating database: {e}")
        return None, 0

def main():
    """Main function to populate drummer database"""
    print("POPULATING DRUMMER DATABASE FOR REAL BATCH TESTING")
    print("="*60)
    
    db_path, count = create_drummer_database()
    
    if db_path and count > 0:
        print(f"\nSUCCESS: DATABASE READY: {db_path}")
        print(f"SUCCESS: DRUMMERS LOADED: {count}")
        print(f"SUCCESS: READY FOR REAL BATCH TESTING")
        
        print(f"\nNext steps:")
        print(f"1. Run: python real_batch_test_with_timing.py")
        print(f"2. The test will now find {count} drummers with signature songs")
        print(f"3. Enhanced MVSep timing accommodations are active")
        print(f"4. Full workflow will be tested with authentic data")
        
    else:
        print(f"\nFAILED: Could not create drummer database")
        print(f"FAILED: Cannot proceed with real batch testing")

if __name__ == "__main__":
    main()
