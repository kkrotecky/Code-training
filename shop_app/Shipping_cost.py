import math
import tkinter as tk
from tkinter import ttk, messagebox
from items import items_dict

class ShoppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping Cart")
        self.root.geometry("600x400")
        
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
        for item, details in items_dict.items():
            self.items_listbox.insert(tk.END, f"{item}: €{details['cost']}, Weight: {details['weight']}kg")
        
        # Add to cart button
        ttk.Button(self.items_frame, text="Add to Cart", command=self.add_to_cart).grid(row=2, column=0, pady=5)
        
        # Cart display
        ttk.Label(self.cart_frame, text="Your Cart").grid(row=0, column=0, pady=5)
        self.cart_listbox = tk.Listbox(self.cart_frame, width=30, height=10, 
                                     selectmode=tk.EXTENDED)  # Changed from MULTIPLE to EXTENDED
        self.cart_listbox.grid(row=1, column=0, pady=5)
        
        # Add this instance variable to track selected item
        self.selected_item = None
        
        # Remove from Cart button
        ttk.Button(self.cart_frame, text="Remove Selected", command=self.remove_from_cart).grid(row=2, column=0, pady=5)
        
        # Totals display
        self.totals_var = tk.StringVar()
        ttk.Label(self.cart_frame, textvariable=self.totals_var).grid(row=3, column=0, pady=5)
        self.update_totals()
        
        # Checkout button
        ttk.Button(self.cart_frame, text="Checkout", command=self.checkout).grid(row=4, column=0, pady=5)

    def add_to_cart(self):
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return
            
        item_name = list(items_dict.keys())[selection[0]]
        self.basket.append(item_name)
        self.total_cost += items_dict[item_name]['cost']
        self.total_weight += items_dict[item_name]['weight']
        
        self.update_cart_display()
        self.update_totals()

    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        for item in self.basket:
            self.cart_listbox.insert(tk.END, item)

    def update_totals(self):
        shipping = self.calculate_shipping()
        self.totals_var.set(
            f"Total Cost: €{self.total_cost:.2f}\n"
            f"Total Weight: {self.total_weight:.2f}kg\n"
            f"Shipping: €{shipping:.2f}"
        )

    def calculate_shipping(self):
        base_shipping = self.total_weight * 1.2
        weight_penalty = 10 if self.total_weight > 50 else 0
        
        if self.total_cost >= 200 and self.total_weight <= 50:
            return 0
        
        return base_shipping + weight_penalty

    def checkout(self):
        shipping = self.calculate_shipping()
        message = (
            f"=== Final Summary ===\n"
            f"Items: {', '.join(self.basket)}\n"
            f"Total cost: €{self.total_cost:.2f}\n"
            f"Total weight: {self.total_weight:.2f}kg\n"
            f"Shipping cost: €{shipping:.2f}\n"
            f"Final total: €{self.total_cost + shipping:.2f}"
        )
        
        if shipping == 0:
            message += "\nCongratulations! You got free shipping!"
        elif self.total_weight > 50:
            message += "\nNote: A €10 penalty was applied due to weight exceeding 50kg"
            
        messagebox.showinfo("Checkout", message)

    def track_selection(self, event):
        try:
            # Get index of the clicked line
            index = self.cart_text.index("@%s,%s" % (event.x, event.y))
            # Get the line content
            line = self.cart_text.get(f"{index} linestart", f"{index} lineend").strip()
            if line:
                self.selected_item = line
            return "break"  # Prevents default handling
        except tk.TclError:
            pass

    def remove_from_cart(self):
        selections = self.cart_listbox.curselection()
        if not selections:
            messagebox.showwarning("Warning", "Please select item(s) to remove")
            return
            
        # Convert to list to avoid issues with changing indices
        items_to_remove = [self.cart_listbox.get(i) for i in selections]
        
        # Remove selected items and update totals
        for item in items_to_remove:
            self.basket.remove(item)
            self.total_cost -= items_dict[item]['cost']
            self.total_weight -= items_dict[item]['weight']
        
        # Update displays
        self.update_cart_display()
        self.update_totals()

def main():
    root = tk.Tk()
    app = ShoppingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
# This code is a simple shopping cart program that allows users to select items from a predefined list, calculates the total cost and weight of the items in the cart, and determines the shipping cost based on the total cost and weight. The program also provides a summary of the selected items, total cost, weight, and shipping cost.
# The program uses a dictionary to store item details, including their cost and weight. It allows users to add items to their basket until they indicate they are done. The shipping cost is calculated based on the total cost and weight of the items in the basket, with free shipping for orders over €100.