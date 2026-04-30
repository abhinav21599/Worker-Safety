import base64
with open(r"e:\Mini Project\Codeathon-2\Worker-Safety\assets\bg.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
print(encoded_string[:100]) # just check it worked
