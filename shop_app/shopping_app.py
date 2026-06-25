"""Shopping Cart GUI — main application entry point.

Phase 4: UX Polish — order history, search improvements, quantity spinner,
confirmation summary, and error recovery.
"""

import json
import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from pathlib import Path

import sv_ttk
from PIL import Image, ImageTk

from config import PROFILE_JSON
from data import load_items
from mailing import send_order_confirmation
from order import Order, OrderRepository


# ── Constants ──────────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FREE_SHIPPING_THRESHOLD = 500.0
FREE_SHIPPING_MAX_WEIGHT = 50.0
ORDERS_DIR = Path(__file__).parent / "orders"
INVOICES_DIR = Path(__file__).parent / "invoices"


# ── Helpers ────────────────────────────────────────────────────────────

def _validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


def _validate_name(name: str) -> bool:
    return bool(name.strip())


def fmt_price(amount: float) -> str:
    return f"€{amount:,.2f}"


def create_default_icon(color="#2196F3"):
    img = Image.new("RGB", (20, 20), color=color)
    return ImageTk.PhotoImage(img)


def load_icon(filename, size=(20, 20)):
    try:
        path = os.path.join(os.path.dirname(__file__), "assets", filename)
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading icon: {e}")
        return create_default_icon()


# ── ToolTip ────────────────────────────────────────────────────────────

class ToolTip:
    """Hover tooltip with configurable delay."""

    def __init__(self, widget, text, delay=2000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.schedule_id = None
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_tooltip(self, event=None):
        self.cancel_schedule()
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_schedule(self):
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def show_tooltip(self, event=None):
        try:
            x, y, _, _ = self.widget.bbox("insert")
        except tk.TclError:
            x, y = 0, 0
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padding=(5, 2),
        )
        label.pack()

    def hide_tooltip(self, event=None):
        self.cancel_schedule()
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


# ── User Details Dialog ────────────────────────────────────────────────

