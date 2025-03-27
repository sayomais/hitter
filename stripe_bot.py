import stripe
import time
import json
import logging
import random
from datetime import datetime
import sys
import os

class StripeBot:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.stripe = stripe
        self.stripe.api_key = self.config['stripe_secret_key']
        self.transaction_count = 0
        self.success_count = 0
        self.decline_count = 0
        self.error_count = 0
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Error: {config_path} not found!")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {config_path}")
            sys.exit(1)
            
    def setup_logging(self):
        logging.basicConfig(
            filename=self.config['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def process_payment(self):
        try:
            card = random.choice(self.config['test_cards'])
            payment = self.stripe.PaymentIntent.create(
                amount=self.config['amount'],
                currency='usd',
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'number': card,
                        'exp_month': 12,
                        'exp_year': 2025,
                        'cvc': '314',
                        'billing_details': {
                            'name': 'Test User',
                            'address': {
                                'line1': '123 Test St',
                                'city': 'Test City',
                                'state': 'TS',
                                'postal_code': '12345',
                                'country': 'US'
                            }
                        }
                    }
                }
            )
            return payment.status, card
        except stripe.error.CardError as e:
            return f"declined: {e.error.message}", card
        except Exception as e:
            return f"error: {str(e)}", card
            
    def log_transaction(self, status, card):
        self.transaction_count += 1
        if "succeeded" in status:
            self.success_count += 1
        elif "declined" in status:
            self.decline_count += 1
        else:
            self.error_count += 1
            
        log_message = f"Transaction {self.transaction_count} - Card: {card[:6]}XXXXXX{card[-4:]} - Status: {status}"
        print(log_message)
        logging.info(log_message)
        
    def print_stats(self):
        print("\n=== Current Statistics ===")
        print(f"Total Transactions: {self.transaction_count}")
        print(f"Successful: {self.success_count}")
        print(f"Declined: {self.decline_count}")
        print(f"Errors: {self.error_count}")
        print(f"Success Rate: {(self.success_count/self.transaction_count)*100:.2f}%")
        print("=======================\n")
        
    def run(self):
        print("Stripe Bot Started!")
        print(f"Logging to: {self.config['log_file']}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                if self.transaction_count >= self.config['max_transactions']:
                    print(f"Reached maximum transactions ({self.config['max_transactions']})")
                    if self.config['auto_restart']:
                        print(f"Restarting in {self.config['restart_delay']} seconds...")
                        time.sleep(self.config['restart_delay'])
                        self.transaction_count = 0
                        self.success_count = 0
                        self.decline_count = 0
                        self.error_count = 0
                        continue
                    else:
                        break
                        
                status, card = self.process_payment()
                self.log_transaction(status, card)
                
                if self.transaction_count % 10 == 0:
                    self.print_stats()
                    
                time.sleep(self.config['interval'])
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            self.print_stats()
        except Exception as e:
            print(f"Error: {str(e)}")
            logging.error(f"Error: {str(e)}")
            if self.config['auto_restart']:
                print(f"Restarting in {self.config['restart_delay']} seconds...")
                time.sleep(self.config['restart_delay'])
                self.run()
            else:
                self.print_stats()

if __name__ == "__main__":
    bot = StripeBot()
    bot.run() 