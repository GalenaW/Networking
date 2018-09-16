import pickle

file = open("picture.png", "rb")
data = []
i=0

for i in range(
    data.append(file.read(512))
    if not data[i]:
        break
    i=i+1

file.close()

file2 = open("copy.png", "wb")

for chunk in data:
    file2.write(chunk)
    
file2.close()