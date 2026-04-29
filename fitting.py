import numpy as np
from scipy.optimize import curve_fit
from astropy.modeling.functional_models import Gaussian2D
from astropy.convolution import convolve, convolve_fft, Gaussian2DKernel
from astropy.modeling import fitting

def _eval_gaussian(x, x_0, y_0, A, sigma_x, sigma_y, theta):
    return Gaussian2D.evaluate(x[0], x[1], A, x_0, y_0, sigma_x, sigma_y, theta).flatten()

def _gaussian_filter(img, sigma=250):
    kernel = Gaussian2DKernel(sigma)
    return convolve_fft(img, kernel)

def _fourier_filtering(img, radius=-1):
    import matplotlib.pyplot as plt
    from scipy.fft import fft2, ifft2, fftshift, ifftshift
    img_fft = fftshift(fft2(img))

    x, y = np.ogrid[:img.shape[1], :img.shape[0]]
    xx, yy = np.meshgrid(x, y)
    circle_mask = np.zeros(xx.shape)
    r2 = radius**2
    circle_mask[(xx-0.5*img.shape[1])**2+(yy-0.5*img.shape[0])**2<r2] = 1

    img_fft = img_fft * circle_mask 
    
    return np.real(ifft2(ifftshift(img_fft))).astype(np.float64)
    #return img_fft

def gaussian(img: np.ndarray, nulling_limit=0.75, img_radius=100):
    if len(img.shape) == 3:
        img = np.median(img, axis=0)

    peak = np.unravel_index(np.argmax(img.flatten()), img.shape)
    #if img.size>10000:
    cropped=True
    img = img[peak[0]-img_radius:peak[0]+img_radius, peak[1]-img_radius:peak[1]+img_radius]
    #else:
    #cropped=False

    ymax, xmax = np.unravel_index(np.argmax(img.flatten()), img.shape)
    
    #img = _gaussian_filter(img)
    #_fourier_filtering(img)

    # x, y = np.ogrid[:img.shape[0], :img.shape[1]]
    # xx, yy = np.meshgrid(x, y)

    y, x = np.mgrid[:np.shape(img)[0], :np.shape(img)[1]]

    col = img[:, xmax]
    rig = img[ymax, :]
    x_stddev = (np.abs((np.arange(np.shape(img)[0])-ymax)**2*col).sum() / col.sum()) **0.5
    y_stddev = (np.abs((np.arange(np.shape(img)[1])-xmax)**2*rig).sum() / rig.sum()) **0.5
    print(x_stddev, y_stddev)
    model = Gaussian2D(amplitude=np.max(img), x_mean=xmax, y_mean=ymax, x_stddev=150, y_stddev=150,
                        bounds={'amplitude': (0, None), 
                                #'x_mean': (xmax-5, xmax+5), 'y_mean': (ymax-5, ymax+5), 
                                'x_stddev': (1,None), 'y_stddev': (1,None)})
    fit = fitting.SimplexLSQFitter()
    #fit = fitting.LevMarLSQFitter()
    #fit = fitting.TRFLSQFitter()
    #fit = fitting.DogBoxLSQFitter()
    out = fit(model, x, y, img, maxiter=1000)

    print(f"resul: {out.x_mean}, {out.y_mean}, {out.amplitude}, {out.x_stddev}, {out.y_stddev}")
    if cropped:
        return out.y_mean.value+peak[0]-img_radius, out.x_mean.value+peak[1]-img_radius
    else:
        return out.y_mean.value, out.x_mean.value
    
def gaussian_old(img: np.ndarray, p0=None, nulling_limit=0.75):
    if len(img.shape) == 3:
        img = np.median(img, axis=0)

    peak = np.unravel_index(np.argmax(img.flatten()), img.shape)
    if img.size>10000:
        cropped=True
        img = img[peak[0]-50:peak[0]+50,peak[1]-50:peak[1]+50]
    else:
        cropped=False
    
    #img = _gaussian_filter(img)
    #_fourier_filtering(img)

    if p0 is None:
        p0 = [peak[1], peak[0],np.max(img),100,100,0]
        print(p0)
        bounds=([p0[0]-100,p0[1]-100,0.5*p0[2],0,0,-1*np.inf],
                [p0[0]+100,p0[1]+100,np.inf,np.inf,np.inf,np.inf])
        print(bounds)

    x, y = np.ogrid[:img.shape[0], :img.shape[1]]
    xx, yy = np.meshgrid(x, y)

    # Todo change for minimize and use simplex algorithm instead.
    popt, pcov = curve_fit(_eval_gaussian, np.array([xx, yy]), img.flatten(), p0=p0, bounds=bounds)
    print(f"resul: {popt}")
    if cropped:
        return popt[0]+peak[1]-50, popt[1]+peak[0]-50
    else:
        return popt[0], popt[1]

def com(img):
    from scipy.ndimage import center_of_mass
    return center_of_mass(img)
