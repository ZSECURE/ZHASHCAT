#!/usr/bin/python3

def parse_passwords(file_path):
    passwords = {}
    recovered_passwords = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(':')
            username = parts[0]
            password_hash = parts[1]
            password = parts[2] if len(parts) > 2 else None

            if password:
                recovered_passwords.append(password)

            if password_hash not in passwords:
                passwords[password_hash] = []
            passwords[password_hash].append(username)

    return passwords, recovered_passwords

def find_shared_passwords(passwords):
    shared_passwords = {}

    for password_hash, usernames in passwords.items():
        if len(usernames) > 1:
            shared_passwords[password_hash] = usernames

    return shared_passwords

def main():
    file_path = 'passwords.txt'
    passwords, recovered_passwords = parse_passwords(file_path)

    shared_passwords = find_shared_passwords(passwords)

    print('Users with the same password:')
    for password_hash, usernames in shared_passwords.items():
        print(f'Password Hash: {password_hash}')
        print(f'Usernames:')
        for username in usernames:
            print(f'- {username}')
        print()

    print('Recovered passwords:')
    if len(recovered_passwords) == 0:
        print('No recovered passwords found.')
    else:
        for password in recovered_passwords:
            print(password)

if __name__ == '__main__':
    main()
