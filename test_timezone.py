#!/usr/bin/env python3
"""Test script to verify Pakistan timezone functionality"""

import sys
import os
from datetime import datetime
import pytz

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import utc_to_pakistan, PAKISTAN_TZ, pakistan_now

def test_timezone_functions():
    """Test timezone conversion functions"""
    print("=== Pakistan Timezone Test ===")
    
    # Test current time in Pakistan
    pak_current = pakistan_now()
    print(f"Current Pakistan time: {pak_current}")
    print(f"Timezone: {pak_current.tzinfo}")
    
    # Test UTC to Pakistan conversion
    utc_now = datetime.utcnow()
    print(f"\nUTC time: {utc_now}")
    
    converted = utc_to_pakistan(utc_now)
    print(f"Converted to Pakistan (formatted): {converted}")
    
    # Test with timezone-aware UTC datetime
    utc_aware = pytz.utc.localize(utc_now)
    converted_aware = utc_to_pakistan(utc_aware)
    print(f"Converted from timezone-aware UTC: {converted_aware}")
    
    # Test format matches expected pattern
    expected_format = "%d-%m-%Y %I:%M %p"
    print(f"\nExpected format: {expected_format}")
    print(f"Sample output: {converted}")
    
    # Test with None value
    converted_none = utc_to_pakistan(None)
    print(f"Conversion of None: {converted_none}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_timezone_functions()
