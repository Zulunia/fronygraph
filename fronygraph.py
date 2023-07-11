import requests
import time
from pyfiglet import Figlet
from datetime import datetime

# Example API URL (can be adjusted)
api_url = "http://192.168.1.205/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DataCollection=CommonInverterData&DeviceId=1"

def get_pac_value(api_url):
    try:
        # Request the JSON data from the API
        response = requests.get(api_url)
        data = response.json()

        # Check if the "PAC" key exists in the API response
        is_sleeping = ("PAC" not in data["Body"]["Data"])

        # Extract the current "PAC" value if it exists
        if not is_sleeping:
            pac_value = data["Body"]["Data"]["PAC"]["Value"]
        elif "DAY_ENERGY" in data["Body"]["Data"]:    # Check if DAY_ENERGY Key exists
                pac_value = data["Body"]["Data"]["DAY_ENERGY"]["Value"]  # Use "DAY_ENERGY" if "PAC" key doesn't exist (sleeping at night)
        else:
            pac_value = "0"
##      Some debug constants
#        is_sleeping = 1
#        return None, True

        return pac_value, is_sleeping
    except (requests.exceptions.RequestException, ValueError):
        # Return None and True (is_sleeping) if there's no response from the API or an error occurs
        return None, True

# Define the number of datapoints to display, the height and width of the graph
history_size = 64  # same as x-axis size
max_y_value = 5500
y_axis_height = 20
x_axis_length = history_size

# Create an empty list to store PAC values
pac_history = []

# Configure Figlet with the "banner" font
figlet = Figlet(font="banner")

# Define the sleep duration between updates (in seconds)
update_interval = 60

# Start an infinite loop to update and plot the data
while True:
    # Get the current PAC value and is_sleeping flag by making the API request
    pac_value, is_sleeping = get_pac_value(api_url)

    # Append the PAC value to the history list
    pac_history.append(pac_value)

    # Truncate the history list if it exceeds the desired size
    if len(pac_history) > history_size:
        pac_history = pac_history[-history_size:]

    if pac_value is not None and not is_sleeping:
        # Scale the PAC values to fit within the y-axis height
        scaled_values = [int(value / max_y_value * y_axis_height) for value in pac_history]

    # Clear the console screen
    print("\033c", end="")


    if is_sleeping and pac_value is not None: # If sleeping just show daily energy and no graph (for now)
        # Set text color to light blue
        light_blue = "\u001b[94m"
        reset_color = "\u001b[0m"

        # Print centered "STAND-BY" text in light blue
        standby_line = figlet.renderText("STAND-BY")
        centered_standby_line = standby_line.rstrip().center(x_axis_length)
        print(f"{light_blue}{centered_standby_line}{reset_color}")

        # Output the value of "DAY_ENERGY" under the "STAND-BY" text
        # Generate the ASCII art representation of the PAC value using Figlet
        day_energy = pac_value

        day_ascii = figlet.renderText("{:,}".format(day_energy) + " W")
        lines = day_ascii.split("\n")
        max_line_length = max(len(line) for line in lines)

#        print(f"{day_energy}")
        print('─' * x_axis_length)
        print("\n\n")
        print("Total: \n\n")
        centered_day_energy_lines = [line.center(x_axis_length) for line in lines]
        print(f"\n".join(centered_day_energy_lines) + "\n\u001b[0m")
    elif pac_value is None:  # if error or api unavailable
        # Set text color to flashing red
        flashing_red = "\u001b[5;91m"
        reset_color = "\u001b[0m"

        # Print centered and flashing "OFFLINE" text in red
        offline_line = figlet.renderText("OFFLINE")
        centered_offline_line = offline_line.rstrip().center(x_axis_length)
        print(f"{flashing_red}{centered_offline_line}{reset_color}")

        # Output hrule
        print('─' * x_axis_length, '\n')

        # Output the time when pac_value was None
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n\nContact lost: {current_time}")

    else:   # show PAC and Graph
        # Determine the text color based on the PAC value
        if pac_value < 1800:
            text_color = "\u001b[38;5;202m"  # Orange
        elif pac_value < 3500:
            text_color = "\u001b[38;5;226m"  # Yellow
        else:
            text_color = "\u001b[38;5;255m"  # White

        # Create the vertical bar graph representation with filled boxes
        for i in range(y_axis_height, 0, -1):
            line = ''.join(['█' if value >= i else ' ' for value in scaled_values])
            print(line)

        # Output the x-axis
        print('─' * x_axis_length, '\n')

        # Generate the ASCII art representation of the PAC value using Figlet
        pac_ascii = figlet.renderText("{:,}".format(pac_value) + " W")
        lines = pac_ascii.split("\n")
        max_line_length = max(len(line) for line in lines)


#        centered_day_energy_line = day_energy_ascii.rstrip().center(60)
        #centered_lines = [line.center(x_axis_length) for line in lines]
        #print(f"{text_color}\n".join(centered_lines) + "\n\u001b[0m")
        centered_lines = [f"{text_color}{line.center(x_axis_length)}\u001b[0m" for line in lines]
        print(f"\n".join(centered_lines))
#        print(f"{text_color}\n".join(centered_lines))

    # Sleep for the specified duration before updating again
    time.sleep(update_interval)
