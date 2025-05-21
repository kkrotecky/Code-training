import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from PIL import Image, ImageTk
import sv_ttk  # Add this import
from mailing import send_order_confirmation
import json

def load_items_from_csv():
    items_dict = {}
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'items.csv')
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                items_dict[row['item']] = {
                    'weight': float(row['weight']),
                    'cost': float(row['cost'])
                }
        return items_dict
    except FileNotFoundError:
        messagebox.showerror("Error", f"items.csv not found in {current_dir}!")
        return {}

def create_default_icon(color="#2196F3"):
    # Create a simple colored square as default icon
    img = Image.new('RGB', (20, 20), color=color)
    return ImageTk.PhotoImage(img)

def load_icon(filename, size=(20, 20)):
    try:
        path = os.path.join(os.path.dirname(__file__), 'assets', filename)
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading icon: {e}")
        return create_default_icon()

class ToolTip:
    def __init__(self, widget, text, delay=2000):  # delay in milliseconds (2 seconds)
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.schedule_id = None
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_tooltip(self, event=None):
        # Cancel any existing scheduled tooltip
        self.cancel_schedule()
        # Schedule new tooltip
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_schedule(self):
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def show_tooltip(self, event=None):
        # Get widget position
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Create new tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, 
                         background="#ffffe0", 
                         relief="solid", 
                         borderwidth=1,
                         padding=(5, 2))
        label.pack()

    def hide_tooltip(self, event=None):
        # Cancel any scheduled tooltip
        self.cancel_schedule()
        # Destroy existing tooltip
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class UserDetailsDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Details")
        self.dialog.geometry("300x200")  # Made taller for new button
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + parent.winfo_width()/2 + 400,
            parent.winfo_rooty() + parent.winfo_height()/2 + 400))
        
        # Variables
        self.name = tk.StringVar()
        self.email = tk.StringVar()
        self.result = None
        
        # Name entry
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.dialog, textvariable=self.name).grid(row=0, column=1, padx=5, pady=5)
        
        # Email entry
        ttk.Label(self.dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.dialog, textvariable=self.email).grid(row=1, column=1, padx=5, pady=5)
        
        # Load Profile button
        ttk.Button(self.dialog, text="Load Profile", command=self.load_profile).grid(row=2, columnspan=2, pady=10)
        
        # OK/Cancel buttons
        ttk.Button(self.dialog, text="OK", command=self.ok).grid(row=3, column=0, padx=5, pady=20)
        self.dialog.bind('<Return>', lambda event: self.ok())
        ttk.Button(self.dialog, text="Cancel", command=self.cancel).grid(row=3, column=1, padx=5, pady=20)

    def load_profile(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(current_dir, 'user_profile.json')
            
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                    self.name.set(profile['name'])
                    self.email.set(profile['email'])
                    messagebox.showinfo("Success", "Profile loaded successfully!")
            else:
                messagebox.showwarning("Warning", "No saved profile found.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load profile: {str(e)}")

    def ok(self):
        if not self.name.get() or not self.email.get():
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        self.result = (self.name.get(), self.email.get())
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()

class ShoppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping Cart")
        self.root.geometry("800x600")
        
        # Get user details before showing main window
        self.get_user_details()
        if not hasattr(self, 'user_name') or not hasattr(self, 'user_email'):
            self.root.destroy()
            return
            
        # Load items from CSV
        self.items_dict = load_items_from_csv()
        
        self.basket = []
        self.total_cost = 0
        self.total_weight = 0
        
        # Create frames
        self.items_frame = ttk.Frame(root, padding="10")
        self.items_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.cart_frame = ttk.Frame(root, padding="10")
        self.cart_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Available items list
        ttk.Label(self.items_frame, text="Available Items").grid(row=0, column=0, pady=5)
        self.items_listbox = tk.Listbox(self.items_frame, width=40)
        self.items_listbox.grid(row=1, column=0, pady=5)
        
        # Add items to listbox
        for item, details in self.items_dict.items():
            self.items_listbox.insert(tk.END, f"{item}: €{details['cost']}, Weight: {details['weight']}kg")
        
        # Add scrollbar to items listbox
        self.items_scrollbar = ttk.Scrollbar(self.items_frame, orient="vertical", command=self.items_listbox.yview)
        self.items_listbox.configure(yscrollcommand=self.items_scrollbar.set)
        self.items_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Load PNG icons
        self.cart_icon = load_icon('cart.png')
        self.remove_icon = load_icon('remove_icon.png')

        # Add to cart button
        self.add_cart_btn = ttk.Button(self.items_frame, 
            text="Add to Cart", 
            image=self.cart_icon, 
            compound="left", 
            command=self.add_to_cart)
        self.add_cart_btn.grid(row=2, column=0, pady=5)
        ToolTip(self.add_cart_btn, "Add selected item to cart (Ctrl+A)")
        
        # Add below the items list
        self.search_frame = ttk.Frame(self.items_frame)
        self.search_frame.grid(row=3, column=0, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_items)

        ttk.Button(self.search_frame, text="Search", command=self.search_items).grid(row=0, column=1)
        
        # Cart display
        ttk.Label(self.cart_frame, text="Your Cart").grid(row=0, column=0, pady=5)
        self.cart_listbox = tk.Listbox(self.cart_frame, width=30, height=10, 
                                     selectmode=tk.EXTENDED)  # Changed from MULTIPLE to EXTENDED
        self.cart_listbox.grid(row=1, column=0, pady=5)
        
        # Add scrollbar to cart listbox
        self.cart_scrollbar = ttk.Scrollbar(self.cart_frame, orient="vertical", command=self.cart_listbox.yview)
        self.cart_listbox.configure(yscrollcommand=self.cart_scrollbar.set)
        self.cart_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Add this instance variable to track selected item
        self.selected_item = None
        
        # Remove from Cart button
        self.remove_btn = ttk.Button(self.cart_frame, 
            text="Remove Selected", 
            image=self.remove_icon, 
            compound="left", 
            command=self.remove_from_cart)
        self.remove_btn.grid(row=2, column=0, pady=5)
        ToolTip(self.remove_btn, "Remove selected items (Delete)")
        
        # Totals display
        self.totals_var = tk.StringVar()
        ttk.Label(self.cart_frame, textvariable=self.totals_var).grid(row=3, column=0, pady=5)
        
        # Add Progress bar and label
        self.progress_bar = ttk.Progressbar(
            self.cart_frame, 
            orient="horizontal", 
            length=200, 
            mode="determinate"
        )
        self.progress_bar.grid(row=4, column=0, pady=5)
        
        self.progress_label = ttk.Label(
            self.cart_frame, 
            text="Progress to Free Shipping: 0%"
        )
        self.progress_label.grid(row=5, column=0, pady=5)
        
        # Move checkout button one row down
        self.checkout_btn = ttk.Button(self.cart_frame, 
            text="Checkout", 
            command=self.checkout)
        self.checkout_btn.grid(row=6, column=0, pady=5)
        ToolTip(self.checkout_btn, "Complete purchase (Enter)")
        
        self.update_totals()
        
        # Bind double-click event to cart listbox
        self.cart_listbox.bind('<Double-1>', self.edit_cart_item)

        # New keyboard shortcuts
        self.root.bind('<Control-a>', lambda e: self.add_to_cart())
        self.root.bind('<Delete>', lambda e: self.remove_from_cart())
        self.root.bind('<Return>', lambda e: self.checkout())
        
        # Remove the email entry frame since we now have it stored
        # Replace it with a user info display
        # Profile display in the top-right corner
        self.profile_frame = ttk.Frame(self.root)
        self.profile_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.profile_label = ttk.Label(
            self.profile_frame, 
            text=f"👤 {self.user_name}\n✉️ {self.user_email}",
            justify="right"
        )
        self.profile_label.grid(row=0, column=0, sticky="e")

        self.save_profile_btn = ttk.Button(
            self.profile_frame, 
            text="Save Profile", 
            command=self.save_profile
        )
        self.save_profile_btn.grid(row=1, column=0, sticky="e", pady=(2, 0))

        self.load_profile()

    def get_user_details(self):
        dialog = UserDetailsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.user_name, self.user_email = dialog.result

    def add_to_cart(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return
            
        item_name = list(self.items_dict.keys())[selection[0]]
        self.basket.append(item_name)
        self.total_cost += self.items_dict[item_name]['cost']
        self.total_weight += self.items_dict[item_name]['weight']
        
        self.update_cart_display()
        self.update_totals()

    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        # Create a dictionary to count items
        item_counts = {}
        for item in self.basket:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        # Display items with their quantities
        for item, count in item_counts.items():
            display_text = f"{item} (x{count})" if count > 1 else item
            self.cart_listbox.insert(tk.END, display_text)

    def update_totals(self):
        shipping = self.calculate_shipping()
        self.totals_var.set(
            f"Total Cost: €{self.total_cost:.2f}\n"
            f"Total Weight: {self.total_weight:.2f}kg\n"
            f"Shipping: €{shipping:.2f}"
        )

        # Update progress calculation to use 500
        progress = (self.total_cost / 500) * 100 if self.total_cost <= 500 else 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"Progress to Free Shipping: {progress:.0f}%")

    def calculate_shipping(self):
        base_shipping = self.total_weight * 1.2
        weight_penalty = 10 if self.total_weight > 50 else 0
        
        if self.total_cost >= 500 and self.total_weight <= 50:  # Changed from 200 to 500
            return 0
        
        return base_shipping + weight_penalty

    def checkout(self):
        if not self.basket:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
            
        shipping = self.calculate_shipping()
        success, message = send_order_confirmation(
            self.user_email,  # Use stored email
            self.basket,
            self.total_cost,
            self.total_weight,
            shipping
        )
        
        if success:
            messagebox.showinfo("Success", "Order placed successfully!\nCheck your email for confirmation.")
            self.basket.clear()
            self.total_cost = 0
            self.total_weight = 0
            self.update_cart_display()
            self.update_totals()
        else:
            messagebox.showerror("Error", message)

    def track_selection(self, event):
        try:
            selections = self.cart_listbox.curselection()
            if selections:
                self.selected_item = self.cart_listbox.get(selections[0])
            return "break" # Prevents default handling
        except tk.TclError:
            pass

    def remove_from_cart(self):
        selections = self.cart_listbox.curselection()
        if not selections:
            messagebox.showwarning("Warning", "Please select item(s) to remove")
            return
            
        for index in selections:
            item_text = self.cart_listbox.get(index)
            # Extract item name without quantity
            item_name = item_text.split(" (x")[0]
            # Remove all instances of this item
            while item_name in self.basket:
                self.basket.remove(item_name)
                self.total_cost -= self.items_dict[item_name]['cost']
                self.total_weight -= self.items_dict[item_name]['weight']
    
        self.update_cart_display()
        self.update_totals()

    def search_items(self, event=None):
        search_term = self.search_var.get().lower()
        self.items_listbox.delete(0, tk.END)
        
        for item, details in self.items_dict.items():
            if search_term in item.lower():
                self.items_listbox.insert(tk.END, f"{item}: €{details['cost']}, Weight: {details['weight']}kg")

    # Add this method to the ShoppingApp class
    def edit_cart_item(self, event=None):
        selection = self.cart_listbox.curselection()
        if not selection:
            return
            
        item = self.cart_listbox.get(selection[0])
        quantity = messagebox.askinteger(
            "Edit Quantity", 
            f"Enter quantity for {item}:",
            initialvalue=1,
            minvalue=0,
            maxvalue=99
        )
        
        if quantity is None:  # User cancelled
            return
            
        if quantity == 0:  # Remove item
            self.basket.remove(item)
            self.total_cost -= self.items_dict[item]['cost']
            self.total_weight -= self.items_dict[item]['weight']
        else:  # Update quantity
            current_count = self.basket.count(item)
            difference = quantity - current_count
            
            # Remove all current instances
            while item in self.basket:
                self.basket.remove(item)
            
            # Add new quantity
            for _ in range(quantity):
                self.basket.append(item)
            
            # Update totals
            self.total_cost += self.items_dict[item]['cost'] * difference
            self.total_weight += self.items_dict[item]['weight'] * difference
        
        self.update_cart_display()
        self.update_totals()

    def save_profile(self):
        """Save user profile to a JSON file"""
        profile = {
            'name': self.user_name,
            'email': self.user_email
        }
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(current_dir, 'user_profile.json')
            
            with open(profile_path, 'w') as f:
                json.dump(profile, f)
            messagebox.showinfo("Success", "Profile saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save profile: {str(e)}")

    def load_profile(self):
        """Load user profile from JSON file"""
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(current_dir, 'user_profile.json')
            
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                    self.user_name = profile['name']
                    self.user_email = profile['email']
                    # Update profile display
                    self.profile_label.config(
                        text=f"👤 {self.user_name}\n✉️ {self.user_email}"
                    )
        except FileNotFoundError:
            # No saved profile, that's ok
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not load profile: {str(e)}")

def main():
    root = tk.Tk()
    # Apply Sun Valley theme before creating the app
    sv_ttk.set_theme("dark")  # or "light or dark"
    app = ShoppingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
# This code is a simple shopping cart program that allows users to select items from a predefined list, calculates the total cost and weight of the items in the cart, and determines the shipping cost based on the total cost and weight. The program also provides a summary of the selected items, total cost, weight, and shipping cost.
# The program uses a dictionary to store item details, including their cost and weight. It allows users to add items to their basket until they indicate they are done. The shipping cost is calculated based on the total cost and weight of the items in the basket, with free shipping for orders over €100.