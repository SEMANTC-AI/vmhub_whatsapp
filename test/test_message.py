# test/test_message.py

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

# Load environment variables from project root
load_dotenv(project_root / '.env')

class WhatsAppTester:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')  # Your Twilio WhatsApp number
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Missing required environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)

    def format_phone(self, phone: str) -> str:
        """Format phone number to WhatsApp format"""
        # Remove non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if needed
        if len(cleaned) == 11:  # Brazilian number with DDD
            return f"55{cleaned}"
        elif len(cleaned) == 10:  # Old format without 9
            return f"559{cleaned}"
        elif len(cleaned) >= 12:  # Already has country code
            return cleaned
        
        raise ValueError(f"Invalid phone number format: {phone}")

    def send_test_message(self, to_number: str, campaign_type: str = 'birthday'):
        """Send a test message"""
        try:
            # Format the phone number
            formatted_number = self.format_phone(to_number)
            
            # Get template and parameters based on campaign type
            template, parameters = self._get_campaign_content(campaign_type)
            
            print(f"Sending {campaign_type} message to {formatted_number}")
            
            message = self.client.messages.create(
                from_=f'whatsapp:{self.from_number}',
                body=template.format(**parameters),
                to=f'whatsapp:{formatted_number}'
            )
            
            print(f"Message sent! SID: {message.sid}")
            print(f"Status: {message.status}")
            return message.sid
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise

    def _get_campaign_content(self, campaign_type: str):
        """Get template and parameters for different campaign types"""
        templates = {
            'birthday': (
                "Olá {name}! 🎉 Feliz Aniversário! Como presente especial, preparamos um cupom para você: {coupon}",
                {"name": "Test User", "coupon": "BDAY10"}
            ),
            'welcome': (
                "Olá {name}! 👋 Bem-vindo à nossa lavanderia! Estamos felizes em ter você como cliente.",
                {"name": "Test User"}
            ),
            'reactivation': (
                "Olá {name}! 😊 Sentimos sua falta! Faz {days} dias que não te vemos. Que tal voltar?",
                {"name": "Test User", "days": "30"}
            ),
            'loyalty': (
                "Olá {name}! 🌟 Você é um cliente especial! Aqui está um cupom de fidelidade: {coupon}",
                {"name": "Test User", "coupon": "LOYAL10"}
            )
        }
        
        return templates.get(campaign_type, templates['birthday'])

def main():
    # Get phone number from command line
    phone = input("Enter phone number to test: ")
    
    # Get campaign type
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
    
    # Initialize tester and send message
    tester = WhatsAppTester()
    tester.send_test_message(phone, campaign_type)

if __name__ == "__main__":
    main()