import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from statsmodels.tsa.stattools import adfuller
import os
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from tqdm import tqdm
import warnings
from scipy.optimize import OptimizeWarning

# Define paths and parameters
data_dir = 'WinRPS/data'
csv_file_name = 'strategy_simulation_results.csv'
pdf_file_name = 'strategy_exponential_decay_plots.pdf'
tiff_file_name = 'strategy_exponential_decay_plots.tiff'
dpi = 150  # Reduced DPI setting for optimization

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
try:
    data = pd.read_csv(csv_file_path)
except FileNotFoundError:
    raise FileNotFoundError(f"The file {csv_file_path} does not exist.")
except Exception as e:
    raise RuntimeError(f"Error loading data: {e}")

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

# Define the exponential decay function
def exponential_decay(t, W0, k):
    return W0 * np.exp(-k * t)

# Function to perform Augmented Dickey-Fuller test
def perform_adfuller(series):
    if series.nunique() <= 1:
        return np.nan, np.nan  # Return NaN for both test statistic and p-value

    result = adfuller(series.dropna())
    return result[0], result[1]  # Returns test statistic and p-value

# Function to fit the exponential decay model with bounds
def fit_exponential_decay(time, win_rate):
    with warnings.catch_warnings():
        warnings.filterwarnings('error', category=OptimizeWarning)
        try:
            p0 = [max(win_rate), 0.1]
            bounds = ([0, 0], [np.inf, np.inf])
            popt, _ = curve_fit(
                exponential_decay, time, win_rate,
                p0=p0,
                bounds=bounds,
                maxfev=10000
            )
            W0, k = popt
            return W0, k
        except (RuntimeError, OptimizeWarning) as e:
            return np.nan, np.nan

# Common function to generate plots
def generate_plots(time, s1_win_rate, s2_win_rate, k_s1, k_s2, s1_p_value, s2_p_value, strat1, strat2, plot_style='dots'):
    fig, axs = plt.subplots(2, 1, figsize=(12, 12), dpi=dpi)
    
    # ADF Plot
    axs[0].bar(['S1', 'S2'], [s1_p_value, s2_p_value], color=['blue', 'orange'])
    axs[0].set_title(f'ADF p-values: {strat1} vs {strat2}', fontsize=14)
    axs[0].set_ylabel('p-value', fontsize=12)
    axs[0].set_ylim(0, 1)
    axs[0].grid(True)
    
    # Exponential Decay Plot
    if plot_style == 'dots':
        axs[1].plot(time, s1_win_rate, 'o', color='blue', label='S1')
        axs[1].plot(time, s2_win_rate, 'o', color='orange', label='S2')
    else:  # 'lines'
        axs[1].plot(time, s1_win_rate, 'o', color='blue', label='S1')
        axs[1].plot(time, exponential_decay(time, *fit_exponential_decay(time, s1_win_rate)), '-', color='darkblue', label=f'S1 Fit: k={k_s1:.2f}')
        axs[1].plot(time, s2_win_rate, 'o', color='orange', label='S2')
        axs[1].plot(time, exponential_decay(time, *fit_exponential_decay(time, s2_win_rate)), '-', color='darkorange', label=f'S2 Fit: k={k_s2:.2f}')
    
    axs[1].set_title(f'Exponential Decay: {strat1} vs {strat2}', fontsize=14)
    axs[1].set_xlabel('Time', fontsize=12)
    axs[1].set_ylabel('Win%', fontsize=12)
    if axs[1].get_lines():  # Only add legend if there are lines to label
        axs[1].legend(fontsize=12)
    axs[1].grid(True)

    plt.tight_layout()
    return fig

# Function to save plots to PDF
def save_plots_to_pdf(figures, pdf_file_path):
    with PdfPages(pdf_file_path) as pdf:
        for fig in tqdm(figures, desc="Saving PDF Plots"):
            pdf.savefig(fig)
            plt.close(fig)  # Close the figure to free up memory

# Function to save plots to TIFF with a grid layout
def save_plots_to_tiff(figures, tiff_file_path):
    num_plots = len(figures)
    num_pages = (num_plots + images_per_page - 1) // images_per_page  # Calculate number of pages

    images = []
    
    for page in tqdm(range(num_pages), desc="Generating TIFF Pages"):
        fig, axs = plt.subplots(rows, columns, figsize=(12, 9), dpi=dpi)  # Create a grid
        axs = axs.flatten()  # Flatten to easily index
        
        start_idx = page * images_per_page
        end_idx = min(start_idx + images_per_page, num_plots)

        for i, plot_idx in enumerate(range(start_idx, end_idx)):
            ax = axs[i]
            sub_fig = figures[plot_idx]

            # Directly copy the subplots to the grid
            sub_fig_axs = sub_fig.axes

            for j, subplot in enumerate(sub_fig_axs):
                for line in subplot.get_lines():
                    ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label(), color=line.get_color())
                ax.set_title(subplot.get_title(), fontsize=10)
                ax.set_xlabel(subplot.get_xlabel(), fontsize=8)
                ax.set_ylabel(subplot.get_ylabel(), fontsize=8)
                if subplot.get_legend() and subplot.get_legend().get_lines():  # Check if there are legends
                    handles, labels = subplot.get_legend_handles_labels()
                    ax.legend(handles, labels, fontsize=8)
                ax.grid(True)
        
        plt.tight_layout()
        png_file_path = f'page_{page + 1}.png'
        plt.savefig(png_file_path, dpi=dpi)
        plt.close(fig)
        
        images.append(Image.open(png_file_path))

    if images:
        images[0].save(tiff_file_path, save_all=True, append_images=images[1:], resolution=dpi, compression='tiff_deflate')

    for png_file in os.listdir(data_dir):
        if png_file.startswith('page_') and png_file.endswith('.png'):
            os.remove(os.path.join(data_dir, png_file))
            print(f"Deleted {png_file}")

# Generate plots and save to PDF and TIFF
figures = []
for strat1, strat2 in tqdm(combinations, desc="Generating Plots"):
    subset = data[(data['S1'] == strat1) & (data['S2'] == strat2)]
    try:
        s1_test_statistic, s1_p_value = perform_adfuller(subset['%S1W'])
        s2_test_statistic, s2_p_value = perform_adfuller(subset['%S2W'])

        time = np.arange(len(subset))
        s1_win_rate = subset['%S1W'].values
        s2_win_rate = subset['%S2W'].values
        W0_s1, k_s1 = fit_exponential_decay(time, s1_win_rate)
        W0_s2, k_s2 = fit_exponential_decay(time, s2_win_rate)

        # Generate PDF plot with dots
        fig = generate_plots(time, s1_win_rate, s2_win_rate, k_s1, k_s2, s1_p_value, s2_p_value, strat1, strat2, plot_style='dots')
        figures.append(fig)
        plt.close(fig)  # Close the figure to free up memory

        # Generate TIFF plot with lines
        fig = generate_plots(time, s1_win_rate, s2_win_rate, k_s1, k_s2, s1_p_value, s2_p_value, strat1, strat2, plot_style='lines')
        figures.append(fig)
        plt.close(fig)  # Close the figure to free up memory

    except ValueError as e:
        print(f"Skipping combination {strat1} vs {strat2} due to error: {e}")

# Save plots to PDF and TIFF
save_plots_to_pdf(figures, pdf_file_path)
save_plots_to_tiff(figures, tiff_file_path)
