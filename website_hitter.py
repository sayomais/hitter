import time
import json
import logging
import random
from datetime import datetime
import sys
import os
import requests

class WebsiteHitter:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.transaction_count = 0
        self.success_count = 0
        self.decline_count = 0
        self.error_count = 0
        self.is_running = False
        self.cards = []
        self.amount = 1000  # Default amount
        
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
            card = random.choice(self.cards)
            # Simulate payment processing
            time.sleep(1)  # Simulate network delay
            
            # Random success/decline simulation
            if random.random() < 0.3:  # 30% success rate
                return "succeeded", card
            elif random.random() < 0.6:  # 30% decline rate
                return "declined", card
            else:  # 40% error rate
                return "error", card
                
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
        return log_message
        
    def get_stats(self):
        success_rate = (self.success_count/self.transaction_count)*100 if self.transaction_count > 0 else 0
        stats = f"""
=== Current Statistics ===
Total Transactions: {self.transaction_count}
Successful: {self.success_count}
Declined: {self.decline_count}
Errors: {self.error_count}
Success Rate: {success_rate:.2f}%
=======================
"""
        return stats

def main():
    # Load configuration
    bot = WebsiteHitter()
    
    print("Website Hitter Started!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            if bot.transaction_count >= bot.config['max_transactions']:
                print(f"Reached maximum transactions ({bot.config['max_transactions']})")
                if bot.config['auto_restart']:
                    print(f"Restarting in {bot.config['restart_delay']} seconds...")
                    time.sleep(bot.config['restart_delay'])
                    bot.transaction_count = 0
                    bot.success_count = 0
                    bot.decline_count = 0
                    bot.error_count = 0
                    continue
                else:
                    break
                    
            status, card = bot.process_payment()
            log_message = bot.log_transaction(status, card)
            
            if bot.transaction_count % 10 == 0:
                print(bot.get_stats())
                
            time.sleep(bot.config['interval'])
            
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        print(bot.get_stats())
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.error(f"Error: {str(e)}")
        if bot.config['auto_restart']:
            print(f"Restarting in {bot.config['restart_delay']} seconds...")
            time.sleep(bot.config['restart_delay'])
            main()
        else:
            print(bot.get_stats())

if __name__ == "__main__":
    main() 