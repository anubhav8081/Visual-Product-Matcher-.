# pip install icrawler

import os
from icrawler.builtin import BingImageCrawler

# list of categories
categories = [
    "apple", "banana", "mango", "orange", "pineapple", "grapes", "strawberry",
    "watermelon", "papaya", "pomegranate", "potato", "onion", "tomato", "cucumber",
    "carrot", "broccoli", "cauliflower", "capsicum", "laptop", "keyboard", "mouse",
    "phone", "headphones", "bicycle", "bus", "train", "airplane", "ship", "motorcycle",
    "shoes", "bag", "watch", "guitar", "piano", "violin", "camera", "television",
    "chair", "table", "bed", "sofa", "cup", "bottle", "plate", "spoon", "ball", "clock"
]

save_dir = "Dummy"
os.makedirs(save_dir, exist_ok=True)

for category in categories:
    category_dir = os.path.join(save_dir, category)
    os.makedirs(category_dir, exist_ok=True)

    print(f"🔎 Downloading images for: {category}")
    crawler = BingImageCrawler(storage={"root_dir": category_dir})
    crawler.crawl(keyword=category, max_num=5)

print(f"🎉 Download complete! Check '{save_dir}' folder.")
