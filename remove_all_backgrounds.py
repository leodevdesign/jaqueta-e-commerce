import os
import glob
import cv2
import numpy as np

def remove_background(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Failed to load: {img_path}")
        return False

    if len(img.shape) == 3 and img.shape[2] == 4:
        rgb = img[:, :, :3]
    else:
        rgb = img

    h, w = rgb.shape[:2]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    # Sample border pixels to get the exact studio gray background color
    border_pixels = np.concatenate([rgb[0, :], rgb[-1, :], rgb[:, 0], rgb[:, -1]])
    bg_color = np.median(border_pixels, axis=0)

    diff = np.linalg.norm(rgb.astype(np.float32) - bg_color, axis=2)

    # Detect studio background: close to bg_color or low saturation + high brightness
    bg_candidate = (diff < 36) | ((sat < 18) & (val > 190))

    # Connected components starting from image edges to avoid cutting inner light highlights
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bg_candidate.astype(np.uint8), connectivity=8)
    border_labels = set(labels[0, :]).union(labels[-1, :]).union(labels[:, 0]).union(labels[:, -1])
    border_labels.discard(0)

    final_bg = np.isin(labels, list(border_labels))
    fg_mask = (~final_bg).astype(np.uint8) * 255

    # Refine mask edges
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_smooth = cv2.GaussianBlur(fg_mask, (3, 3), 0)

    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = fg_smooth

    cv2.imwrite(img_path, rgba)
    return True

def main():
    folder = os.path.join("assets", "angulos-3d")
    
    # Fix jaq-preta-.png naming to jaq-preta-8.png
    odd_preta = os.path.join(folder, "jaq-preta-.png")
    target_preta_8 = os.path.join(folder, "jaq-preta-8.png")
    if os.path.exists(odd_preta):
        if os.path.exists(target_preta_8):
            os.remove(target_preta_8)
        os.rename(odd_preta, target_preta_8)
        print("Renamed jaq-preta-.png -> jaq-preta-8.png")

    files = sorted(glob.glob(os.path.join(folder, "jaq-*.png")))
    # Exclude any temporary test files
    files = [f for f in files if not os.path.basename(f).startswith("test_")]

    print(f"Total angle images to process: {len(files)}")
    count = 0
    for f in files:
        success = remove_background(f)
        if success:
            count += 1
            print(f"[{count}/{len(files)}] Processed: {os.path.basename(f)}")

    # Clean up test files if they exist
    for test_f in ["test_cut.png", "test_preta.png"]:
        p = os.path.join(folder, test_f)
        if os.path.exists(p):
            os.remove(p)

    print(f"\nCompleted! {count} angle images processed with transparent backgrounds.")

if __name__ == "__main__":
    main()
