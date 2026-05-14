# Annotated Image and Binary Mask Visualization (R and Python Versions)

This project helps visualize annotations from VIA (VGG Image Annotator) `.json` files by drawing the annotated regions on the original image and creating a binary mask. Two implementations are provided: one in **R** and one in **Python**.

---

## 🧪 Features

- Supports **polygon annotations** from VIA JSON format.
- Displays original image with overlaid annotations.
- Generates a binary mask of annotated regions.
- Saves visualizations as PNG images.
- Available in both **R** and **Python** for flexibility.

---

## 📁 Folder Structure

```
project/
├── sample_visualization.R          # R visualization script
├── sample_visualization_2.ipynb    # Python visualization script
├── 2019Mohakhali (1).json          # VIA JSON annotation file
├── 2019Mohakhali (1).jpg           # Original image file
├── original_annotated.png          # Annotated image output
├── binary_mask.png                 # Binary mask output
```

---

## 📦 Requirements

### 🧬 R Dependencies

Install these packages if not already installed:

```r
install.packages(c("ggplot2", "jsonlite", "png", "jpeg", "grid", "cowplot"))
```

### 🧪 Python Dependencies

You can install the required Python packages using pip:

```bash
pip install opencv-python numpy matplotlib
```

---

## 🚀 How to Use

### ▶ R Version

1. Open and edit `script.R` to set correct paths:
    ```r
    json_path <- "your/path/file.json"
    image_path <- "your/path/file.jpg"
    ```

2. Run the script in RStudio or using `Rscript`.

### ▶ Python Version

1. Edit the `visualize_annotations.py` file to set your file paths:
    ```python
    json_path = "/path/to/your/file.json"
    image_path = "/path/to/your/file.jpg"
    ```

2. Run the script:
    ```bash
    python visualize_annotations.py
    ```

---

## 🔁 Alternative Process: Python vs. R

| Feature                 | R Implementation        | Python Implementation     |
|------------------------|-------------------------|----------------------------|
| Library Base           | `ggplot2`, `cowplot`    | `OpenCV`, `matplotlib`    |
| Mask Creation          | `ggplot2 + geom_polygon`| `cv2.fillPoly`            |
| Output Types           | PNG plots               | PNG plots                 |
| Image Reading          | `jpeg`, `png` libraries | `cv2.imread`              |
| Advantage              | Elegant plots, easy UI  | Faster, easier automation |
| Recommended For        | Static visualization    | Scripted batch processing |

---


## 👨‍💻 Author

**Ahmed Imtiaz**

---

