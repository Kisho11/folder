import requests
import pandas as pd

post_ain = pd.read_csv("IMDB_images_22.csv")
post_ain_list = post_ain['links'].to_list()
print(post_ain_list)

index = 1
for img in post_ain_list:
    res = requests.get(img)
    file = open("imdb_image_"+str(index), "wb")
    file.write(res.content)
    file.close()
    index += 1
# response = requests.get("https://m.media-amazon.com/images/M/MV5BYjAyMzZkMjktOGM2Ni00MzgzLTgwOGYtN2FhOTE0NzhkYjE4XkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_.jpg")
#
# file = open("sample_image.png", "wb")
# file.write(response.content)
# file.close()