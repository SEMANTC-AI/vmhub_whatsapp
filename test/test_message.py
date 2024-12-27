# test/test_message.py

import asyncio
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

from src.services.whatsapp_client import WhatsAppClient

class WhatsAppTester:
    def __init__(self):
        self.whatsapp = WhatsAppClient()

    def format_phone(self, phone: str) -> str:
        """Format phone number to international format"""
        cleaned = ''.join(filter(str.isdigit, phone))
        
        if phone.startswith('+'):
            if len(cleaned) >= 10:
                return cleaned
        
        if cleaned.startswith('55'):
            return cleaned
        if len(cleaned) == 11:
            return f"55{cleaned}"
        
        raise ValueError(f"Invalid phone number format: {phone}")

    async def send_test_message(self, to_number: str, campaign_type: str = 'birthday', loyalty_count: int = 0):
        """Send a test message"""
        from src.models.message import Message
        from src.config.constants import CampaignType
        
        try:
            formatted_number = self.format_phone(to_number)
            parameters = self._get_campaign_parameters(campaign_type, loyalty_count)
            
            print(f"Sending {campaign_type} message to {formatted_number}")
            
            message = Message(
                user_id="test_user",
                campaign_type=CampaignType(campaign_type),
                target_id="test_target",
                phone_number=formatted_number,
                template_name=campaign_type,
                parameters=parameters,
                loyalty_count=loyalty_count if campaign_type == 'loyalty' else None
            )
            
            result = await self.whatsapp.send_message(message)
            
            print(f"Message sent! ID: {result['message_id']}")
            print(f"Status: {result['status']}")
            return result['message_id']
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise

    def _get_campaign_parameters(self, campaign_type: str, loyalty_count: int = 0):
        """Get parameters for different campaign types"""
        parameters = {
            'birthday': {
                "name": "Test User",
                "coupon": "BDAY10"
            },
            'welcome': {
                "name": "Test User"
            },
            'reactivation': {
                "name": "Test User",
                "days_inactive": "30"
            },
            'loyalty': {
                "name": "Test User",
                "services": str(loyalty_count)
            }
        }
        
        return parameters.get(campaign_type, parameters['birthday'])

async def main():
    try:
        phone = input("Enter phone number to test: ")
        
        print("\nAvailable campaign types:")
        print("1. Birthday")
        print("2. Welcome")
        print("3. Reactivation")
        print("4. Loyalty")
        campaign_choice = input("\nSelect campaign type (1-4): ")
        
        campaign_types = {
            '1': 'birthday',
            '2': 'welcome',
            '3': 'reactivation',
            '4': 'loyalty'
        }
        
        campaign_type = campaign_types.get(campaign_choice, 'birthday')
        
        loyalty_count = 0
        if campaign_type == 'loyalty':
            loyalty_count = int(input("\nEnter number of services (1-10): "))
            if not 1 <= loyalty_count <= 10:
                print("Invalid service count. Using 1.")
                loyalty_count = 1

        tester = WhatsAppTester()
        await tester.send_test_message(phone, campaign_type, loyalty_count)

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
