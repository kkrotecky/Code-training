# Shopping Cart Application

A Python-based shopping cart application with a graphical user interface that manages orders and calculates shipping costs.

## Features

### User Management
- User profile creation and storage
- Profile loading functionality
- JSON-based profile persistence

### Shopping Interface
- Interactive item selection from CSV catalog
- Real-time cart management
- Quantity adjustment via double-click
- Multiple item selection support
- Search functionality for items

### Shipping Calculator
- Free shipping for orders over €500 (with weight ≤ 50kg)
- Base shipping rate: €1.2 per kg
- Weight penalty: €10 for orders over 50kg
- Progress bar showing progress towards free shipping

### User Experience
- Modern Sun Valley theme
- Tooltips with keyboard shortcuts
- Keyboard shortcuts support:
  - Ctrl+A: Add to cart
  - Delete: Remove from cart
  - Enter: Checkout

### Order Processing
- Email confirmation system
- Dual confirmation (customer & shop)
- Order summary with detailed breakdown

## Technical Requirements

- Python 3.x
- Required packages:
  ```
  pip install pillow
  pip install python-dotenv
  pip install sv-ttk
  ```

## File Structure
```
shop_app/
│
├── shopping_app.py    # Main application
├── items.csv         # Product catalog
├── mailing.py        # Email functionality
└── .env             # Environment variables (email configuration)
```

## Configuration

1. Create a `.env` file with email settings:
```
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SHOP_EMAIL=shop@example.com
```

2. Ensure `items.csv` contains your product catalog with format:
```csv
item,weight,cost
product1,weight1,cost1
product2,weight2,cost2
```

## Usage

Run the application:
```bash
python shopping_app.py
```

## Security Notes

- User profiles are stored locally in `user_profile.json`
- Email credentials are managed via environment variables
- No sensitive data is stored in source code
