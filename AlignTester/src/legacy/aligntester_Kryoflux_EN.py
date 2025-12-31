
import re
import math
import sys

def calculate_graph_bar(average):
    """
    Generates a graphical representation of the average with specific conditions
    """
    # Define total bar length
    total_length = 50
    
    # Calculate number of blocks to fill
    filled_blocks = math.floor((average / 100) * total_length)
    
    # Determine text to display
    if 99.000 <= average <= 99.999:
        alignment_text = "Align Perfect"
    elif 97.000 <= average <= 98.999:
        alignment_text = "Align Good"
    elif 96.000 <= average <= 97.999:
        alignment_text = "Align Average"
    elif average < 96.000:
        alignment_text = "Align Poor"
    else:
        alignment_text = ""
    
    # Build graph bar
    bar = "[" + "█" * filled_blocks + " " * (total_length - filled_blocks) + "]"
    
    return f"{bar} {average:.3f}% {alignment_text}"

def extract_percentage_values(filename, limit=160):
    """
    Extracts numerical values between [] ending with %
    Calculates their average, limiting to first 160 values
    With 3 decimal place precision
    """
    values_with_details = []
    
    try:
        # Open and read file
        with open(filename, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                # Regex to find values between [] ending with %
                pattern = r'\[(\d+(?:\.\d+)?)\s*%\]'
                
                # Search for matches in the line
                results = re.findall(pattern, line)
                for result in results:
                    value = float(result)
                    
                    # Extract number at the start of the line (between 00.0 and 85.1)
                    number_match = re.search(r'^(\d+\.\d)', line)
                    number = float(number_match.group(1)) if number_match else 0.0
                    
                    values_with_details.append({
                        'value': value, 
                        'line_number': line_number, 
                        'number': number,
                        'original_line': line.strip()
                    })
            
            # Sort values by the number found
            values_with_details.sort(key=lambda x: x['number'])
            
            # Limit to first 160 values
            used_values = values_with_details[:limit]
            
            # Calculate and display average
            if used_values:
                values = [v['value'] for v in used_values]
                average = sum(values) / len(values)
                
                # Calculate track_max (last value found)
                track_max = values_with_details[-1]['number'] if values_with_details else 0
                
                # Verify if track_max corresponds to half the total number of values
                total_values_count = len(values_with_details)
                track_max_verification = total_values_count / 2
                
                # Calculate track_normal (number of used values divided by 2)
                track_normal = len(used_values) / 2
                
                # Display details of used values
                print("\nUsed Values Details:")
                for detail in used_values:
                    print(f"Line {detail['line_number']} - Number {detail['number']} : {detail['original_line']} (Value : {detail['value']}%)")
                
                # Display additional information
                print(f"\nTotal number of values found: {total_values_count}")
                print(f"Number of values used for average: {len(used_values)}")
                print(f"Total number of tracks read: {track_max}")
                print(f"Total number of tracks for average calculation: {track_normal}")
                
                #print("\nGraphical Representation:")
                print(calculate_graph_bar(average))
            else:
                print("No percentage values found.")
    
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return values_with_details

# Check if a filename is provided as an argument
if len(sys.argv) < 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

# Get filename from arguments
filename = sys.argv[1]

# Launch extraction and calculation
results = extract_percentage_values(filename)

