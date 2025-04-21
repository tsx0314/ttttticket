import ddddocr

def captcha(path):
    image = open(path, "rb").read()
    result = ocr.classification(image)
    return result