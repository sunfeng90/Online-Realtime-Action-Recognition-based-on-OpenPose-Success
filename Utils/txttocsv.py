lines = []
with open('origin_data.txt') as f:
    for line in f:
        if line:
            line = line.rstrip()
            line = line.replace(" ", ",", 36)
            line = line + "\n"
            lines.append(line)
file1 = open('data_with_scene.csv', 'w')
file1.writelines(lines)
file1.close()