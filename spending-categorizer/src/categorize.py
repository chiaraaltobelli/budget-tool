def load_categories(file_path):
    import pandas as pd
    categories = pd.read_csv(file_path)
    return categories.set_index('description').to_dict()['category']

def categorize_spending(export_data, categories):
    categorized_data = []
    for index, row in export_data.iterrows():
        description = row['description'].lower()
        category = next((cat for desc, cat in categories.items() if desc.lower() in description), 'Uncategorized')
        categorized_data.append({'date': row['date'], 'description': row['description'], 'amount': row['amount'], 'category': category})
    return categorized_data

def compile_output(categorized_data):
    import pandas as pd
    output_df = pd.DataFrame(categorized_data)
    return output_df

def process_exports(export_files, categories):
    import pandas as pd
    all_categorized_data = []
    for file in export_files:
        export_data = pd.read_csv(file)
        categorized_data = categorize_spending(export_data, categories)
        all_categorized_data.extend(categorized_data)
    return compile_output(all_categorized_data)