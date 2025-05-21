import csv

items_dict = {
      "banana" : {
            "weight" : 1,
            "cost" : 2
        },
        "cherry" : {
            "weight" : 0.5,
            "cost": 1
        },
        "table": {
            "weight" : 15,
            "cost" : 250
        },
        "cookies": {
            "weight" : 0.150,
            "cost" : 2
        },
        "computer": {
            "weight" : 13,
            "cost" : 3500
        },
        "television": {
            "weight" : 10,
            "cost" : 1000
        },
        "fragrance": {
            "weight" : 0.200,
            "cost" : 600
        },
        "phone": {
            "weight" : 0.100,
            "cost" : 1200
        },
        "wine": {
            "weight" : 1,
            "cost" : 20
        },
        "headphones": {
            "weight" : 0.200,
            "cost" : 200
        },
        "keyboard": {
            "weight" : 0.200,
            "cost" : 350
        },
        "lamp": {
            "weight" : 0.500,
            "cost" : 50
        },
    }
    # Add more items as needed
    # Example usage of the items_dict
    # print(items_dict["banana"]["cost"])  # Output: 2

def export_to_csv():
    # Define the CSV file path
    csv_file_path = 'D://CODE/Test/shop_app/items.csv'
    
    # Open the file in write mode
    with open(csv_file_path, 'w', newline='') as csvfile:
        # Define the CSV writer and headers
        fieldnames = ['item', 'weight', 'cost']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each item's data
        for item_name, details in items_dict.items():
            writer.writerow({
                'item': item_name,
                'weight': details['weight'],
                'cost': details['cost']
            })

# Export the dictionary when this file is run directly
if __name__ == "__main__":
    export_to_csv()
    print("Items exported to items.csv successfully!")