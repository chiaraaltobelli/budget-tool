import os
import pandas as pd
from io_utils import read_categories, read_exports
from categorize import categorize_spending

def main():
    categories_file = 'data/categories.csv'
    exports_folder = 'data/exports'
    output_file = 'inputs.xlsx'

    # Read categories
    categories = read_categories(categories_file)

    # Initialize a list to hold all categorized spending
    all_categorized_spending = []

    # Process each export file in the specified folder (.csv, .xls, .xlsx)
    exports_folder_path = str(exports_folder)
    # resolve relative to project root (one level above src)
    if not os.path.isabs(exports_folder_path):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        exports_folder_path = os.path.join(project_root, exports_folder_path)

    for filename in os.listdir(exports_folder_path):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.csv', '.xls', '.xlsx'):
            file_path = os.path.join(exports_folder_path, filename)
            exports = read_exports(file_path)
            categorized_spending = categorize_spending(exports, categories)
            all_categorized_spending.extend(categorized_spending)

    # # Write the compiled output to a single spreadsheet
    # write_output(all_categorized_spending, output_file)

if __name__ == '__main__':
    main()