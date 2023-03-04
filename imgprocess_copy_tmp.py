from deepCR import deepCR
from astropy.io import fits
import numpy as np
from glob import glob
import os

pathroot = "/astro/users/zczhuo/zhuo/phast/deepcrtrain/"
pathimgs = pathroot + "files/img4clean/photcorr/"
# os.chdir(pathimgs)

imgfull = glob(pathimgs + "*flc.fits")
print("all_imgs_name:", imgfull)

# import the trained model used for UVIS images
mdl = deepCR(mask="2022-10-26_mymodel8_epoch30.pth", hidden=32)


def imgclean(imgname, mdl):
    print("image_name:", imgname)

    # open the image with all extensions
    imgall = fits.open(imgname, mode="update")

    # process each chip/extension of the image, manually normalize the input for training
    imgorichip1 = imgall[1].data
    imgorichip1mean = imgorichip1.mean()
    imgorichip1std = imgorichip1.std()
    print("imgchip1mean_std:", imgorichip1mean, imgorichip1std)
    imgnormchip1 = (imgorichip1 - imgorichip1mean) / imgorichip1std
    print("chip1_normalize_done")

    imgorichip2 = imgall[4].data
    imgorichip2mean = imgorichip2.mean()
    imgorichip2std = imgorichip2.std()
    print("imgchip2mean_std:", imgorichip2mean, imgorichip2std)
    imgnormchip2 = (imgorichip2 - imgorichip2mean) / imgorichip2std
    print("chip2_normalize_done")

    # for tweakreg purpose, threshold = 0.1 is good, mis-recognition of real sources as cr is allowed in the step
    maskimgchip1, cleaned_imgchip1 = mdl.clean(
        imgnormchip1, threshold=0.10, inpaint="medmask"
    )
    cleaned_imgchip1ori = (
        cleaned_imgchip1 * imgorichip1std + imgorichip1mean
    )  # reverse process the image to get original absolute flux
    cleaned_imgchip1ori = np.float32(
        cleaned_imgchip1ori
    )  # important! otherwise not accepted by tweakreg
    maskimgchip1 = np.float32(maskimgchip1)
    print("chip1_clean_done_scaleback")

    maskimgchip2, cleaned_imgchip2 = mdl.clean(
        imgnormchip2, threshold=0.10, inpaint="medmask"
    )
    cleaned_imgchip2ori = cleaned_imgchip2 * imgorichip2std + imgorichip2mean
    cleaned_imgchip2ori = np.float32(cleaned_imgchip2ori)
    maskimgchip2 = np.float32(maskimgchip2)
    print("chip2_clean_done_scaleback")

    imgall[1].data = cleaned_imgchip1ori
    imgall[4].data = cleaned_imgchip2ori
    imgall.flush()
    print("update original fits file done")
    ## attention, backup original files beforehand, this step will change the values of the original images
    ## not good for scientific purpose
    return


for ii in imgfull:
    imgclean(ii, mdl)


# save binary mask for additional tests
# maskchip1name = pathroot + 'files/img4clean/visit11_notweak/' + imgnamestr + 'chip1crmask.npy'
# maskchip1name = pathroot + 'files/imgoriall/' + imgnamestr + 'chip1crmask.npy'
# with open(maskchip1name, 'wb') as f:
#    np.save(f, maskimgchip1)

# maskchip2name = pathroot + 'files/imgoriall/' + imgnamestr + 'chip2crmask.npy'
# with open(maskchip2name, 'wb') as f:
#    np.save(f, maskimgchip2)
# print('save binary mask done')

# save cleaned img array only for additional tests, no other fits info
# chip1name = pathroot + 'files/imgoriall/' + imgnamestr + 'chip1inpaint.npy'
# with open(chip1name, 'wb') as f:
#    np.save(f, cleaned_imgchip1ori)

# chip2name = pathroot + 'files/imgoriall/' + imgnamestr + 'chip2inpaint.npy'
# with open(chip2name, 'wb') as f:
#    np.save(f, cleaned_imgchip2ori)
