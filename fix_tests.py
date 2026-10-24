with open('tests/test_score_cli.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == 'if __name__ == "__main__":':
        break
    new_lines.append(line)

with open('tests/test_score_cli.py', 'w') as f:
    f.writelines(new_lines)
