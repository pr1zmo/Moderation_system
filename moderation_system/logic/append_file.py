def get_class(label: str) -> str:
    """Convert label to class: 0 (positive) -> 2 (neither), 1 (offensive) -> 1 (offensive)"""
    if label == '0':
        return '2'
    return '1'

def get_neither(label: str) -> str:
    """Get neither count: 3 for positive, 0 for offensive"""
    if label == '0':
        return '3'
    return '0'

def append_file_contents(source_filename, target_filename):
    # try:
        # Open the source file in read mode ('r')
        with open(source_filename, 'r') as source_file:
            next(source_file)  # Skip header
            
            # Get current line count in target file
            with open(target_filename, 'r') as target_file:
                # Count existing lines (subtract 1 for header)
                current_count = sum(1 for _ in target_file) - 1
            
            # Append new data
            with open(target_filename, 'a') as target_file:
                for line in source_file:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    # Parse CSV: label,sentence
                    parts = line.split(',', 1)  # Split only on first comma
                    if len(parts) != 2:
                        continue
                    
                    label, tweet = parts
                    
                    '''
                    Format: index,count,hate_speech,offensive_language,neither,class,tweet
                    '''
                    formatted_line = f"{current_count},{3},{0},{label[0]},{get_neither(label)},{get_class(label)},{tweet}\n"
                    target_file.write(formatted_line)
                    current_count += 1
    # except FileNotFoundError:
    #     print(f"Error: One of the files not found. Check file names.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")

# Example usage:
# Assume 'file1.txt' contains "Line 1\nLine 2" and 'file2.txt' contains "Line 3\nLine 4"
# The code below will append the content of 'file2.txt' to the end of 'file1.txt'
# resulting in 'file1.txt' containing "Line 1\nLine 2\nLine 3\nLine 4"