class UserDetailsDialog:
    """Modal dialog for entering user name and email."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Details")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center over parent (or screen if parent not mapped yet)
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        dx, dy = 300, 200

        # If parent is not yet mapped (width/height = 1), center on screen
        if pw <= 1 or ph <= 1:
            screen_w = self.dialog.winfo_screenwidth()
            screen_h = self.dialog.winfo_screenheight()
            x = max(0, (screen_w - dx) // 2)
            y = max(0, (screen_h - dy) // 2)
        else:
            x = px + (pw - dx) // 2
            y = py + (ph - dy) // 2

        self.dialog.geometry(f"+{x}+{y}")

        self.name = tk.StringVar()
        self.email = tk.StringVar()
        self.result = None

        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.dialog, textvariable=self.name).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(self.dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.dialog, textvariable=self.email).grid(
            row=1, column=1, padx=5, pady=5
        )

        ttk.Button(self.dialog, text="Load Profile", command=self.load_profile).grid(
            row=2, columnspan=2, pady=10
        )
        ttk.Button(self.dialog, text="OK", command=self.ok).grid(
            row=3, column=0, padx=5, pady=20
        )
        self.dialog.bind("<Return>", lambda e: self.ok())
        ttk.Button(self.dialog, text="Cancel", command=self.cancel).grid(
            row=3, column=1, padx=5, pady=20
        )

    def load_profile(self):
        try:
            path = Path(str(PROFILE_JSON))
            if path.exists():
                with open(path, "r") as f:
                    profile = json.load(f)
                if not isinstance(profile, dict):
                    raise ValueError("Profile is not a valid JSON object")
                self.name.set(profile.get("name", ""))
                self.email.set(profile.get("email", ""))
                messagebox.showinfo("Success", "Profile loaded successfully!")
            else:
                messagebox.showwarning("Warning", "No saved profile found.")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror(
                "Error", f"Saved profile is corrupted ({e}).\nPlease re-enter your details."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not load profile: {e}")

    def ok(self):
        name = self.name.get().strip()
        email = self.email.get().strip()

        if not _validate_name(name):
            messagebox.showwarning("Warning", "Please enter your name.")
            return
        if not _validate_email(email):
            messagebox.showwarning("Warning", "Please enter a valid email address.")
            return

        self.result = (name, email)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()


# ── Checkout Confirmation Dialog ───────────────────────────────────────

class CheckoutConfirmation:
    """Shows a full order summary and asks the user to confirm."""

    def __init__(self, parent, basket, items_dict, total_cost, total_weight, shipping_cost, user_name, user_email):
        self.result = False
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Confirm Order")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center over parent (or screen if parent not mapped yet)
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        dx, dy = 450, 400

        if pw <= 1 or ph <= 1:
            screen_w = self.dialog.winfo_screenwidth()
            screen_h = self.dialog.winfo_screenheight()
            x = max(0, (screen_w - dx) // 2)
            y = max(0, (screen_h - dy) // 2)
        else:
            x = px + (pw - dx) // 2
            y = py + (ph - dy) // 2

        self.dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.dialog, padding="15")
        frame.pack(fill="both", expand=True)

        # Customer info
        ttk.Label(frame, text=f"Customer: {user_name}", font=("", 10, "bold")).pack(
            anchor="w"
        )
        ttk.Label(frame, text=f"Email: {user_email}").pack(anchor="w")
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        # Items
        ttk.Label(frame, text="Items:", font=("", 10, "bold")).pack(anchor="w")
        item_counts = {}
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1

        items_frame = ttk.Frame(frame)
        items_frame.pack(fill="both", expand=True, pady=4)

        # Scrollable text widget for items
        text = tk.Text(items_frame, height=8, width=50, wrap="none")
        scroll_y = ttk.Scrollbar(items_frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll_y.set)

        for name, qty in item_counts.items():
            item = items_dict[name]
            line_total = qty * item.cost
            text.insert(
                "end",
                f"  {name} x{qty}  @ {fmt_price(item.cost)}  =  {fmt_price(line_total)}\n",
            )

        text.configure(state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        # Totals
        grand_total = total_cost + shipping_cost
        ttk.Label(
            frame,
            text=f"Subtotal:       {fmt_price(total_cost)}",
            font=("", 10),
        ).pack(anchor="e")
        ttk.Label(
            frame,
            text=f"Shipping:       {fmt_price(shipping_cost)}",
            font=("", 10),
        ).pack(anchor="e")
        ttk.Label(
            frame,
            text=f"Weight:         {total_weight:.2f} kg",
            font=("", 10),
        ).pack(anchor="e")
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=4)
        ttk.Label(
            frame,
            text=f"Grand Total:  {fmt_price(grand_total)}",
            font=("", 12, "bold"),
        ).pack(anchor="e")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(12, 0))
        ttk.Button(
            btn_frame, text="Cancel", command=self.dialog.destroy
        ).pack(side="right", padx=4)
        ttk.Button(
            btn_frame, text="Confirm Order", command=self.confirm
        ).pack(side="right", padx=4)
        self.dialog.bind("<Return>", lambda e: self.confirm())

    def confirm(self):
        self.result = True
        self.dialog.destroy()


# ── Main Application ───────────────────────────────────────────────────

class ShoppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping Cart")

        # Size and center on screen
        win_w, win_h = 900, 700
        self.root.geometry(f"{win_w}x{win_h}")
        self.center_window(self.root, win_w, win_h)

        # Order persistence
        self.order_repo = OrderRepository()

        # Get user details before showing main window
        self.get_user_details()
        if not hasattr(self, "user_name") or not hasattr(self, "user_email"):
            self.root.destroy()
            return

        # Load items via data module
        try:
            self.items_dict = load_items()
        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not load items.csv: {e}\nPlease ensure the file exists and is valid."
            )
            self.root.destroy()
            return

        if not self.items_dict:
            messagebox.showerror("Error", "No items loaded. Please check items.csv.")
            self.root.destroy()
            return

        self.basket: list[str] = []
        self.total_cost = 0.0
        self.total_weight = 0.0
        self._order_history_ids: list[str] = []  # maps listbox index → full order_id

        # ── Layout ──────────────────────────────────────────────
        self.items_frame = ttk.Frame(root, padding="10")
        self.items_frame.grid(row=0, column=0, sticky="nsew")

        self.cart_frame = ttk.Frame(root, padding="10")
        self.cart_frame.grid(row=0, column=1, sticky="nsew")

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(0, weight=1)

        # ══════════════════════════════════════════════════════════
        #  Column 0 — Available Items
        # ══════════════════════════════════════════════════════════
        ttk.Label(self.items_frame, text="Available Items", font=("", 11, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 5)
        )

        self.items_listbox = tk.Listbox(self.items_frame, width=40)
        self.items_listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")
        self.items_frame.grid_rowconfigure(1, weight=1)
        self.items_frame.grid_columnconfigure(0, weight=1)

        self._refresh_items_list()

        # Add to cart button
        self.add_cart_btn = ttk.Button(
            self.items_frame,
            text="Add to Cart",
            command=self.add_to_cart,
        )
        self.add_cart_btn.grid(row=2, column=0, columnspan=2, pady=5)
        ToolTip(self.add_cart_btn, "Add selected item to cart (Ctrl+A)")

        # Search row
        self.search_frame = ttk.Frame(self.items_frame)
        self.search_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.search_items())
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ttk.Button(self.search_frame, text="Search", command=self.search_items).grid(
            row=0, column=1, padx=2
        )
        self.clear_btn = ttk.Button(
            self.search_frame, text="Clear", command=self.clear_search
        )
        self.clear_btn.grid(row=0, column=2, padx=2)

        # ══════════════════════════════════════════════════════════
        #  Column 1 — Cart + Order History
        # ══════════════════════════════════════════════════════════
        # ── Cart section ──
        ttk.Label(self.cart_frame, text="Your Cart", font=("", 11, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 5)
        )

        self.cart_listbox = tk.Listbox(
            self.cart_frame, width=30, height=6, selectmode=tk.EXTENDED
        )
        self.cart_listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")

        scroll_cart = ttk.Scrollbar(
            self.cart_frame, orient="vertical", command=self.cart_listbox.yview
        )
        self.cart_listbox.configure(yscrollcommand=scroll_cart.set)
        scroll_cart.grid(row=1, column=2, sticky="ns")

        # Cart buttons row
        cart_btn_frame = ttk.Frame(self.cart_frame)
        cart_btn_frame.grid(row=2, column=0, columnspan=3, pady=4)

        ttk.Button(
            cart_btn_frame, text="Remove Selected", command=self.remove_from_cart
        ).pack(side="left", padx=2)
        ttk.Button(
            cart_btn_frame, text="Edit Qty", command=self.edit_cart_item
        ).pack(side="left", padx=2)
        ToolTip(cart_btn_frame.winfo_children()[0], "Remove selected items (Delete)")
        ToolTip(cart_btn_frame.winfo_children()[1], "Double-click item or press button")

        # Totals display
        self.totals_var = tk.StringVar()
        ttk.Label(self.cart_frame, textvariable=self.totals_var, font=("", 10)).grid(
            row=3, column=0, columnspan=3, pady=4
        )

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.cart_frame, orient="horizontal", length=250, mode="determinate"
        )
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=2)

        self.progress_label = ttk.Label(
            self.cart_frame, text="Progress to Free Shipping: 0%"
        )
        self.progress_label.grid(row=5, column=0, columnspan=3, pady=2)

        # Checkout button
        self.checkout_btn = ttk.Button(
            self.cart_frame, text="Checkout", command=self.checkout
        )
        self.checkout_btn.grid(row=6, column=0, columnspan=3, pady=6)
        ToolTip(self.checkout_btn, "Complete purchase (Enter)")

        ttk.Separator(self.cart_frame, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=8
        )

        # ── Order History section ──
        hist_header = ttk.Frame(self.cart_frame)
        hist_header.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        ttk.Label(hist_header, text="Order History", font=("", 11, "bold")).pack(
            side="left"
        )
        ttk.Button(hist_header, text="R", width=3, command=self._refresh_order_history).pack(
            side="right"
        )

        self.history_listbox = tk.Listbox(
            self.cart_frame, width=30, height=6
        )
        self.history_listbox.grid(row=9, column=0, columnspan=3, pady=2, sticky="nsew")
        self.cart_frame.grid_rowconfigure(9, weight=1)

        scroll_hist = ttk.Scrollbar(
            self.cart_frame, orient="vertical", command=self.history_listbox.yview
        )
        self.history_listbox.configure(yscrollcommand=scroll_hist.set)
        scroll_hist.grid(row=9, column=3, sticky="ns")

        # Order history buttons
        hist_btn_frame = ttk.Frame(self.cart_frame)
        hist_btn_frame.grid(row=10, column=0, columnspan=3, pady=4)

        ttk.Button(
            hist_btn_frame, text="Open Invoice PDF", command=self._open_order_invoice
        ).pack(side="left", padx=2)
        ttk.Button(
            hist_btn_frame, text="View Order JSON", command=self._view_order_json
        ).pack(side="left", padx=2)

        self.history_listbox.bind("<Double-1>", lambda e: self._open_order_invoice())

        self.update_totals()

        # ── Events & shortcuts ──────────────────────────────────
        self.cart_listbox.bind("<Double-1>", self.edit_cart_item)
        self.root.bind("<Control-a>", lambda e: self.add_to_cart())
        self.root.bind("<Delete>", lambda e: self.remove_from_cart())
        self.root.bind("<Return>", lambda e: self.checkout())

        # ── Profile display ─────────────────────────────────────
        self.profile_frame = ttk.Frame(self.root)
        self.profile_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.profile_label = ttk.Label(
            self.profile_frame,
            text=f"Name: {self.user_name}\nEmail: {self.user_email}",
            justify="right",
        )
        self.profile_label.grid(row=0, column=0, sticky="e")

        self.save_profile_btn = ttk.Button(
            self.profile_frame, text="Save Profile", command=self.save_profile
        )
        self.save_profile_btn.grid(row=1, column=0, sticky="e", pady=(2, 0))

        self.load_profile()
        self._refresh_order_history()

    # ── Window positioning ───────────────────────────────────────

    @staticmethod
    def center_window(win: tk.Tk | tk.Toplevel, width: int, height: int) -> None:
        """Center a tkinter window on the screen."""
        win.update_idletasks()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        win.geometry(f"+{x}+{y}")

    # ── User details ────────────────────────────────────────────

    def get_user_details(self):
        dialog = UserDetailsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.user_name, self.user_email = dialog.result

    # ── Items ───────────────────────────────────────────────────

    def _refresh_items_list(self, filter_text: str = ""):
        """Populate the items listbox, optionally filtered."""
        self.items_listbox.delete(0, tk.END)
        for item, details in self.items_dict.items():
            if filter_text and filter_text not in item.lower():
                continue
            self.items_listbox.insert(
                tk.END, f"{item}: {fmt_price(details.cost)}, {details.weight}kg"
            )

    # ── Cart operations ─────────────────────────────────────────

    def add_to_cart(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return

        item_name = list(self.items_dict.keys())[selection[0]]

        # Quantity spinner
        qty = simpledialog.askinteger(
            "Quantity",
            f"How many {item_name}(s) to add?",
            initialvalue=1,
            minvalue=1,
            maxvalue=99,
        )
        if qty is None or qty < 1:
            return  # cancelled or invalid

        for _ in range(qty):
            self.basket.append(item_name)
        self.total_cost += self.items_dict[item_name].cost * qty
        self.total_weight += self.items_dict[item_name].weight * qty

        self.update_cart_display()
        self.update_totals()

    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        item_counts = {}
        for item in self.basket:
            item_counts[item] = item_counts.get(item, 0) + 1
        for item, count in item_counts.items():
            display = f"{item} (x{count})" if count > 1 else item
            self.cart_listbox.insert(tk.END, display)

    def remove_from_cart(self):
        selections = self.cart_listbox.curselection()
        if not selections:
            messagebox.showwarning("Warning", "Please select item(s) to remove")
            return

        for index in selections:
            item_text = self.cart_listbox.get(index)
            item_name = item_text.split(" (x")[0]
            while item_name in self.basket:
                self.basket.remove(item_name)
                self.total_cost -= self.items_dict[item_name].cost
                self.total_weight -= self.items_dict[item_name].weight

        self.update_cart_display()
        self.update_totals()

    # ── Totals & shipping ───────────────────────────────────────

    def update_totals(self):
        shipping = self.calculate_shipping()
        self.totals_var.set(
            f"Total Cost: {fmt_price(self.total_cost)}\n"
            f"Total Weight: {self.total_weight:.2f}kg  |  "
            f"Shipping: {fmt_price(shipping)}"
        )

        progress = (
            (self.total_cost / FREE_SHIPPING_THRESHOLD) * 100
            if self.total_cost <= FREE_SHIPPING_THRESHOLD
            else 100
        )
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"Progress to Free Shipping: {progress:.0f}%")

    def calculate_shipping(self):
        base_shipping = self.total_weight * 1.2
        weight_penalty = 10 if self.total_weight > FREE_SHIPPING_MAX_WEIGHT else 0

        if (
            self.total_cost >= FREE_SHIPPING_THRESHOLD
            and self.total_weight <= FREE_SHIPPING_MAX_WEIGHT
        ):
            return 0

        return base_shipping + weight_penalty

    # ── Checkout ────────────────────────────────────────────────

    def checkout(self):
        if not self.basket:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        shipping = self.calculate_shipping()

        # Confirmation summary before finalizing
        confirm = CheckoutConfirmation(
            self.root,
            self.basket,
            self.items_dict,
            self.total_cost,
            self.total_weight,
            shipping,
            self.user_name,
            self.user_email,
        )
        self.root.wait_window(confirm.dialog)
        if not confirm.result:
            return  # user cancelled

        order = Order.from_basket(
            customer_name=self.user_name,
            customer_email=self.user_email,
            basket=self.basket,
            items_dict=self.items_dict,
            total_cost=self.total_cost,
            total_weight=self.total_weight,
            shipping_cost=shipping,
        )

        order_path = self.order_repo.save(order)

        # Email is optional — don't block on failure
        success, _ = send_order_confirmation(
            self.user_email,
            self.basket,
            self.total_cost,
            self.total_weight,
            shipping,
        )

        lines = ["Order placed successfully!"]
        if success:
            lines.append("Confirmation email sent.")
        lines.append(f"")
        lines.append(f"Order saved: {order_path.name}")
        messagebox.showinfo("Success", "\n".join(lines))

        self.basket.clear()
        self.total_cost = 0.0
        self.total_weight = 0.0
        self.update_cart_display()
        self.update_totals()
        self._refresh_order_history()

    # ── Edit quantity ───────────────────────────────────────────

    def edit_cart_item(self, event=None):
        selection = self.cart_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item in your cart")
            return

        item_text = self.cart_listbox.get(selection[0])
        item_name = item_text.split(" (x")[0]

        quantity = simpledialog.askinteger(
            "Edit Quantity",
            f"Enter quantity for {item_name}:",
            initialvalue=self.basket.count(item_name),
            minvalue=0,
            maxvalue=99,
        )

        if quantity is None:
            return

        # Remove all, then re-add desired quantity
        while item_name in self.basket:
            self.basket.remove(item_name)
            self.total_cost -= self.items_dict[item_name].cost
            self.total_weight -= self.items_dict[item_name].weight

        for _ in range(quantity):
            self.basket.append(item_name)
            self.total_cost += self.items_dict[item_name].cost
            self.total_weight += self.items_dict[item_name].weight

        self.update_cart_display()
        self.update_totals()

    # ── Search ──────────────────────────────────────────────────

    def search_items(self, event=None):
        self._refresh_items_list(filter_text=self.search_var.get().lower())

    def clear_search(self):
        """Clear the search field and show all items."""
        self.search_var.set("")
        self._refresh_items_list()
        self.search_entry.focus_set()

    # ── Order History ───────────────────────────────────────────

    def _refresh_order_history(self):
        """Reload the order history listbox from disk."""
        self.history_listbox.delete(0, tk.END)
        self._order_history_ids.clear()
        try:
            orders = self.order_repo.list_all()
        except Exception:
            orders = []

        if not orders:
            self.history_listbox.insert(tk.END, "(no orders yet)")
            return

        for order in reversed(orders):  # newest first
            self._order_history_ids.append(order.order_id)
            try:
                dt = datetime.fromisoformat(order.created_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                date_str = order.created_at

            invoice_path = INVOICES_DIR / f"invoice_{order.order_id}.pdf"
            has_invoice = " [PDF]" if invoice_path.exists() else ""

            self.history_listbox.insert(
                tk.END,
                f"#{order.order_id[:8]}  {date_str}  {fmt_price(order.totals.grand_total)}{has_invoice}",
            )

    def _selected_order_id(self) -> str | None:
        """Extract the full order ID from the currently selected history item."""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order from the history")
            return None
        idx = selection[0]
        if idx >= len(self._order_history_ids):
            return None
        return self._order_history_ids[idx]

    def _open_order_invoice(self):
        """Open the PDF invoice for the selected order (Windows)."""
        order_id = self._selected_order_id()
        if not order_id:
            return

        invoice_path = INVOICES_DIR / f"invoice_{order_id}.pdf"
        if not invoice_path.exists():
            answer = messagebox.askyesno(
                "No Invoice",
                f"No PDF invoice found for order #{order_id}.\n\nGenerate one now?",
            )
            if answer:
                # Generate invoice on demand using the invoice generator
                try:
                    sys.path.insert(0, str(Path(__file__).parent))
                    from invoice_generator.invoice_generator import generate_invoice

                    order = self.order_repo.load(order_id)
                    if order is None:
                        messagebox.showerror("Error", f"Order #{order_id} not found on disk.")
                        return
                    INVOICES_DIR.mkdir(parents=True, exist_ok=True)
                    generate_invoice(order, invoice_path)
                    messagebox.showinfo("Success", f"Invoice saved: {invoice_path.name}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not generate invoice: {e}")
                    return
            else:
                return

        try:
            os.startfile(invoice_path)  # Windows
        except AttributeError:
            messagebox.showinfo("Invoice", f"Invoice located at:\n{invoice_path}")

    def _view_order_json(self):
        """Show the raw order JSON in a read-only dialog."""
        order_id = self._selected_order_id()
        if not order_id:
            return

        order = self.order_repo.load(order_id)
        if order is None:
            messagebox.showerror("Error", f"Order #{order_id} not found.")
            return

        # Show in a read-only text dialog
        viewer = tk.Toplevel(self.root)
        viewer.title(f"Order #{order_id}")
        viewer.geometry("500x400")
        viewer.transient(self.root)

        text = tk.Text(viewer, wrap="none", padx=10, pady=10)
        text.pack(fill="both", expand=True)

        import json as _json
        text.insert("end", _json.dumps(order.to_dict(), indent=2, ensure_ascii=False))
        text.configure(state="disabled")

        ttk.Button(viewer, text="Close", command=viewer.destroy).pack(pady=5)

    # ── Profile persistence ─────────────────────────────────────

    def save_profile(self):
        try:
            profile = {"name": self.user_name, "email": self.user_email}
            with open(str(PROFILE_JSON), "w") as f:
                json.dump(profile, f)
            messagebox.showinfo("Success", "Profile saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save profile: {e}")

    def load_profile(self):
        try:
            path = Path(str(PROFILE_JSON))
            if path.exists():
                with open(path, "r") as f:
                    profile = json.load(f)
                if not isinstance(profile, dict):
                    raise ValueError("Profile is not a valid object")
                self.user_name = profile.get("name", self.user_name)
                self.user_email = profile.get("email", self.user_email)
                self.profile_label.config(
                    text=f"Name: {self.user_name}\nEmail: {self.user_email}"
                )
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showwarning(
                "Profile Error",
                f"Saved profile is corrupted ({e}).\nStarting with empty profile.",
            )
            # Reset corrupted profile
            self.save_profile()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load profile: {e}")


# ── Entry point ────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    sv_ttk.set_theme("dark")
    ShoppingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
