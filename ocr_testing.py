import ddddocr

ocr = ddddocr.DdddOcr()

image = open("captcha.png", "rb").read()
result = ocr.classification(image)
print(result)