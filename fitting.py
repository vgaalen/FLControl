import numpy as np
from scipy.optimize import curve_fit
from astropy.modeling.functional_models import Gaussian2D

def _eval_gaussian(x, x_0, y_0, A, sigma_x, sigma_y, theta):
    return Gaussian2D.evaluate(x[0], x[1], A, x_0, y_0, sigma_x, sigma_y, theta).flatten()


def gaussian(img: np.ndarray, p0=None):
    if len(img.shape) == 3:
        img = np.median(img, axis=0)

    if p0 is None:
        peak = np.unravel_index(np.argmax(img.flatten()), img.shape)
        p0 = [peak[1], peak[0],np.max(img),10,10,0]

    x, y = np.ogrid[:img.shape[0], :img.shape[1]]
    xx, yy = np.meshgrid(x, y)

    popt, pcov = curve_fit(_eval_gaussian, np.array([xx, yy]), img.flatten(), p0=p0)
    return popt[1], popt[0]
