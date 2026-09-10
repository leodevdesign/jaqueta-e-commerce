import cv2
import numpy as np

def generate_maps(input_path, depth_out_path, norm_out_path, is_front=True):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]
    
    b, g, r, alpha = cv2.split(img)
    mask = (alpha > 20).astype(np.float32)
    
    # Smooth mask
    mask_smooth = cv2.GaussianBlur(mask, (5, 5), 0)
    
    # Luminance
    gray = cv2.cvtColor(cv2.merge([b, g, r]), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    
    # Distance transform from mask boundary to generate natural cylindrical/torso body volume
    dist_map = cv2.distanceTransform((mask * 255).astype(np.uint8), cv2.DIST_L2, 5)
    max_dist = np.max(dist_map) + 1e-5
    dist_norm = dist_map / max_dist
    
    # Radial torso curvature
    y_idx, x_idx = np.indices((h, w))
    cx, cy = w / 2.0, h * 0.48
    norm_x = np.abs(x_idx - cx) / (w * 0.45)
    norm_y = np.abs(y_idx - cy) / (h * 0.48)
    torso_bulge = np.clip(1.0 - (norm_x**1.8 + norm_y**1.8 * 0.8), 0.0, 1.0)
    
    # Combine: deep torso volume + distance transform for round sleeves/shoulders + high-frequency fabric fold details
    base_volume = np.sqrt(dist_norm) * 0.65 + torso_bulge * 0.35
    depth = (base_volume * 0.72 + gray * 0.28) * mask_smooth
    depth = np.clip(depth * 255.0, 0, 255).astype(np.uint8)
    depth = cv2.GaussianBlur(depth, (3, 3), 0)
    
    cv2.imwrite(depth_out_path, depth)
    print(f"Saved depth map: {depth_out_path}")
    
    # Normal Map
    depth_float = depth.astype(np.float32) / 255.0
    dzdy, dzdx = np.gradient(depth_float)
    dzdx *= 4.5
    dzdy *= 4.5
    
    normal = np.zeros((h, w, 3), dtype=np.float32)
    normal[:, :, 0] = -dzdx if is_front else dzdx
    normal[:, :, 1] = -dzdy
    normal[:, :, 2] = 1.0
    
    norm_len = np.sqrt(np.sum(normal**2, axis=2, keepdims=True)) + 1e-6
    normal /= norm_len
    
    normal_bgr = np.clip((normal * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    cv2.imwrite(norm_out_path, normal_bgr)
    print(f"Saved normal map: {norm_out_path}")

def main():
    # Front (jaq-ver-1.png)
    generate_maps(
        'assets/angulos-3d/jaq-ver-1.png',
        'assets/angulos-3d/ver_front_depth.png',
        'assets/angulos-3d/ver_front_norm.png',
        is_front=True
    )
    # Back (jaq-ver-5.png)
    generate_maps(
        'assets/angulos-3d/jaq-ver-5.png',
        'assets/angulos-3d/ver_back_depth.png',
        'assets/angulos-3d/ver_back_norm.png',
        is_front=False
    )

if __name__ == "__main__":
    main()
