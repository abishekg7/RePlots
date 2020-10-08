import matplotlib.pyplot as plt
import cartopy


def setup_map(ax=None, proj=None, land=True, coast=True, 
              rivers=False, states=False, 
              top_labels=False, bottom_labels=True, left_labels=True, right_labels=False,
              infer_intervals=True, robust=True, levels=None, title=None,
              transform=None):
    '''Plot var on lon/lat map with projection.
        
    Inputs
    ------
    ax: matplotlib Axes instance, optional
        Previously-created Axes in which to set up the map. If not provided, a single 
        Axes instance will be created with proj as the projection.
    proj: cartopy projection, optional
        Projection for plot. See cartopy documentation for options. Example:
        >>> proj = cartopy.crs.LambertConformal()
    land: bool, optional
        Plot land.
    coast: bool, optional
        Plot coastline.
    rivers: bool, optional
        Plot rivers.
    states: bool, optional
        Plot political borders.
    top_labels: bool, optional
        Plot longitude labels at the top of the Axes.
    bottom_labels: bool, optional
        Plot longitude labels at the bottom of the Axes.
    left_labels: bool, optional
        Plot latitude labels at the left of the Axes.
    right_labels: bool, optional
        Plot latitude labels at the right of the Axes.
    infer_intervals: bool, optional
        For pcolormesh-style plot. Infer the locations of cell edges from input locations 
        of cell centers. See xarray documentation for more information.
    robust: bool, optional
        Use 2% to 98% values to choose range for colorbar. See xarray documentation 
        for more information.
    levels: int, sequence, optional
        For contourf-style plot, with discrete colorbar. Input int of number of levels 
        to plot within range or input sequence of values that control boundaries of 
        levels. See xarray documentation for more information.
    title: str, optional
        Title to add to Axes. If title is given, xarray will not automatically add labels 
        to Axes or title (`add_labels=False`)
    transform: cartopy projection, optional
        Projection to match projection of plot variable x and y coordinates. By default this 
        is PlateCarree and does not need to be input. See cartopy documentation for options. 
        Example:
        >>> transform = cartopy.crs.PlateCarree()
    '''
    
    if ax is None:
        assert proj is not None, 'If ax is input, proj also needs to be input.'
    
    if proj is not None:
        assert isinstance(proj,cartopy.crs.Projection), 'input "proj" must be a `cartopy` projection.'
        
    if transform is not None:
        assert isinstance(proj,cartopy.crs.Projection), 'input "transform" must be a `cartopy` projection.'
    
    # store arguments for use after this function is called
    pargs = {}  # arguments to go into subsequent plot call
    oargs = {}  # other arguments that might be useful
    
    if ax is None:
        fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj))

    # Add natural features
    if land:
        ax.add_feature(cartopy.feature.LAND.with_scale('110m'), facecolor='0.8')
    if coast:
        ax.add_feature(cartopy.feature.COASTLINE.with_scale('10m'), edgecolor='0.2')
    if rivers:
        ax.add_feature(cartopy.feature.RIVERS.with_scale('110m'), edgecolor='b')
    if states:
        ax.add_feature(cartopy.feature.STATES.with_scale('110m'), edgecolor='k')
        
    if title is not None:
        ax.set_title(title)
        pargs['add_labels'] = False  # don't override axis and colorbar labeling in call to plot
        
    pargs['ax'] = ax

    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False)#, xlocs=np.arange(-104,-80,2))

    # manipulate `gridliner` object to change locations of labels
    gl.top_labels = top_labels
    gl.right_labels = right_labels
    gl.bottom_labels = bottom_labels
    gl.left_labels = left_labels
    oargs['gl'] = gl
        
    pargs['infer_intervals'] = infer_intervals
    pargs['robust'] = robust
    
    if levels is not None:
        pargs['levels'] = levels
    
    if transform is None:
        transform=cartopy.crs.PlateCarree()
    pargs['transform'] = transform  # map projection that plot data is in. Assumed lon/lat or PlateCarree.

    return pargs, oargs


def setup_cbar(fraction=0.046, pad=0.04, label=None, ax=None):
    """
    ax: matplotlib Axes instance, list or array of matplotlib Axes instances
    """
    cbar_kwargs = {'fraction': fraction, 'pad': pad}
    if label is not None:
        cbar_kwargs['label'] = label
    if ax is not None:
        cbar_kwargs['ax'] = ax
    return cbar_kwargs