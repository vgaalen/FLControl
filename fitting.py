import numpy as np
from scipy.optimize import curve_fit

def _eval_gaussian(x, x_0, y_0, A, sigma_x, sigma_y, theta):
    from astropy.modeling.functional_models import Gaussian2D
    return Gaussian2D.evaluate(x[0], x[1], x_0, y_0, A, sigma_x, sigma_y, theta).flatten()


def gaussian(img: np.ndarray, p0=None):
    if len(img.shape) == 3:
        img = np.median(img, axis=0)

    if p0 is None:
        p0 = [img.shape[1]/2,img.shape[0]/2,np.max(img),10,10,0]

    x, y = np.ogrid[:img.shape[0], :img.shape[1]]
    xx, yy = np.meshgrid(x, y)

    popt, pcov = curve_fit(_eval_gaussian, np.array([xx, yy]), img.flatten(), p0=p0)
    print(popt)
    return popt[:2]
