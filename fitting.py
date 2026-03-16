import numpy as np
from scipy.optimize import curve_fit
from astropy.modeling.functional_models import Gaussian2D
from astropy.convolution import convolve, convolve_fft, Gaussian2DKernel

def _eval_gaussian(x, x_0, y_0, A, sigma_x, sigma_y, theta):
    return Gaussian2D.evaluate(x[0], x[1], A, x_0, y_0, sigma_x, sigma_y, theta).flatten()

def _gaussian_filter(img, sigma=100):
    kernel = Gaussian2DKernel(sigma)
    return convolve_fft(img, kernel)

def gaussian(img: np.ndarray, p0=None):
    if len(img.shape) == 3:
        img = np.median(img, axis=0)

    img = _gaussian_filter(img)

    if p0 is None:
        peak = np.unravel_index(np.argmax(img.flatten()), img.shape)
        p0 = [peak[1], peak[0],np.max(img),100,100,0]
        print(p0)
        bounds=([p0[0]-100,p0[1]-100,0.5*p0[2],0,0,-1*np.inf],
                [p0[0]+100,p0[1]+100,np.inf,np.inf,np.inf,np.inf])
        print(bounds)

    x, y = np.ogrid[:img.shape[0], :img.shape[1]]
    xx, yy = np.meshgrid(x, y)

    popt, pcov = curve_fit(_eval_gaussian, np.array([xx, yy]), img.flatten(), p0=p0, bounds=bounds)
    print(f"resul: {popt}")
    return popt[0], popt[1]

def com(img):
    from scipy.ndimage import center_of_mass
    return center_of_mass(img)
