"""Email order confirmation — sends via SMTP using centralized config."""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Tuple

from config import SENDER_EMAIL, SENDER_PASSWORD, SHOP_EMAIL, SMTP_SERVER, SMTP_PORT


def send_order_confirmation(
    customer_email: str,
    basket: List[str],
    total_cost: float,
    total_weight: float,
    shipping_cost: float,
) -> Tuple[bool, str]:
    """Send order confirmation to both the customer and the shop.

    Returns (success, message).
    """
    if not all([SENDER_EMAIL, SENDER_PASSWORD, SHOP_EMAIL]):
        return False, "Email configuration missing. Please check environment variables."

    try:
        # Build shared body
        item_counts: Dict[str, int] = {}
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1

        items_summary = "\n".join(f"- {name} (x{qty})" for name, qty in item_counts.items())
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        final_total = total_cost + shipping_cost

        body = f"""Order Confirmation
-----------------
Date: {date_str}

Items Ordered:
{items_summary}

Order Summary:
-------------
Total Cost: €{total_cost:.2f}
Total Weight: {total_weight:.2f}kg
Shipping Cost: €{shipping_cost:.2f}
Final Total: €{final_total:.2f}
"""

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            # ── Send to customer ──
            msg_customer = MIMEMultipart()
            msg_customer["From"] = SENDER_EMAIL
            msg_customer["To"] = customer_email
            msg_customer["Subject"] = "Order Confirmation"
            msg_customer.attach(MIMEText(body, "plain"))
            server.send_message(msg_customer)

            # ── Send to shop ──
            msg_shop = MIMEMultipart()
            msg_shop["From"] = SENDER_EMAIL
            msg_shop["To"] = SHOP_EMAIL
            msg_shop["Subject"] = f"New Order — {customer_email}"
            msg_shop.attach(MIMEText(body, "plain"))
            server.send_message(msg_shop)

        return True, "Order confirmation sent successfully."

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed — check your email credentials in .env"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except Exception as e:
        return False, f"Error sending confirmation: {e}"
