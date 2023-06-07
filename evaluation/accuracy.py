import os
import sys
sys.path.append('../')
from utilities.pmu_csv_parser import parse_csv_data
import matplotlib.pyplot as plt
from jpt_algo_evaluation.jpt_algo import calculate_complex_voltage, jpt_algo, phase_angle_and_magnitude_from_complex_voltage, calculate_approximation_error,calculate_angle_error, calculate_approximation_error_statistics,calculate_approximation_error_statistics_1


# Define the folder path and percentage values
folder_path = "../5k/"
percentage_values = ["3%", "5%", "10%", "15%", "20%"]

# Initialize lists to store the error statistics
averages = []
std_devs = []
max_errors = []

truthy_pmu_csv_data = parse_csv_data(
    '../pmu8_5k.csv',
    "TimeTag",
    ["Magnitude01", "Magnitude02", "Magnitude03"],
    ["Angle01", "Angle02", "Angle03"]
)

# Iterate over the percentage values
for percentage in percentage_values:
    # Iterate over the CSV files in the subfolder
    for csv_file in ["lab1_res.csv", "lab2_res.csv", "lab3_res.csv"]:
        # Construct the path for the CSV file
        csv_path = os.path.join(folder_path, percentage, csv_file)

        # Parse the CSV data
        received_pmu_data = parse_csv_data(
            csv_path,
            "index",
            ["magnitude"],
            ["phase_angle"]
        )

        # Get the magnitudes
        y_received = received_pmu_data["magnitudes"][0]
        y_truthy = truthy_pmu_csv_data["magnitudes"][0]

        # Calculate the error statistics
        average, std_dev, max_error = calculate_approximation_error_statistics_1(y_truthy, y_received)


        # Append the error statistics to the respective lists
        averages.append(average)
        std_devs.append(std_dev)
        max_errors.append(max_error)

# Print the error statistics
for i, percentage in enumerate(percentage_values):
    for j in range(3):
        print(f"For {percentage} - lab{j+1}_res.csv:")
        print(f"Average: {averages[i*3+j]}")
        print(f"Standard Deviation: {std_devs[i*3+j]}")
        print(f"Maximum Error: {max_errors[i*3+j]}")
        print()

# print(len(averages))
# print(len(std_devs))
def combine_res(data):
    cal_res =[]
    for i in range(0,len(data),3):
        subset = data[i:i+3]
        # print(subset)
        average = sum(subset) /3
        # print(average)
        cal_res.append(average)

    return cal_res

y_mag = combine_res(averages)
std_mag = combine_res(std_devs)

# Scale the standard deviations to determine error bar lengths
scaling_factor = 1.96  # 95% confidence interval
error_lengths = [scaling_factor * std_dev for std_dev in std_mag]

print(y_mag, "\n")
print(std_mag)

missing_rate = [0.03,0.05,0.1,0.15,0.2]
x = [val * 100 for val in missing_rate]
# Plot the graph with error bars
plt.errorbar(x, y_mag, yerr=error_lengths, fmt='o', capsize=5)
plt.plot(x,y_mag)
plt.xticks(x, percentage_values)
plt.xlabel("Percentage")
plt.ylabel("Y")
plt.title("Graph with Error Bars")
plt.show()
