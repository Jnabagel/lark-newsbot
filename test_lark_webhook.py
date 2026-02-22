"""Test script to verify Lark webhook is working."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.lark_client import LarkClient

def test_lark_webhook():
    """Test Lark webhook with a simple message."""
    print("Testing Lark webhook...")
    
    try:
        lark_client = LarkClient()
        
        # Test 1: Simple text message
        print("\n1. Testing simple text message...")
        success = lark_client.send_message("Hello from AI Agent Platform! This is a test message.")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test 2: Markdown message
        print("\n2. Testing markdown message...")
        markdown_content = """
# Test News Summary

## Top Headlines
- Test headline 1
- Test headline 2

**This is a test message from the NewsBot.**
        """
        success = lark_client.send_markdown(markdown_content, title="Test News Summary")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        print("\n" + "="*60)
        if success:
            print("✅ Lark webhook is working! Check your Lark group/chat.")
        else:
            print("❌ Lark webhook test failed. Check logs/app.log for details.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lark_webhook()
