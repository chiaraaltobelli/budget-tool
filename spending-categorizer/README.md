# Spending Categorizer

The Spending Categorizer is a Python application designed to help users track their spending by categorizing transactions from exported bank statements. This project reads transaction data from CSV or TSV files, matches them against predefined categories, and compiles the results into a single spreadsheet for easy budget tracking.

## Project Structure

```
spending-categorizer
├── src
│   ├── main.py          # Entry point of the application
│   ├── categorize.py    # Contains categorization logic
│   ├── io_utils.py      # Manages input and output operations
│   ├── rules.py         # Defines categorization rules
│   └── __init__.py      # Marks the directory as a Python package
├── data
│   ├── categories.csv    # List of categories for spending
│   └── exports           # Directory for exported bank files
├── tests
│   └── test_categorize.py # Unit tests for categorization functions
├── requirements.txt      # Project dependencies
├── .gitignore            # Files to ignore in version control
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the Repository**: 
   ```
   git clone <repository-url>
   cd spending-categorizer
   ```

2. **Install Dependencies**: 
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Prepare Data**: 
   - Place your exported bank statement files (CSV/TSV) in the `data/exports` directory.
   - Ensure the `data/categories.csv` file is populated with the categories you want to use for categorization.

## Usage

To run the application, execute the following command in your terminal:
```
python src/main.py
```

This will process all the exported files in the `data/exports` directory, categorize the transactions based on the `data/categories.csv`, and compile the results into a single spreadsheet named "inputs".

## Testing

To run the unit tests, use:
```
pytest tests/test_categorize.py
```

This will ensure that the categorization functions work correctly with various inputs.