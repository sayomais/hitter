import pyautogui
import keyboard
import time
import sys
import stripe
from datetime import datetime

# Safety feature to prevent the program from running indefinitely
pyautogui.FAILSAFE = True

# Test card numbers (These are Stripe's test card numbers)
TEST_CARDS = {
    "success": "4242424242424242",
    "decline": "4000000000000002",
    "insufficient_funds": "4000000000009995",
    "expired": "4000000000000069"
}

class StripeAutoHitter:
    def __init__(self, stripe_secret_key):
        self.stripe = stripe
        self.stripe.api_key = stripe_secret_key
        self.clicking = False
        self.current_card = None
        self.transaction_count = 0
        
    def process_payment(self, amount=1000):  # amount in cents (10.00)
        try:
            payment = self.stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'number': self.current_card,
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
            return payment.status
        except stripe.error.CardError as e:
            return f"declined: {e.error.message}"
        except Exception as e:
            return f"error: {str(e)}"

    def auto_hit(self):
        print("Stripe Auto Hitter Started!")
        print("Press 'F6' to start/stop clicking")
        print("Press 'F7' to exit the program")
        print("Press '1-4' to select test card:")
        print("1: Success card")
        print("2: Decline card")
        print("3: Insufficient funds card")
        print("4: Expired card")
        
        while True:
            # Card selection
            if keyboard.is_pressed('1'):
                self.current_card = TEST_CARDS["success"]
                print("Selected: Success card")
                time.sleep(0.5)
            elif keyboard.is_pressed('2'):
                self.current_card = TEST_CARDS["decline"]
                print("Selected: Decline card")
                time.sleep(0.5)
            elif keyboard.is_pressed('3'):
                self.current_card = TEST_CARDS["insufficient_funds"]
                print("Selected: Insufficient funds card")
                time.sleep(0.5)
            elif keyboard.is_pressed('4'):
                self.current_card = TEST_CARDS["expired"]
                print("Selected: Expired card")
                time.sleep(0.5)
            
            if keyboard.is_pressed('f6'):
                self.clicking = not self.clicking
                print(f"Clicking {'Started' if self.clicking else 'Stopped'}")
                time.sleep(0.5)
                
            if keyboard.is_pressed('f7'):
                print("Exiting program...")
                sys.exit()
                
            if self.clicking and self.current_card:
                self.transaction_count += 1
                result = self.process_payment()
                print(f"Transaction {self.transaction_count}: {result}")
                time.sleep(1)  # Wait 1 second between attempts

if __name__ == "__main__":
    print("Stripe Auto Hitter Program")
    print("-------------------------")
    print("Instructions:")
    print("1. Enter your Stripe secret key:")
    stripe_key = input().strip()
    
    print("\n2. Select a test card (1-4)")
    print("3. Press F6 to start/stop processing")
    print("4. Press F7 to exit")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    hitter = StripeAutoHitter(stripe_key)
    hitter.auto_hit() 