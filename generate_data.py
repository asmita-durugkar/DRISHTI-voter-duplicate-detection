"""
Synthetic Voter Data Generator with Intentional Duplicates
This script generates realistic voter data with various types of duplicates for testing
"""

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import string

fake = Faker('en_IN')  # Indian locale for realistic Indian names
Faker.seed(42)
random.seed(42)


def generate_voter_id():
    """Generate a random voter ID"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=7))
    return f"{letters}{numbers}"


def create_typo(text, typo_type='char'):
    """Create intentional typos in names"""
    if not text or len(text) < 3:
        return text

    text_list = list(text)
    pos = random.randint(1, len(text_list) - 2)

    if typo_type == 'char':
        # Replace a character
        text_list[pos] = random.choice(string.ascii_letters)
    elif typo_type == 'swap':
        # Swap two adjacent characters
        text_list[pos], text_list[pos + 1] = text_list[pos + 1], text_list[pos]
    elif typo_type == 'missing':
        # Remove a character
        text_list.pop(pos)
    elif typo_type == 'extra':
        # Add an extra character
        text_list.insert(pos, text_list[pos])

    return ''.join(text_list)


def create_duplicate_variations(voter_record, duplicate_type):
    """Create different types of duplicate records"""
    duplicate = voter_record.copy()

    if duplicate_type == 'exact':
        # Exact duplicate with different Voter ID
        duplicate['Voter_ID'] = generate_voter_id()

    elif duplicate_type == 'typo_name':
        # Name with typo
        duplicate['Voter_ID'] = generate_voter_id()
        duplicate['Full_Name'] = create_typo(voter_record['Full_Name'], 'char')

    elif duplicate_type == 'missing_char':
        # Name with missing character
        duplicate['Voter_ID'] = generate_voter_id()
        duplicate['Full_Name'] = create_typo(voter_record['Full_Name'], 'missing')

    elif duplicate_type == 'extra_space':
        # Extra spaces in name
        duplicate['Voter_ID'] = generate_voter_id()
        name_parts = voter_record['Full_Name'].split()
        duplicate['Full_Name'] = '  '.join(name_parts)

    elif duplicate_type == 'case_change':
        # Different case
        duplicate['Voter_ID'] = generate_voter_id()
        duplicate['Full_Name'] = voter_record['Full_Name'].lower()

    elif duplicate_type == 'address_typo':
        # Same person, slight address difference
        duplicate['Voter_ID'] = generate_voter_id()
        duplicate['Address'] = create_typo(voter_record['Address'], 'char')

    elif duplicate_type == 'abbreviated':
        # Abbreviated name
        duplicate['Voter_ID'] = generate_voter_id()
        name_parts = voter_record['Full_Name'].split()
        if len(name_parts) > 1:
            name_parts[0] = name_parts[0][0] + '.'
        duplicate['Full_Name'] = ' '.join(name_parts)

    elif duplicate_type == 'father_name_diff':
        # Different father's name (might be legitimate but suspicious)
        duplicate['Voter_ID'] = generate_voter_id()
        duplicate['Father_Mother_Name'] = fake.name()

    elif duplicate_type == 'dob_typo':
        # Date of birth off by a day or month (data entry error)
        duplicate['Voter_ID'] = generate_voter_id()
        original_dob = datetime.strptime(voter_record['Date_of_Birth'], '%Y-%m-%d')
        new_dob = original_dob + timedelta(days=random.choice([1, -1, 30, -30]))
        duplicate['Date_of_Birth'] = new_dob.strftime('%Y-%m-%d')

    elif duplicate_type == 'phonetic':
        # Phonetically similar name
        duplicate['Voter_ID'] = generate_voter_id()
        # Simple phonetic variations
        replacements = {
            'ph': 'f', 'k': 'c', 'sh': 's', 'v': 'w'
        }
        name = voter_record['Full_Name'].lower()
        for old, new in replacements.items():
            if old in name:
                name = name.replace(old, new, 1)
                break
        duplicate['Full_Name'] = name.title()

    return duplicate


def generate_voter_dataset(n_records=1000, duplicate_percentage=15):
    """
    Generate synthetic voter data with intentional duplicates

    Args:
        n_records: Total number of unique records to generate
        duplicate_percentage: Percentage of records that will have duplicates
    """

    indian_states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'Gujarat',
                     'Rajasthan', 'Uttar Pradesh', 'West Bengal', 'Kerala', 'Punjab']

    voters = []

    print(f"Generating {n_records} unique voter records...")

    # Generate base voter records
    for i in range(n_records):
        voter = {
            'Voter_ID': generate_voter_id(),
            'Full_Name': fake.name(),
            'Father_Mother_Name': fake.name(),
            'Date_of_Birth': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            'Gender': random.choice(['Male', 'Female', 'Other']),
            'Address': fake.address().replace('\n', ', '),
            'City': fake.city(),
            'State': random.choice(indian_states),
            'PIN_Code': fake.postcode(),
            'Polling_Station': f"PS-{random.randint(1, 50):03d}",
            'Registration_Date': fake.date_between(start_date='-10y', end_date='today').strftime('%Y-%m-%d')
        }
        voters.append(voter)

    df_original = pd.DataFrame(voters)

    # Create duplicates
    n_duplicates = int(n_records * duplicate_percentage / 100)
    print(f"Creating {n_duplicates} duplicate records with various variations...")

    duplicate_types = [
        'exact', 'typo_name', 'missing_char', 'extra_space', 'case_change',
        'address_typo', 'abbreviated', 'father_name_diff', 'dob_typo', 'phonetic'
    ]

    duplicates = []
    duplicate_info = []  # Track which records are duplicates of which

    # Randomly select records to duplicate
    duplicate_indices = random.sample(range(len(voters)), n_duplicates)

    for idx in duplicate_indices:
        original_voter = voters[idx]
        duplicate_type = random.choice(duplicate_types)

        duplicate_voter = create_duplicate_variations(original_voter, duplicate_type)
        duplicates.append(duplicate_voter)

        duplicate_info.append({
            'Original_Voter_ID': original_voter['Voter_ID'],
            'Duplicate_Voter_ID': duplicate_voter['Voter_ID'],
            'Duplicate_Type': duplicate_type
        })

    df_duplicates = pd.DataFrame(duplicates)
    df_duplicate_info = pd.DataFrame(duplicate_info)

    # Combine all records
    df_combined = pd.concat([df_original, df_duplicates], ignore_index=True)

    # Shuffle the dataset
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"\nDataset Statistics:")
    print(f"Total records: {len(df_combined)}")
    print(f"Unique voters: {n_records}")
    print(f"Duplicate records: {n_duplicates}")
    print(f"Duplicate types distribution:")
    print(df_duplicate_info['Duplicate_Type'].value_counts())

    return df_combined, df_duplicate_info


# Generate the dataset
if __name__ == "__main__":
    # Generate dataset with 1000 unique records and 15% duplicates
    voter_data, duplicate_mapping = generate_voter_dataset(n_records=1000, duplicate_percentage=15)

    # Save to CSV files
    voter_data.to_csv('voter_database.csv', index=False)
    duplicate_mapping.to_csv('duplicate_ground_truth.csv', index=False)

    print("\n✅ Files created successfully!")
    print("📁 voter_database.csv - Main voter database with duplicates")
    print("📁 duplicate_ground_truth.csv - Ground truth for testing accuracy")
    print("\nYou can now use these files to test your duplicate detection system!")