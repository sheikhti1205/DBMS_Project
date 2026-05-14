# Install required packages (if not already installed)
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("png")) install.packages("png")
if (!require("grid")) install.packages("grid")
if (!require("jpeg")) install.packages("jpeg")
if (!require("cowplot")) install.packages("cowplot")  # For arranging multiple plots

# Load required libraries
library(ggplot2)
library(jsonlite)
library(png)
library(grid)
library(jpeg)
library(cowplot)

# Set paths to your files
json_path <- "2019Mirpur (25).json"
image_path <- "2019Mirpur (25).jpg"

# Read the JSON file
json_data <- fromJSON(json_path, flatten = TRUE)

# Extract image filename and regions data
image_file <- names(json_data)[1]
regions <- json_data[[1]]$regions

# Create a data frame for all polygons
polygons_df <- data.frame()
for (i in seq_along(regions)) {
  region <- regions[[i]]
  if (!is.null(region$shape_attributes$name) && region$shape_attributes$name == "polygon") {
    df <- data.frame(
      x = region$shape_attributes$all_points_x,
      y = region$shape_attributes$all_points_y,
      group = i,
      label = region$region_attributes$label
    )
    polygons_df <- rbind(polygons_df, df)
  }
}

# Read the image file
img <- readJPEG(image_path)

# 1. Create the original annotated image
p_original <- ggplot(polygons_df, aes(x = x, y = y, group = group, fill = label)) +
  annotation_custom(
    rasterGrob(img, width = unit(1, "npc"), height = unit(1, "npc")),
    xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf
  ) +
  geom_polygon(alpha = 0.3, color = "red", size = 0.7) +
  scale_y_reverse() +
  theme_minimal() +
  labs(title = "Original Image with Annotations",
       subtitle = paste(length(unique(polygons_df$group)), "annotated regions")) +
  coord_equal()

# 2. Create the black-and-white mask image
p_mask <- ggplot(polygons_df, aes(x = x, y = y, group = group)) +
  # Black background
  theme_void() +
  theme(panel.background = element_rect(fill = "black")) +
  # White polygons
  geom_polygon(fill = "white", color = "white", size = 0.5) +
  scale_y_reverse() +
  labs(title = "Binary Mask of Annotations",
       subtitle = "White regions show annotated areas") +
  coord_equal()

# Combine both plots into one figure
print(p_original)

# 2. Display the binary mask image plot
print(p_mask)

# Save the plots separately (already done below, kept for completeness)
ggsave("original_annotated.png", plot = p_original, width = 8, height = 6, dpi = 300)
ggsave("binary_mask.png", plot = p_mask, width = 8, height = 6, dpi = 300)


