import numpy as np
from PIL import Image, ImageFilter

input_path = 'assets/images/jacket-main-iridescent.jpg'
cutout_path = 'assets/images/jacket-cutout.png'
depth_path = 'assets/images/jacket-depth.png'
normal_path = 'assets/images/jacket-normal.png'

# Load image
img = Image.open(input_path).convert('RGB')
w, h = img.size

# 1. Background removal / Alpha cutout
arr = np.array(img, dtype=np.float32)
max_rgb = np.max(arr, axis=2)

mask = np.clip((max_rgb - 8.0) / 18.0 * 255.0, 0, 255).astype(np.uint8)
mask_img = Image.fromarray(mask, mode='L').filter(ImageFilter.GaussianBlur(radius=1.2))

rgba = img.convert('RGBA')
rgba.putalpha(mask_img)
rgba.save(cutout_path, format='PNG')
print(f"Saved {cutout_path}")

# 2. Depth / Height Map Generation
gray = np.array(img.convert('L'), dtype=np.float32) / 255.0

y_indices, x_indices = np.indices((h, w))
cx, cy = w / 2.0, h / 2.0
dist_x = np.abs(x_indices - cx) / (w * 0.45)
dist_y = np.abs(y_indices - cy) / (h * 0.50)
radial_bulge = np.clip(1.0 - (dist_x**1.8 + dist_y**1.8), 0.0, 1.0)

mask_norm = np.array(mask_img, dtype=np.float32) / 255.0
depth = (radial_bulge * 0.65 + gray * 0.35) * mask_norm
depth_uint8 = np.clip(depth * 255.0, 0, 255).astype(np.uint8)
depth_img = Image.fromarray(depth_uint8, mode='L').filter(ImageFilter.GaussianBlur(radius=2.5))
depth_img.save(depth_path, format='PNG')
print(f"Saved {depth_path}")

# 3. Normal Map Generation via pure NumPy
depth_arr = np.array(depth_img, dtype=np.float32) / 255.0
dzdy, dzdx = np.gradient(depth_arr)
dzdx *= 5.0
dzdy *= 5.0

normal = np.zeros((h, w, 3), dtype=np.float32)
normal[:, :, 0] = -dzdx
normal[:, :, 1] = -dzdy
normal[:, :, 2] = 1.0

norm_len = np.sqrt(np.sum(normal**2, axis=2, keepdims=True)) + 1e-6
normal /= norm_len

normal_rgb = np.clip((normal * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
normal_img = Image.fromarray(normal_rgb, mode='RGB')
normal_img.save(normal_path, format='PNG')
print(f"Saved {normal_path}")
print("All maps created successfully!")
