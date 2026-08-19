import os
import zipfile
import tkinter as tk
from tkinter import filedialog

def setup_data():
    print("Starting Automated Data Setup...")
    
    raw_dir = os.path.join(os.getcwd(), 'data', 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    print(f"Ensured data directory exists at:\n{raw_dir}")

    root = tk.Tk()
    root.withdraw() # Hide the main window
    root.attributes('-topmost', True) # Bring the file dialog to the front

    print("\n*** ACTION REQUIRED ***")
    print("Please look for a file selection window that just opened.")
    print("(It might be blinking at the bottom of your screen or behind VS Code!)")
    print("Select the downloaded Olist ZIP file from Kaggle...")
    
    zip_path = filedialog.askopenfilename(
        title="Select the downloaded Olist Kaggle ZIP file",
        filetypes=[("ZIP files", "*.zip")]
    )

    if not zip_path:
        print("❌ No file selected. Setup cancelled. Please run again and select the file.")
        return

    print(f"\nExtracting {zip_path} into {raw_dir}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract everything directly to the raw directory
            zip_ref.extractall(raw_dir)
        
        print("✅ Extraction complete!")
        
        files = os.listdir(raw_dir)
        csv_count = sum(1 for f in files if f.endswith('.csv'))
        print(f"Found {csv_count} CSV files in {raw_dir}.")
        
        if csv_count >= 9:
            print("\n🎉 SUCCESS! The files are perfectly placed. You can now run profiling!")
        else:
            print("\n⚠️ Warning: Extracted files, but didn't find all 9 CSVs. Check the ZIP.")
            
    except Exception as e:
        print(f"❌ Error extracting ZIP: {e}")

if __name__ == "__main__":
    setup_data()
