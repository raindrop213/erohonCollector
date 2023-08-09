import tkinter as tk
import customtkinter
import tkinter.font as tkFont

# https://zhuanlan.zhihu.com/p/491731567
root = tk.Tk()
root.geometry("400x240")

textExample=tk.Text(root, height=10)
textExample.pack()

font_1 = customtkinter.CTkFont(family="Arial", size=16, weight="bold", slant="italic")

print(list(tkFont.families()))
root.mainloop()

# font_list = list(tkFont.families())
# self.fonts_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=font_list)
# self.fonts_menu.grid(row=7, column=0, padx=20, pady=20, sticky="s")
# self.fonts_menu.set("Arial")

# def joinimages(images, quality, resolution):
#     return images[0].save(os.path.join(file_path, f'q{quality} r{resolution}.pdf'),  quality=quality, resolution=resolution, save_all=True, append_images=images[1:])

# all_images[0].save(os.path.join(file_path, 'q95 r-.pdf'), quality=95, save_all=True, append_images=all_images[1:])
# joinimages(all_images, 95, 100)
# joinimages(all_images, 95, 200)
# joinimages(all_images, 95, 300)
