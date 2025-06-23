import re
import urllib.request
import os

id_counter = 1

while True:
    content = input("Enter content (or 'quit' to exit): ")
    if content.lower() == 'quit':
        break

    image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
    
    for url in image_urls:
        ext = os.path.splitext(url)[1] or '.jpg'
        filename = f"image_{id_counter}{ext}"
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded: {filename}")
        id_counter += 1
