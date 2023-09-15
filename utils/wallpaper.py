import ctypes
import os
import random
from PIL import Image
def main(wallpaper_path):
    # 定义壁纸图片文件夹路径
    # wallpaper_folder = os.path.expanduser(r"E:\BaiduNetdiskDownload\sd_tzh\outputs\txt2img-samples\samples")

    # 获取图片文件夹中的所有图片文件
    # wallpapers = [f for f in os.listdir(wallpaper_folder) if f.endswith((".jpg", ".jpeg", ".png", ".bmp"))]

    # 循环更换壁纸

        # 随机选择一个壁纸
        # wallpaper_path = os.path.join(wallpaper_folder, random.choice(wallpapers))

        # 设置壁纸
    img = Image.open(wallpaper_path)
    img.show()
    # ans = input("y/n?")
    # if ans in ['y','Y']:
    #     SPI_SETDESKWALLPAPER = 20
    #     ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)

    # 等待继续更换壁纸
        


if __name__ == '__main__':
    main(r".\outputs\txt2img-samples\samples\00062.png")
