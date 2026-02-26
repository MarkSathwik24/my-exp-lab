import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 1. Set up the transformation matrix (initial values)
def get_matrix(a, b, c, d):
    return np.array([[a, b], [c, d]])

# 2. Setup Figure and Axes
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.25)
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.grid(True)
ax.set_title("Interactive Eigenvalues Visualization")
ax.axhline(0, color='black',linewidth=1)
ax.axvline(0, color='black',linewidth=1)

# Generate a unit circle to visualize transformation
theta = np.linspace(0, 2*np.pi, 100)
circle = np.array([np.cos(theta), np.sin(theta)])

# Plot initial transformed circle and vectors
transformed_circle = ax.plot(circle[0, :], circle[1, :], color='blue', alpha=0.5)[0]
vec1 = ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=1, color='green', label='Eigenvector 1')
vec2 = ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy', scale=1, color='red', label='Eigenvector 2')
ax.legend()

# 3. Define Slider Axes and Initial Values
ax_a = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_b = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_c = plt.axes([0.25, 0.05, 0.65, 0.03])
ax_d = plt.axes([0.25, 0.00, 0.65, 0.03])

s_a = Slider(ax_a, 'a', -2.0, 2.0, valinit=1.0)
s_b = Slider(ax_b, 'b', -2.0, 2.0, valinit=0.0)
s_c = Slider(ax_c, 'c', -2.0, 2.0, valinit=0.0)
s_d = Slider(ax_d, 'd', -2.0, 2.0, valinit=1.0)

# 4. Update Function
def update(val):
    a, b, c, d = s_a.val, s_b.val, s_c.val, s_d.val
    A = get_matrix(a, b, c, d)
    
    # Calculate transformation
    new_circle = A @ circle
    transformed_circle.set_data(new_circle[0, :], new_circle[1, :])
    
    # Calculate Eigenvalues/Vectors
    try:
        eigenvalues, eigenvectors = np.linalg.eig(A)
        # Scale vectors by eigenvalues for visualization
        v1 = eigenvectors[:, 0] * eigenvalues[0]
        v2 = eigenvectors[:, 1] * eigenvalues[1]
        
        # Update vectors
        vec1.set_UVC(v1[0], v1[1])
        vec2.set_UVC(v2[0], v2[1])
        
        ax.set_title(f"Eigenvalues: {eigenvalues[0]:.2f}, {eigenvalues[1]:.2f}")
    except:
        pass
    fig.canvas.draw_idle()

# Register update function with sliders
s_a.on_changed(update)
s_b.on_changed(update)
s_c.on_changed(update)
s_d.on_changed(update)

update(None) # Initial run
plt.show()
