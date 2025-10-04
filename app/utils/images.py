from PIL import Image, ImageStat
import io

def basic_quality(img_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # crude brightness estimate
    stat = ImageStat.Stat(img)
    luma = sum(stat.mean)/3
    too_dark = luma < 25
    # crude blur check via resize trick
    small = img.resize((16,16)).resize(img.size)
    diff = ImageStat.Stat(Image.blend(img, small, 0.5)).var
    blur_indicator = sum(diff)/3
    too_blurry = blur_indicator < 50
    return {"too_dark": too_dark, "too_blurry": too_blurry, "ok": not (too_dark or too_blurry)}
