import csv


def append_file_contents(source_filename, target_filename):
    """
    Append feedback entries (label,sentence) from source_filename
    into target_filename using the new Jigsaw-style CSV format:
        text,toxicity,severe_toxicity,obscene,threat,insult,identity_attack,sexual_explicit

    Feedback label '1' (offensive) → toxicity scores set to 1.0
    Feedback label '0' (clean)     → toxicity scores set to 0.0
    """
    with open(source_filename, 'r', encoding='utf-8') as source_file:
        reader = csv.reader(source_file)
        next(reader, None)  # Skip header

        with open(target_filename, 'a', newline='', encoding='utf-8') as target_file:
            writer = csv.writer(target_file)
            for row in reader:
                if len(row) < 2:
                    continue
                label, text = row[0].strip(), row[1].strip()
                if not text:
                    continue

                # Map feedback label to toxicity scores
                score = 1.0 if label == '1' else 0.0
                # text,toxicity,severe_toxicity,obscene,threat,insult,identity_attack,sexual_explicit
                writer.writerow([text, score, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Example usage:
# Assume 'file1.txt' contains "Line 1\nLine 2" and 'file2.txt' contains "Line 3\nLine 4"
# The code below will append the content of 'file2.txt' to the end of 'file1.txt'
# resulting in 'file1.txt' containing "Line 1\nLine 2\nLine 3\nLine 4"