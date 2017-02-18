import subprocess

def colorName(red, green, blue):
    p = subprocess.Popen(['./colorName', str(red), str(green), str(blue)],
        stdout=subprocess.PIPE)

    out, err = p.communicate()
    return out.rstrip()

# print(colorName(191, 92, 93))