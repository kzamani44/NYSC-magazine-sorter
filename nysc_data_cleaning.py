import pandas as pd
import os
import re
import glob
import requests

"""
    TODO:
    1. remove duplicate data
    2. transform all names,gender and LGA to lower case
"""

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Read the data from the excel file
df = pd.read_excel('ADAMAWA COPA 2024 BATCH C I & II  (Responses).xlsx')



# Rename columns
df = df.rename(columns={
    "PONE NUMBER": "Phone number",
    "FULL NAME": "Full name",
    "STATE CODE (e.g., AD/24C/0000)": "State code",
    "GENDER": "Gender",
    "PASSPORT PHOTOGRAPH": "Passport Photo",
})

# Drop duplicates entries by name,gender and state code
df = df.drop_duplicates(subset=['Full name', 'Gender', 'State code'])

'''
    Basic data cleaning
    - Capitalize first name
    - capitalize gender
    - make state code all caps and remove whitespaces
    - remove whitespaces for phone numbers
'''
df['Full name'] = df['Full name'].str.capitalize()
df['Gender'] = df['Gender'].str.capitalize()
df['State code'] = df['State code'].str.upper()
df['State code'] = df['State code'].str.replace(' ','')
df['Passport Photo'] = df['Passport Photo'].str.replace(' ', '')
df['LGA OF PPA'] = df['LGA OF PPA'].str.strip()


'''
    TODO:
    - make sure that you create a general folder based on the Batch
    - Inside the general folder, create folders based on the LGAs
    - Inside the LGAs folder, save corp member data inside based on their LGA
'''

# Folder where your Excel files are stored
base_dir = r"C:\Users\ADMIN\Desktop\NYSC data"

# Find the first Excel file in the folder (ignores temp files like ~$)
excel_files = [f for f in glob.glob(os.path.join(base_dir, "*.xlsx")) if not os.path.basename(f).startswith("~$")]

if not excel_files:
    raise FileNotFoundError("No Excel files found in the folder.")

# Use the first Excel file (or loop if multiple)
file_path = excel_files[0]

# Extract just the filename (without extension)
file_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]

# Regex to capture the batch part (e.g., "BATCH C I & II", "BATCH AI & AII")
match = re.search(r"(BATCH.*?)(?:\s*\(|$)", file_name_no_ext, re.IGNORECASE)

if match:
    batch_name = match.group(1).strip()   # e.g. "BATCH C I & II"
else:
    batch_name = "Batch_Unknown"

# Create batch folder
batch_folder = os.path.join(base_dir, batch_name)
os.makedirs(batch_folder, exist_ok=True)

# Get unique LGAs from Dataframe
lgas = df['LGA OF PPA'].unique()
# print(batch_folder)

for _,row in df.iterrows():
    # Clean up folder name (remove extra spaces, make lowercase, replace spaces with underscores)
    lga_folder = row['LGA OF PPA']
    # print(lga_folder)

    # Build the full path
    lga_folder_path = os.path.join(batch_folder, lga_folder)

    # Create the folder if it doesn’t exist
    os.makedirs(lga_folder_path, exist_ok=True)

    # Convert all fields to strings safely
    full_name = str(row['Full name']) if pd.notna(row['Full name']) else "unknown_name"
    state_code = str(row['State code']) if pd.notna(row['State code']) else "unknown_code"
    phone_number = str(row['Phone number']) if pd.notna(row['Phone number']) else "unknown_phone"

    # Clean up filenames: replace spaces with slashes and underscores
    safe_state_code = re.sub(r"[\/\\]", "_", state_code)

    # Safe phone numbers
    safe_phone = re.sub(r"[\/\\\s]", "_", phone_number)

    # Use name or state code as filename
    file_name = f"{row['Full name'].strip()}_{safe_state_code}_{safe_phone}.jpg"
    file_path = os.path.join(lga_folder_path, file_name)

    # Get and download the photo from google drive
    photo_url = str(row['Passport Photo'])
    # print(f"photo url - {photo_url}")

    if "id=" in photo_url:
        file_id = photo_url.split("id=")[-1]
        # print(f"file_id - {file_id}")
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        try:
            # Download image
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print("Saved: ",file_path)
            else:
                print("Failed to download: ",photo_url)

        except Exception as e:
            print("Error downloading", photo_url, ":", e)