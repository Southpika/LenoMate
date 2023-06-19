import screen_brightness_control as sbc
import tkinter as tk
from tkinter import ttk

# 创建一个 Tkinter 窗口
window = tk.Tk()
window.title("屏幕亮度控制")
window.geometry("300x150")

# 设置整个 GUI 的背景颜色为淡蓝色
# window.configure(bg="#A4D3EE")

# 创建一个样式对象
style = ttk.Style(window)

# 设置窗口标题的样式
style.configure("TLabel", font=("Arial", 12))

# 设置亮度控制滑块的样式
style.configure("Custom.Horizontal.TScale",
                # background="#A4D3EE",
                troughcolor="#DCEFFB",
                )

# 函数：调节屏幕亮度
def set_brightness(brightness):
    brightness = int(float(brightness))
    sbc.set_brightness(brightness)
    current_brightness = sbc.get_brightness()
    brightness_label.config(text=f"当前亮度：{current_brightness}%", style="TLabel")

# 创建亮度控制滑块
brightness_slider = ttk.Scale(window, from_=0, to=100, orient="horizontal", command=set_brightness, style="Custom.Horizontal.TScale",length=800)
brightness_slider.set(sbc.get_brightness())
brightness_slider.pack(pady=30, padx=20)

# 创建当前亮度标签
current_brightness = sbc.get_brightness()
brightness_label = ttk.Label(window, text=f"当前亮度：{current_brightness}%", style="TLabel")
# brightness_label.config(background="#A4D3EE")
brightness_label.pack()


# 运行 GUI 主循环
window.mainloop()
