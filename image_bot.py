import os
import cv2
import numpy as np
from PIL import Image
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor

# Telegram Bot Token
BOT_TOKEN = "7644887882:AAE8Us4J8-uultwW6ubtYxM7ddLYSiytvXs"

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Initialize Super-Resolution Model
sr = cv2.dnn_superres.DnnSuperResImpl_create()
model_path = "ESPCN_x4.pb"  # Path to the model file

# Check if the model file exists
if not os.path.exists(model_path):
    print(f"Model file '{model_path}' not found. Please download it and place it in the current directory.")
    exit()

sr.readModel(model_path)
sr.setModel("espcn", 4)  # Using ESPCN 4x upscaling

# Function to Enhance Image
def enhance_image(image_path):
    img = cv2.imread(image_path)
    img_upscaled = sr.upsample(img)  # Apply Super-Resolution

    output_path = "enhanced_image.jpg"
    cv2.imwrite(output_path, img_upscaled, [cv2.IMWRITE_JPEG_QUALITY, 100])
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
