# Read the contents of the sender_time.txt file
with open('sender_time.txt', 'r') as sender_file:
    sender_lines = sender_file.readlines()

# Read the contents of the receive_time.txt file
with open('receive time.txt', 'r') as receive_file:
    receive_lines = receive_file.readlines()

print(sender_lines)
# Extract the numbers from the sender_time.txt file
sender_numbers = [float(line.split(':')[1].strip()) for line in sender_lines]

# Extract the numbers from the receive_time.txt file
receive_numbers = [float(line.split(':')[1].strip()) for line in receive_lines]


# Perform the subtraction
results = [receiver - sender for receiver, sender in zip(receive_numbers, sender_numbers)]

# Define the percentages
percentages = [3, 5, 10, 15, 20]

# Calculate the adjusted results with percentages
adjusted_results = [result + (result * percentage / 100) for result in results for percentage in percentages]


# Print the results with percentages
for result, percentage in zip(results, percentages):
    print(f"{percentage}% : {result}")
