import base64
import os

img_path = r"e:\Mini Project\Codeathon-2\Worker-Safety\assets\bg.png"
config_path = r"e:\Mini Project\Codeathon-2\Worker-Safety\src\config.py"

with open(img_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

with open(config_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the background image section
new_bg_css = f"""background-image: 
        linear-gradient(rgba(2, 6, 23, 0.8), rgba(2, 6, 23, 0.8)),
        url('data:image/png;base64,{b64}') !important;
    background-size: cover !important;
    background-attachment: fixed !important;"""

# We'll replace the existing background-image block
import re
pattern = r"background-image:.*?!important;"
content = re.sub(pattern, new_bg_css, content, flags=re.DOTALL)

# Also remove background-size if it exists
content = re.sub(r"background-size:.*?!important;", "", content)

with open(config_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated config.py with base64 background")
