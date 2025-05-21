import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SMTP_EMAIL')
SENDER_PASSWORD = os.getenv('SMTP_PASSWORD')
SHOP_EMAIL = os.getenv('SHOP_EMAIL')

def send_order_confirmation(customer_email, basket, total_cost, total_weight, shipping_cost):
    if not all([SENDER_EMAIL, SENDER_PASSWORD, SHOP_EMAIL]):
        return False, "Email configuration missing. Please check environment variables."

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['Subject'] = "Order Confirmation"
        
        # Create item summary
        items_summary = []
        item_counts = {}
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        for item, count in item_counts.items():
            items_summary.append(f"- {item} (x{count})")
        
        # Create email body
        body = f"""
        Order Confirmation
        -----------------
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        Items Ordered:
        {chr(10).join(items_summary)}
        
        Order Summary:
        -------------
        Total Cost: €{total_cost:.2f}
        Total Weight: {total_weight:.2f}kg
        Shipping Cost: €{shipping_cost:.2f}
        Final Total: €{total_cost + shipping_cost:.2f}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            # Send to customer
            msg['To'] = customer_email
            server.send_message(msg)
            
            # Send to shop
            msg['To'] = SHOP_EMAIL
            server.send_message(msg)
            
        return True, "Order confirmation sent successfully"
        
    except Exception as e:
        return False, f"Error sending confirmation: {str(e)}"