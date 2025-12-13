import os
import shutil

BASE_DIR = r"C:\Ticket-system\ticket_system"
SETUP_SRC = os.path.join(BASE_DIR, "setup", "templates")
SETUP_DST = os.path.join(BASE_DIR, "setup", "templates", "setup")
TRANS_DST = os.path.join(BASE_DIR, "transactions", "templates", "transactions")

# Define moves (src_filename, dst_folder, dst_filename)
moves = [
    ("area.html", SETUP_DST, "area_form.html"),
    ("customer.html", SETUP_DST, "customer_form.html"),
    ("item_category.html", SETUP_DST, "item_category_form.html"),
    ("item.html", SETUP_DST, "item_form.html"),
    ("machine.html", SETUP_DST, "machine_form.html"),
    ("operator.html", SETUP_DST, "operator_form.html"),
    
    # Transactions (Source is currently setup/templates because previous step moved them there flatly)
    ("sales_order_touch.html", TRANS_DST, "sales_order_form.html"),
    ("job.html", TRANS_DST, "job_order_form.html"),
    ("print.html", TRANS_DST, "printing_transaction_form.html"),
    ("rewinding.html", TRANS_DST, "rewinding_transaction_form.html"),
    # Handling duplicate/rename
    ("sliting.html", TRANS_DST, "slitting_transaction_form.html"), 
    ("laminating.html", TRANS_DST, "lamination_transaction_form.html"),
    ("core.html", TRANS_DST, "core_transaction_form.html"),
]

def main():
    # Create directories
    os.makedirs(SETUP_DST, exist_ok=True)
    os.makedirs(TRANS_DST, exist_ok=True)
    
    print(f"Created/Verified directories:\n{SETUP_DST}\n{TRANS_DST}")
    
    for src_name, dst_dir, dst_name in moves:
        src_path = os.path.join(SETUP_SRC, src_name)
        dst_path = os.path.join(dst_dir, dst_name)
        
        if os.path.exists(src_path):
            try:
                shutil.move(src_path, dst_path)
                print(f"Moved: {src_name} -> {dst_name}")
            except Exception as e:
                print(f"Error moving {src_name}: {e}")
        else:
            print(f"Source not found: {src_path}")

if __name__ == "__main__":
    main()
