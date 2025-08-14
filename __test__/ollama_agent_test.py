#!/usr/bin/env python3

"""
Test script to verify the tool_call serialization fix
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helper.tool_call import run_agent_with_question

def test_basic_question():
    """Test with a simple question that shouldn't require tool calls"""
    try:
        print("Testing basic question...")
        result, messages = run_agent_with_question(
            "Hello, how are you?", 
            save_messages=True, 
            messages_file="test_messages.json",
            stream=False
        )
        print(f"✅ Success! Result: {result}")
        print(f"✅ Messages saved successfully. Total messages: {len(messages)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_tool_question():
    """Test with a question that might trigger tool calls"""
    try:
        print("\nTesting tool-based question...")
        result, messages = run_agent_with_question(
            "List the files in the current directory", 
            save_messages=True, 
            messages_file="test_tool_messages.json",
            stream=False
        )
        print(f"✅ Success! Result: {result}")
        print(f"✅ Messages saved successfully. Total messages: {len(messages)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting serialization tests...")
    
    test1 = test_basic_question()
    test2 = test_tool_question()
    
    if test1 and test2:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
