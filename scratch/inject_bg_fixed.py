import base64
import os

img_path = r"e:\Mini Project\Codeathon-2\Worker-Safety\assets\bg.png"
config_path = r"e:\Mini Project\Codeathon-2\Worker-Safety\src\config.py"

if os.path.exists(img_path):
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the new base style block
    new_base_style = f"""html, body, .stApp {{
    font-family: 'Outfit', 'Inter', sans-serif;
    background-color: {{t['bg']}} !important;
    background-image: 
        linear-gradient(rgba(2, 6, 23, 0.85), rgba(2, 6, 23, 0.85)),
        url('data:image/png;base64,{b64}') !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}}"""

    # We use a very specific replacement for the old block
    import re
    pattern = r"html, body, \.stApp \{{.*?\}}"
    content = re.sub(pattern, new_base_style, content, flags=re.DOTALL)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Success")
else:
    print(f"Error: {img_path} not found")
