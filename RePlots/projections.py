import logging
import cartopy


def get_projection():
    # set up plotting projections stuff for maps
    pc = cartopy.crs.PlateCarree()  # to match lon/lat
    proj = cartopy.crs.LambertConformal(central_longitude=-90)  # projection for plot

    return proj
