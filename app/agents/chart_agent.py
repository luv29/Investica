from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import numpy as np
import random

from pydantic_ai import Agent, RunContext
from typing import List, Dict, Optional, Union, Any

from app.utils import model, CHART_AGENT_SYSTEM_PROMPT
# from model import model
# from prompts import CHART_AGENT_SYSTEM_PROMPT 

load_dotenv()

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class Deps:
    reasoner_output: str

chart_agent = Agent(
    model,
    system_prompt=CHART_AGENT_SYSTEM_PROMPT,
    deps_type=Deps,
    retries=2
)

import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional
import base64
import io

plt.style.use('default')
sns.set_palette("husl")
plt.ioff()

@chart_agent.tool
def create_histogram(
    ctx: RunContext[Deps],
    data: Optional[List[float]] = None, 
    title: Optional[str] = None,
    bins: int = 30,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: str = 'skyblue',
    sample_size: int = 1000
) -> Dict[str, str]:
    """
    Create a histogram for numerical data distribution.
    
    Args:
        ctx: The context
        data: List of numerical values (if None, generates random data)
        title: Chart title (optional)
        bins: Number of bins (default: 30)
        x_label: X-axis label (optional)
        y_label: Y-axis label (optional)
        color: Bar color (default: 'skyblue')
        sample_size: Size of random data if data is None (default: 1000)
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    # Generate random data if none provided
    if data is None:
        np.random.seed(42)  # For reproducible results
        data = np.random.normal(50, 15, sample_size).tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=bins, color=color, alpha=0.7, edgecolor='black')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Distribution Histogram', fontsize=16, fontweight='bold')
    
    ax.set_xlabel(x_label or 'Values', fontsize=12)
    ax.set_ylabel(y_label or 'Frequency', fontsize=12)
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
        "data_points": len(data),
        "title": title or "Distribution Histogram"
    }

@chart_agent.tool
def create_line_chart(
    ctx: RunContext[Deps],
    x_data: Optional[List[Union[float, int]]] = None,
    y_data: Optional[List[Union[float, int]]] = None,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: str = 'blue',
    line_style: str = '-',
    marker: str = 'o',
    sample_size: int = 50
) -> Dict[str, str]:
    """
    Create a line chart.
    
    Args:
        ctx: The context
        x_data: X-axis data (if None, generates sequential numbers)
        y_data: Y-axis data (if None, generates random data)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label  
        color: Line color
        line_style: Line style ('-', '--', '-.', ':')
        marker: Marker style ('o', 's', '^', 'v', etc.)
        sample_size: Size of random data if data is None
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    # Generate data if none provided
    if x_data is None:
        x_data = list(range(sample_size))
    if y_data is None:
        np.random.seed(42)
        y_data = np.cumsum(np.random.randn(len(x_data))).tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_data, y_data, color=color, linestyle=line_style, marker=marker, markersize=4)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Line Chart', fontsize=16, fontweight='bold')
    
    ax.set_xlabel(x_label or 'X Values', fontsize=12)
    ax.set_ylabel(y_label or 'Y Values', fontsize=12)
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
        "data_points": len(x_data),
        "title": title or "Line Chart"
    }

@chart_agent.tool
def create_bar_chart(
    ctx: RunContext[Deps],
    categories: Optional[List[str]] = None,
    values: Optional[List[Union[float, int]]] = None,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: str = 'steelblue',
    horizontal: bool = False
) -> Dict[str, str]:
    """
    Create a bar chart.
    
    Args:
        ctx: The context
        categories: Category labels (if None, generates sample categories)
        values: Values for each category (if None, generates random values)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Bar color
        horizontal: Whether to create horizontal bars
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    # Generate data if none provided
    if categories is None:
        categories = [f'Category {i+1}' for i in range(8)]
    if values is None:
        random.seed(42)
        values = [random.randint(10, 100) for _ in range(len(categories))]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if horizontal:
        ax.barh(categories, values, color=color, alpha=0.7)
        ax.set_xlabel(y_label or 'Values', fontsize=12)
        ax.set_ylabel(x_label or 'Categories', fontsize=12)
    else:
        ax.bar(categories, values, color=color, alpha=0.7)
        ax.set_xlabel(x_label or 'Categories', fontsize=12)
        ax.set_ylabel(y_label or 'Values', fontsize=12)
        plt.xticks(rotation=45, ha='right')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Bar Chart', fontsize=16, fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y' if not horizontal else 'x')
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
        "data_points": len(categories),
        "title": title or "Bar Chart"
    }

@chart_agent.tool
def create_scatter_plot(
    ctx: RunContext[Deps],
    x_data: Optional[List[Union[float, int]]] = None,
    y_data: Optional[List[Union[float, int]]] = None,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: str = 'red',
    size: Union[int, List[int]] = 50,
    alpha: float = 0.6,
    sample_size: int = 100
) -> Dict[str, str]:
    """
    Create a scatter plot.
    
    Args:
        ctx: The context
        x_data: X-axis data (if None, generates random data)
        y_data: Y-axis data (if None, generates random data)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Point color
        size: Point size (int or list of sizes)
        alpha: Point transparency (0-1)
        sample_size: Size of random data if data is None
    
    Returns:
        Dictionary with base64 image data and metadata
    """
    # Generate data if none provided
    if x_data is None:
        np.random.seed(42)
        x_data = np.random.randn(sample_size).tolist()
    if y_data is None:
        np.random.seed(43)
        y_data = (2 * np.array(x_data) + np.random.randn(len(x_data))).tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_data, y_data, c=color, s=size, alpha=alpha)
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold')
    else:
        ax.set_title('Scatter Plot', fontsize=16, fontweight='bold')
    
    ax.set_xlabel(x_label or 'X Values', fontsize=12)
    ax.set_ylabel(y_label or 'Y Values', fontsize=12)
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
        "data_points": len(x_data),
        "title": title or "Scatter Plot"
    }

async def main():
    # Test different chart types
    result1 = await chart_agent.run("hello, what can you do?")
    print(f"{result1.output}")

    print("Creating histogram...")
    result1 = await chart_agent.run("Create a sample histogram chart with random data showing a normal distribution")
    print(f"Histogram result: {result1.output}")
    
    print("\nCreating line chart...")
    result2 = await chart_agent.run("Create a line chart showing a trend over time")
    print(f"Line chart result: {result2.data}")
    
    print("\nCreating bar chart...")
    result3 = await chart_agent.run("Create a bar chart comparing different categories")
    print(f"Bar chart result: {result3.data}")
    
    print("\nCreating scatter plot...")
    result4 = await chart_agent.run("Create a scatter plot showing correlation between two variables")
    print(f"Scatter plot result: {result4.data}")

if __name__ == "__main__":
    asyncio.run(main())