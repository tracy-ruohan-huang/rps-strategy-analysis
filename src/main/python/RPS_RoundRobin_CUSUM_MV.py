import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from tqdm import tqdm

data_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data'))
csv_file_name = 'strategy_simulation_results.csv'
pdf_file_name = 'strategy_cusum_mv_plots.pdf'
tiff_file_name = 'strategy_cusum_mv_plots.tiff'
dpi = 300  # Configurable DPI setting

# Grid layout variables
columns = 4
rows = 3
images_per_page = columns * rows

# Ensure output directory exists
os.makedirs(data_dir, exist_ok=True)

# Paths for input and output
csv_file_path = os.path.join(data_dir, csv_file_name)
pdf_file_path = os.path.join(data_dir, pdf_file_name)
tiff_file_path = os.path.join(data_dir, tiff_file_name)

# Load the data
data = pd.read_csv(csv_file_path)

# Ensure required columns exist
required_columns = ['Rnd', 'S1', 'S2', '%S1W', '%S2W']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"Missing required column: {col}")

# Simplified strategy names
strategy_names = [
    "Random",
    "Constant",
    "Sequential",
    "Mirror",
    "Exclusion",
    "Reaction",
    "ReverseMirror",
    "ProbWeighted",
    "MultiRoundObs"
]

combinations = [(s1, s2) for s1 in strategy_names for s2 in strategy_names]

# Function to compute CUSUM
def compute_cusum(series, target_mean):
    return (series - target_mean).cumsum()

# Plotting function for CUSUM
def plot_cusum(subset, strat1, strat2, ax):
    target_mean_p1 = subset['%S1W'].mean()
    target_mean_p2 = subset['%S2W'].mean()
    cusum_p1 = compute_cusum(subset['%S1W'], target_mean_p1)
    cusum_p2 = compute_cusum(subset['%S2W'], target_mean_p2)

    control_limit_upper_p1 = cusum_p1.mean() + 2 * cusum_p1.std()
    control_limit_lower_p1 = cusum_p1.mean() - 2 * cusum_p1.std()
    control_limit_upper_p2 = cusum_p2.mean() + 2 * cusum_p2.std()
    control_limit_lower_p2 = cusum_p2.mean() - 2 * cusum_p2.std()

    ax.plot(subset['Rnd'], cusum_p1, marker='o', linestyle='-', color='blue', label=f'{strat1} (S1)')
    ax.plot(subset['Rnd'], cusum_p2, marker='x', linestyle='--', color='orange', label=f'{strat2} (S2)')
    ax.axhline(y=control_limit_upper_p1, color='blue', linestyle='--', label='S1 CLU')
    ax.axhline(y=control_limit_lower_p1, color='blue', linestyle='--', label='S1 CLL')
    ax.axhline(y=control_limit_upper_p2, color='orange', linestyle='--', label='S2 CLU')
    ax.axhline(y=control_limit_lower_p2, color='orange', linestyle='--', label='S2 CLL')
    ax.set_title(f'{strat1} vs {strat2}')
    ax.set_xlabel('Rounds')
    ax.set_ylabel('CUSUM')
    ax.legend()
    ax.grid(True)

# Plotting function for Moving Average
def plot_moving_avg(subset, strat1, strat2, ax):
    window_size = 5
    moving_avg_cusum_p1 = pd.Series(compute_cusum(subset['%S1W'], subset['%S1W'].mean())).rolling(window=window_size).mean()
    moving_avg_cusum_p2 = pd.Series(compute_cusum(subset['%S2W'], subset['%S2W'].mean())).rolling(window=window_size).mean()

    ax.plot(subset['Rnd'], moving_avg_cusum_p1, marker='o', linestyle='-', color='blue', label=f'{strat1} MA (S1)')
    ax.plot(subset['Rnd'], moving_avg_cusum_p2, marker='x', linestyle='--', color='orange', label=f'{strat2} MA (S2)')
    ax.set_title(f'Moving Avg of CUSUM: {strat1} vs {strat2}')
    ax.set_xlabel('Rounds')
    ax.set_ylabel('CUSUM')
    ax.legend()
    ax.grid(True)

# Create a PDF to save all plots
with PdfPages(pdf_file_path) as pdf:
    for strat1, strat2 in tqdm(combinations, desc="Generating PDF Plots"):
        subset = data[(data['S1'] == strat1) & (data['S2'] == strat2)]

        if not subset.empty:
            # Create and save plots for PDF
            fig, ax = plt.subplots(figsize=(12, 6))
            plot_cusum(subset, strat1, strat2, ax)
            pdf.savefig(fig)
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(12, 6))
            plot_moving_avg(subset, strat1, strat2, ax)
            pdf.savefig(fig)
            plt.close(fig)

# Save individual PNG files
png_files = []
for strat1, strat2 in tqdm(combinations, desc="Saving PNG Files"):
    subset = data[(data['S1'] == strat1) & (data['S2'] == strat2)]

    if not subset.empty:
        # Save CUSUM plot as PNG
        fig, ax = plt.subplots(figsize=(6, 4))  # Reduced size for PNGs
        plot_cusum(subset, strat1, strat2, ax)
        png_path = os.path.join(data_dir, f"{strat1}_vs_{strat2}_cusum.png")
        fig.savefig(png_path, dpi=dpi)  # Use the DPI variable
        png_files.append(png_path)
        plt.close(fig)

        # Save Moving Average plot as PNG
        fig, ax = plt.subplots(figsize=(6, 4))  # Reduced size for PNGs
        plot_moving_avg(subset, strat1, strat2, ax)
        png_path = os.path.join(data_dir, f"{strat1}_vs_{strat2}_mv.png")
        fig.savefig(png_path, dpi=dpi)  # Use the DPI variable
        png_files.append(png_path)
        plt.close(fig)

# Combine PNG files into a single TIFF file with configurable grid layout
tiff_pages = []
for i in tqdm(range(0, len(png_files), images_per_page), desc="Combining PNGs into TIFF"):
    page_images = [Image.open(png_files[j]) for j in range(i, min(i + images_per_page, len(png_files)))]
    widths, heights = zip(*(img.size for img in page_images))

    max_width = max(widths)
    max_height = max(heights)

    total_width = max_width * columns
    total_height = max_height * rows

    # Create a white background image
    new_img = Image.new('RGB', (total_width, total_height), (255, 255, 255))

    for idx, img in enumerate(page_images):
        x_offset = (idx % columns) * max_width
        y_offset = (idx // columns) * max_height
        new_img.paste(img, (x_offset, y_offset))

    tiff_pages.append(new_img)

tiff_pages[0].save(tiff_file_path, save_all=True, append_images=tiff_pages[1:], compression="tiff_deflate", dpi=(dpi, dpi))
print(f"All plots have been saved to {pdf_file_path} and {tiff_file_path}")

# Delete individual PNG files
for png_file in tqdm(png_files, desc="Cleaning Up PNG Files"):
    os.remove(png_file)
