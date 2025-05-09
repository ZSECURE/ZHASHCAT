import argparse
import pandas as pd
from neo4j import GraphDatabase

def get_users_from_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        query = "MATCH (u:User) RETURN u.name AS username, u.enabled AS enabled"
        result = session.run(query)
        users = {record["username"].lower(): record["enabled"] for record in result}
    driver.close()
    return users

def parse_password_file(password_file):
    with open(password_file, 'r') as file:
        passwords = {}
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 3:
                domain_user, _, password = parts
                domain, user = domain_user.split('\\')
                email_format_username = f"{user}@{domain}".lower()
                if password == "":
                    password = "[BLANK_PASSWORD]"
                passwords[email_format_username] = password
    return passwords

def mask_password(password):
    if password == "[BLANK_PASSWORD]":
        return password
    if len(password) <= 4:
        return password
    return password[:4] + '*' * (len(password) - 4)

def filter_and_sort_users(user_data, passwords, filter_keywords=None, min_password_length=None, sort_key=None, strict=False):
    filtered_users = []
    for username, password in passwords.items():
        if (filter_keywords is None or any(
            (password == keyword if strict else keyword.lower() in password.lower())
            for keyword in filter_keywords
        )) and (min_password_length is None or len(password) < min_password_length):
            enabled = user_data.get(username, "Unknown")
            masked_password = mask_password(password)
            filtered_users.append((username, enabled, masked_password))
    
    if sort_key == 'username':
        filtered_users.sort(key=lambda x: x[0])
    elif sort_key == 'enabled':
        filtered_users.sort(key=lambda x: str(x[1]))
    elif sort_key == 'password':
        filtered_users.sort(key=lambda x: x[2])

    return filtered_users

def write_to_excel(output_file, user_data, passwords, filter_keywords, min_password_length, sort_key, strict):
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        # Write filtered sheets based on keywords
        for filter_keyword in filter_keywords:
            filtered_users = filter_and_sort_users(user_data, passwords, filter_keywords=[filter_keyword], sort_key=sort_key, strict=strict)
            sheet_name = (filter_keyword or 'All Users')[:31]  # Excel sheet names must be 31 characters or less
            df = pd.DataFrame(filtered_users, columns=['Username', 'Enabled', 'Password'])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Write additional sheet based on password length
        if min_password_length is not None:
            length_filtered_users = filter_and_sort_users(user_data, passwords, filter_keywords=None, min_password_length=min_password_length, sort_key=sort_key, strict=False)
            length_sheet_name = f"Password < {min_password_length}"
            df_length = pd.DataFrame(length_filtered_users, columns=['Username', 'Enabled', 'Password'])
            df_length.to_excel(writer, sheet_name=length_sheet_name[:31], index=False)

def print_to_screen(filtered_users):
    print(f"{'Username':<30} {'Enabled':<10} {'Password':<20}")
    print("-" * 60)
    for username, enabled, masked_password in filtered_users:
        print(f"{username:<30} {str(enabled):<10} {masked_password:<20}")

def main():
    parser = argparse.ArgumentParser(description="Dump users and their status from Neo4j and compare with a password list.")
    parser.add_argument('--uri', required=True, help='The URI of the Neo4j database.')
    parser.add_argument('--user', required=True, help='The username for the Neo4j database.')
    parser.add_argument('--password', required=True, help='The password for the Neo4j database.')
    parser.add_argument('--password-file', required=True, help='The path to the password file.')
    parser.add_argument('--output-file', help='The path to the output Excel file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Output to screen instead of a file.')
    parser.add_argument('--sort', choices=['username', 'enabled', 'password'], help='Sort the output by username, enabled status, or password.')
    parser.add_argument('--filter', help='Comma-separated list of keywords to filter users with passwords containing any of these substrings.')
    parser.add_argument('--min-password-length', type=int, help='Filter users with passwords shorter than this length.')
    parser.add_argument('--strict', action='store_true', help='Enable strict filtering where passwords must exactly match the filter keywords.')

    args = parser.parse_args()

    user_data = get_users_from_neo4j(args.uri, args.user, args.password)
    passwords = parse_password_file(args.password_file)

    filter_keywords = args.filter.split(',') if args.filter else [None]

    if args.verbose:
        for filter_keyword in filter_keywords:
            filtered_users = filter_and_sort_users(user_data, passwords, filter_keywords=[filter_keyword], min_password_length=args.min_password_length, sort_key=args.sort, strict=args.strict)
            print(f"\nFilter: {filter_keyword or 'None'}")
            print_to_screen(filtered_users)
    else:
        if not args.output_file:
            print("Error: --output-file is required unless -v/--verbose is specified.")
            return
        write_to_excel(args.output_file, user_data, passwords, filter_keywords, args.min_password_length, args.sort, args.strict)

if __name__ == "__main__":
    main()
