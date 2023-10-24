#!/usr/bin/python3

import re
import argparse
import os

def process_hashes(hash_list, search_terms, output_dir=None):
    for term in search_terms:
        matching_hashes = []

        for h in hash_list:
            modified_hash = re.sub(r':(.+?):', '::', h)
            post_colon_data = modified_hash.split("::")[-1] if "::" in modified_hash else ""

            # Using lower() to make the search case-insensitive
            if term.lower() in post_colon_data.lower():
                matching_hashes.append(modified_hash)        
        # If output directory is provided, write the results to a file named after the search term
        if output_dir:
            with open(os.path.join(output_dir, f"{term}.txt"), 'w') as f:
                for match in matching_hashes:
                    f.write(match + '\n')
        else:
            # If no output directory, print the results to the console
            for match in matching_hashes:
                print(match)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search hashes for given terms.')

    # Argument definitions
    parser.add_argument('-hl', '--hash-list', type=str, help='File with a list of hashes.')
    parser.add_argument('-st', '--search-terms', type=str, nargs='*', help='Terms to search for in hashes.')
    parser.add_argument('positional_hash_input', type=str, nargs='?', help='File with a list of hashes or a single hash.', default=None)
    parser.add_argument('positional_search_terms', type=str, nargs='*', help='Terms to search for in hashes.', default=[])
    parser.add_argument('--output', type=str, help='Directory where search results should be written.')

    args = parser.parse_args()

    # Determine source of hashes
    if args.hash_list:
        with open(args.hash_list, 'r') as f:
            hashes = [line.strip() for line in f]
    elif args.positional_hash_input and os.path.exists(args.positional_hash_input):
        with open(args.positional_hash_input, 'r') as f:
            hashes = [line.strip() for line in f]
    elif args.positional_hash_input:
        hashes = [args.positional_hash_input]
    else:
        print("Error: No valid hash input provided.")
        exit(1)

    # Determine search terms
    if args.search_terms:
        search_terms = args.search_terms
    else:
        search_terms = args.positional_search_terms

    process_hashes(hashes, search_terms, args.output)
