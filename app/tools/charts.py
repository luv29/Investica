import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json
import base64
import io
from datetime import datetime

plt.style.use('default')
sns.set_palette("husl")

plt.ioff()

def create_histogram(data: List[float], 
                    title: Optional[str] = None,
                    bins: int = 30) -> Dict[str, str]:
    """
    Create a histogram for numerical data distribution.
    
    Args:
        data: List of numerical values
        title: Chart title (optional)
        bins: Number of bins (default: 30)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=bins, color='skyblue', alpha=0.7, edgecolor='black')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Distribution Histogram', fontsize=16, fontweight='bold')
    
    ax.set_xlabel('Values', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png",
        "chart_type": "histogram",
        "data_points": len(data)
    }

def create_bar_chart(categories: List[str], 
                    values: List[float],
                    title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a bar chart for categorical data comparison.
    
    Args:
        categories: List of category names
        values: List of corresponding values
        title: Chart title (optional)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(categories, values, color='steelblue', alpha=0.8)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Bar Chart Comparison', fontsize=16, fontweight='bold')
    
    ax.set_xlabel('Categories', fontsize=12)
    ax.set_ylabel('Values', fontsize=12)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png", 
        "chart_type": "bar_chart",
        "categories": len(categories)
    }

def create_pie_chart(labels: List[str], 
                    sizes: List[float],
                    title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a pie chart for proportional data.
    
    Args:
        labels: List of category labels
        sizes: List of corresponding values/sizes
        title: Chart title (optional)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Proportional Distribution', fontsize=16, fontweight='bold')
    
    ax.axis('equal')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png",
        "chart_type": "pie_chart", 
        "segments": len(labels)
    }

def create_line_chart(x_values: List, 
                     y_values: List,
                     title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a line chart for trend analysis.
    
    Args:
        x_values: X-axis data points
        y_values: Y-axis data points  
        title: Chart title (optional)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_values, y_values, color='blue', marker='o', linewidth=2, markersize=6)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Trend Analysis', fontsize=16, fontweight='bold')
    
    ax.set_xlabel('X Values', fontsize=12)
    ax.set_ylabel('Y Values', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png",
        "chart_type": "line_chart",
        "data_points": len(x_values)
    }

def create_scatter_plot(x_values: List[float], 
                       y_values: List[float],
                       title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a scatter plot for correlation analysis.
    
    Args:
        x_values: X-axis data points
        y_values: Y-axis data points
        title: Chart title (optional)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_values, y_values, color='red', s=50, alpha=0.6)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Correlation Analysis', fontsize=16, fontweight='bold')
    
    ax.set_xlabel('X Values', fontsize=12)
    ax.set_ylabel('Y Values', fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png",
        "chart_type": "scatter_plot",
        "data_points": len(x_values)
    }

def create_box_plot(data_dict: Dict[str, List[float]],
                   title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a box plot for statistical distribution analysis.
    
    Args:
        data_dict: Dictionary with category names as keys and data lists as values
        title: Chart title (optional)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data_dict.values(), labels=data_dict.keys())
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Statistical Distribution', fontsize=16, fontweight='bold')
    
    ax.set_xlabel('Categories', fontsize=12)
    ax.set_ylabel('Values', fontsize=12)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    
    return {
        "image": image_base64,
        "mime_type": "image/png",
        "chart_type": "box_plot",
        "categories": len(data_dict)
    }