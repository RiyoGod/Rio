import os
import cv2
import numpy as np
import torch
from PIL import Image, ImageEnhance
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
from realesrgan import RealESRGAN
from io import BytesIO

# Telegram Bot Token
BOT_TOKEN = "7644887882:AAE8Us4J8-uultwW6ubtYxM7ddLYSiytvXs"

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Load Real-ESRGAN Model (CPU Mode)
device = torch.device("cpu")
model = RealESRGAN(device, scale=4)
model.load_weights("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRGAN_x4plus.pth")

# Function to Enhance Image
def enhance_image(image_path):
    img = Image.open(image_path)

    # Apply Color Enhancements
    img = ImageEnhance.Contrast(img).enhance(1.3)  # Increase contrast
    img = ImageEnhance.Brightness(img).enhance(1.2)  # Adjust brightness
    img = ImageEnhance.Color(img).enhance(1.5)  # Increase color depth

    # Convert to OpenCV Format
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

    # Apply AI Upscaling (Real-ESRGAN)
    img_tensor = model.predict(img_cv)

    # Convert Back to PIL
    img_upscaled = Image.fromarray(cv2.cvtColor(img_tensor, cv2.COLOR_BGR2RGB))

    # Save Output
    output_path = "enhanced_image.jpg"
    img_upscaled.save(output_path, "JPEG", quality=100)
    return output_path

# Handle Image Uploads
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_image(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path

    # Download Image
    downloaded_file = await bot.download_file(file_path)
    image_path = "input.jpg"
    with open(image_path, "wb") as img_file:
        img_file.write(downloaded_file.getvalue())

    # Process Image
    enhanced_image_path = enhance_image(image_path)

    # Send Enhanced Image
    await message.reply_photo(photo=InputFile(enhanced_image_path), caption="Here is your enhanced UHD image! 🚀")

    # Cleanup
    os.remove(image_path)
    os.remove(enhanced_image_path)

# Start Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
