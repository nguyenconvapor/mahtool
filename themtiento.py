def add_prefix_to_proxies(filepath, prefix_choice):
    """Adds a specified prefix to each line in a file containing IPs and ports.

    Args:
        filepath: The path to the file containing the IPs and ports.
        prefix_choice: An integer representing the prefix to add:
            1: socks5://
            2: socks4://
            3: http://
    """

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    prefixes = {
        1: "socks5://",
        2: "socks4://",
        3: "http://"
    }

    if prefix_choice not in prefixes:
        print("Invalid prefix choice. Please choose 1, 2, or 3.")
        return

    prefix = prefixes[prefix_choice]
    new_lines = [prefix + line.strip() for line in lines]

    try:
        with open(filepath, 'w') as f:  # Overwrites the original file
            f.writelines('\n'.join(new_lines))
        print(f"Prefix '{prefix}' added successfully to {filepath}")

    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")



if __name__ == "__main__":
    filepath = input("Enter the path to the file containing IPs and ports: ")
    print("Choose a prefix:")
    print("1: socks5://")
    print("2: socks4://")
    print("3: http://")


    while True:
        try:
            prefix_choice = int(input("Enter your choice (1, 2, or 3): "))
            if prefix_choice in [1, 2, 3]:
                break  # Exit loop if a valid choice is entered.
            else:
              print("Invalid input. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")


    add_prefix_to_proxies(filepath, prefix_choice)
