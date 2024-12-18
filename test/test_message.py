# test/test_message.py

import asyncio
import os
import sys
from pathlib import Path
import base64
import mimetypes
from typing import Optional

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
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Missing required environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
        
        # Media directory setup
        self.media_dir = project_root / 'media'
        
        # Validate media directory exists
        if not self.media_dir.exists():
            raise ValueError(f"Media directory not found at {self.media_dir}")

    def get_media_path(self, usage_count: int) -> Optional[Path]:
        """Get the path to the loyalty card image based on usage count"""
        card_file = self.media_dir / f'card{usage_count}.jpg'
        if card_file.exists():
            return card_file
        return None

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

    def send_test_message(self, to_number: str, campaign_type: str = 'birthday', loyalty_count: int = 0):
        """Send a test message"""
        try:
            # Format the phone number
            formatted_number = self.format_phone(to_number)
            
            # Get template and parameters based on campaign type
            template, parameters = self._get_campaign_content(campaign_type)
            
            print(f"Sending {campaign_type} message to {formatted_number}")
            
            # Prepare message parameters
            message_params = {
                'from_': f'whatsapp:{self.from_number}',
                'body': template.format(**parameters),
                'to': f'whatsapp:{formatted_number}'
            }

            # Add media for loyalty campaign
            if campaign_type == 'loyalty' and loyalty_count > 0:
                media_path = self.get_media_path(loyalty_count)
                if media_path:
                    # Convert image to base64 for testing
                    with open(media_path, 'rb') as image_file:
                        image_data = image_file.read()
                        media_type = mimetypes.guess_type(media_path)[0]
                        message_params['media_url'] = [
                            f"data:{media_type};base64,{base64.b64encode(image_data).decode()}"
                        ]
                    print(f"Including loyalty card image: {media_path.name}")
            
            message = self.client.messages.create(**message_params)
            
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
                "Parabéns {name}! 🌟 Você completou {services} serviços! Aqui está seu cartão fidelidade atualizado.",
                {"name": "Test User", "services": "5"}
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
    
    # Get loyalty count if applicable
    loyalty_count = 0
    if campaign_type == 'loyalty':
        try:
            loyalty_count = int(input("\nEnter number of services (1-10): "))
            if not 1 <= loyalty_count <= 10:
                print("Invalid service count. Using 1.")
                loyalty_count = 1
        except ValueError:
            print("Invalid input. Using 1.")
            loyalty_count = 1
    
    # Initialize tester and send message
    tester = WhatsAppTester()
    tester.send_test_message(phone, campaign_type, loyalty_count)

if __name__ == "__main__":
    main()