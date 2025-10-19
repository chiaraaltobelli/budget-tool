def apply_rules(description, categories):
    """
    Apply specific rules to the description to improve categorization accuracy.
    This function can be extended to include more complex rules as needed.
    """
    # Example rule: Normalize common variations in descriptions
    description = description.lower().strip()
    
    # Add more rules as necessary
    return description

def categorize_spending(description, categories):
    """
    Categorize spending based on the provided description and categories.
    This function uses the apply_rules function to preprocess the description.
    """
    normalized_description = apply_rules(description, categories)
    
    for category, keywords in categories.items():
        if any(keyword in normalized_description for keyword in keywords):
            return category
            
    return "Uncategorized"  # Default category if no match is found