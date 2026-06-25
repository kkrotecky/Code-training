# Shop App Architecture

## File Structure

```mermaid
graph TD
    subgraph Core
        shopping_app_py[shopping_app.py<br/>Main GUI entry point]
        models_py[models.py<br/>Item & ShoppingCart dataclasses]
        data_py[data.py<br/>CSV I/O helpers]
        config_py[config.py<br/>Paths & env config]
        mailing_py[mailing.py<br/>SMTP email sender]
    end

    subgraph Assets
        items_py[items.py<br/>Item definitions & CSV export]
        items_csv[items.csv<br/>Product catalog]
        user_profile_json[user_profile.json<br/>Saved user profile]
        env[.env<br/>SMTP credentials]
        assets_dir[assets/<br/>PNG icons]
    end

    subgraph GUI_Classes
        ShoppingApp[ShoppingApp<br/>Main window]
        UserDetailsDialog[UserDetailsDialog<br/>Name/email prompt]
        ToolTip[ToolTip<br/>Hover tooltips]
    end

    shopping_app_py --> ShoppingApp
    shopping_app_py --> UserDetailsDialog
    shopping_app_py --> ToolTip
    ShoppingApp --> items_csv
    ShoppingApp --> user_profile_json
    ShoppingApp --> mailing_py
    ShoppingApp --> assets_dir
    data_py --> models_py
    data_py --> config_py
    items_py --> items_csv
    mailing_py --> env
```

---

## Class & Module Dependencies

```mermaid
flowchart RL
    subgraph Modules
        shopping_app[shopping_app.py]
        data[data.py]
        models[models.py]
        config[config.py]
        mailing[mailing.py]
        items[items.py]
    end

    subgraph External
        tkinter[tkinter]
        pillow[PIL / Pillow]
        sv_ttk[sv-ttk<br/>Sun Valley theme]
        smtplib[smtplib]
        dotenv[python-dotenv]
    end

    shopping_app --> tkinter
    shopping_app --> pillow
    shopping_app --> sv_ttk
    shopping_app --> models
    shopping_app --> mailing
    shopping_app --> config
    data --> models
    data --> config
    mailing --> smtplib
    mailing --> dotenv
```

---

## Application Startup Flow

```mermaid
sequenceDiagram
    actor User
    participant main as main()
    participant root as tk.Tk
    participant dialog as UserDetailsDialog
    participant app as ShoppingApp
    participant csv as items.csv
    participant profile as user_profile.json

    User->>main: Run shopping_app.py
    main->>root: Create root window
    main->>sv_ttk: set_theme("dark")
    main->>app: ShoppingApp(root)

    app->>dialog: get_user_details()
    dialog->>User: Show name/email form
    User->>dialog: Enter name + email
    dialog->>dialog: ok() — store result
    dialog-->>app: Return (name, email)

    app->>csv: load_items_from_csv()
    csv-->>app: items_dict

    app->>profile: load_profile()
    profile-->>app: Saved name/email

    app->>app: Build GUI layout
    app-->>User: Display main window
```

---

## Shopping Cart Data Flow

```mermaid
flowchart LR
    csv[(items.csv)] --> |load_items_from_csv| ShoppingApp
    ShoppingApp --> |select & "Add to Cart"| Basket
    
    subgraph Basket [In-Memory Cart State]
        basket_list[basket: list[str]]
        total_cost[total_cost: float]
        total_weight[total_weight: float]
    end

    Basket --> |update_totals| progress[Progress Bar<br/>Free shipping at €500]
    Basket --> |update_cart_display| cart_listbox[Cart Listbox<br/>item (xCount)]
    Basket --> |calculate_shipping| shipping[Shipping Cost<br/>€1.2/kg + €10 penalty >50kg]

    UserDetailsDialog --> |user_name, user_email| profile_frame[Profile Display]
    profile_frame --> |Save| user_profile_json[(user_profile.json)]
    user_profile_json --> |Load| profile_frame

    Basket --> |checkout| mailing_py
    mailing_py --> |send_order_confirmation| smtp[SMTP gmail]
    smtp --> |email| Customer
    smtp --> |email| Shop
```

---

## GUI Layout

```mermaid
flowchart TD
    subgraph root ["800x600 Main Window (Sun Valley Dark)"]
        direction TB

        profile_frame[Profile Frame<br/>Top-right corner<br/>👤 name / ✉ email + Save Profile]

        subgraph left_panel [Left Column - Items]
            direction TB
            items_label[Available Items]
            items_listbox[Listbox<br/>item: €cost, weight: Nkg]
            search_frame[Search Bar + Button]
            add_btn[Add to Cart<br/>Ctrl+A]
        end

        subgraph right_panel [Right Column - Cart]
            direction TB
            cart_label[Your Cart]
            cart_listbox[Listbox<br/>item (xN)]
            remove_btn[Remove Selected<br/>Delete]
            totals_var[Total Cost / Weight / Shipping]
            progress_bar[Free Shipping Progress Bar]
            checkout_btn[Checkout<br/>Enter]
        end
    end

    left_panel --> |add_to_cart| right_panel
    right_panel --> |edit_cart_item| popup[Double-click: Quantity Dialog]
```

---

## Key Business Logic

### Shipping Calculation (`ShoppingApp.calculate_shipping`)

```mermaid
flowchart TD
    A[Start] --> B{total_cost >= 500<br/>AND<br/>total_weight <= 50kg?}
    B -->|Yes| C[Free Shipping = €0]
    B -->|No| D[Base = total_weight × €1.2]
    D --> E{total_weight > 50kg?}
    E -->|Yes| F[Add €10 weight penalty]
    E -->|No| G[Done]
    F --> G
    C --> H[Return shipping cost]
    G --> H
```

### Checkout Flow (`ShoppingApp.checkout`)

```mermaid
flowchart TD
    A[User clicks Checkout / Enter] --> B{basket empty?}
    B -->|Yes| C[Show warning: Cart is empty]
    B -->|No| D[send_order_confirmation<br/>customer_email, basket, totals, shipping]
    D --> E{Email sent<br/>successfully?}
    E -->|Yes| F[Show success message]
    F --> G[Clear basket]
    G --> H[Reset totals]
    E -->|No| I[Show error message]
```

---

## Data Models

```mermaid
classDiagram
    class Item {
        <<frozen dataclass>>
        +str name
        +float weight
        +float cost
    }

    class ShoppingCart {
        <<dataclass>>
        +List[Item] items
        +add(item: Item) None
        +remove(item: Item, all_of_them: bool) None
        +total_cost() float
        +total_weight() float
        +item_counts() Dict[str, int]
        +is_empty() bool
    }

    class ItemDictEntry {
        +float weight
        +float cost
    }

    Item "*" -- "1" ShoppingCart : contained in
    Item ..> ItemDictEntry : loaded from CSV as
```

---

## Configuration & Environment

| File | Purpose |
|---|---|
| `config.py` | Base paths (`ITEMS_CSV`, `PROFILE_JSON`), SMTP settings via `dotenv` |
| `.env` | `SMTP_EMAIL`, `SMTP_PASSWORD`, `SHOP_EMAIL` |
| `items.csv` | 12 products (banana, cherry, table, computer, etc.) with weight & cost |
| `user_profile.json` | Persisted `{name, email}` — loaded at startup, saved via button |
| `assets/` | PNG icons used in buttons (`cart.png`, `remove_icon.png`) |

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+A` | Add selected item to cart |
| `Delete` | Remove selected cart items |
| `Enter` | Checkout |
| `Double-click` (cart) | Edit item quantity |
