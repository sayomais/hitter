# Stripe Auto Hitter

A Python program for testing Stripe payment processing with automatic credit card testing.

## Important Note
This program is intended for legitimate testing purposes only using Stripe's test cards. Using this program with real credit cards or for unauthorized testing is illegal and against Stripe's terms of service.

## Setup

1. Make sure you have Python installed on your computer
2. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```
3. Get your Stripe secret key from your Stripe dashboard

## Usage

1. Run the program:
   ```
   python stripe_auto_hitter.py
   ```
2. Enter your Stripe secret key when prompted
3. Select a test card using number keys 1-4:
   - 1: Success card (4242424242424242)
   - 2: Decline card (4000000000000002)
   - 3: Insufficient funds card (4000000000009995)
   - 4: Expired card (4000000000000069)
4. Press F6 to start/stop processing
5. Press F7 to exit the program

## Features

- Automatic payment processing with Stripe
- Multiple test card options
- Transaction counter
- Real-time status updates
- Easy to use interface

## Test Cards

The program includes Stripe's official test cards:
- Success card: 4242424242424242
- Decline card: 4000000000000002
- Insufficient funds: 4000000000009995
- Expired card: 4000000000000069

## Safety Features

- The program has a failsafe feature: moving your mouse to any corner of the screen will stop the program
- You can always press F7 to exit the program
- There's a 3-second delay before the program starts 