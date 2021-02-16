import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import cartopy
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import pandas as pd


def setup_map(ax=None, proj=None, land=True, coast=True, 
              rivers=False, states=False, glargs={},
              top_labels=False, bottom_labels=True, left_labels=True, right_labels=False,
              xticklabelargs={}, yticklabelargs={},
              infer_intervals=True, robust=True, levels=None, title=None, titlesize=None,
              transform=None, extent=None, xticks=None, yticks=None, 
              xticklabels=True, yticklabels=True, ticklabelsize=None,
              subargs=None, add_colorbar=False):
    '''Setup plot on lon/lat map with projection.
        
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
    glargs: dict, optional
        Keyword arguments to override and go into cartopy gridliner. More options and
        information: 
        https://scitools.org.uk/cartopy/docs/latest/matplotlib/gridliner.html
    top_labels: bool, optional
        Plot longitude labels at the top of the Axes.
    bottom_labels: bool, optional
        Plot longitude labels at the bottom of the Axes.
    left_labels: bool, optional
        Plot latitude labels at the left of the Axes.
    right_labels: bool, optional
        Plot latitude labels at the right of the Axes.
    xticklabelargs: dict, optional
        Keyword arguments to control text style of xticklabels. More information:
        https://scitools.org.uk/cartopy/docs/latest/matplotlib/gridliner.html
    yticklabelargs: dict, optional
        Keyword arguments to control text style of yticklabels. More information:
        https://scitools.org.uk/cartopy/docs/latest/matplotlib/gridliner.html
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
    titlesize: int, string, optional
        Size of title in points (e.g., 12) or descriptive size (e.g.,
        "small", "large").
    transform: cartopy projection, optional
        Projection to match projection of plot variable x and y coordinates. By default this 
        is PlateCarree and does not need to be input. See cartopy documentation for options. 
        Example:
        >>> transform = cartopy.crs.PlateCarree()
    extent: list
        Extent of plot view [left longitude, right longitude, bottom latitude, top latitude]
    xticks: sequence
        Longitudes to label with x ticks.
    yticks: sequence
        Latitudes to label with y ticks.
    xticklabels: bool, optional
        If False, do not plot x tick labels.
    yticklabels: bool, optional
        If False, do not plot y tick labels.
    ticklabelsize: int, string, optional
        Size for all x and y major and minor tick labels in points (e.g., 12) or descriptive size (e.g.,
        "small", "large"). 
    subargs: dict, optional
        Options to pass to `subplot_label`.
    add_colorbar: bool, optional, default: False
        Use xarray plotting call to add colorbar. False by default to then add own 
        colorbar since more options then. Use `cbar` function in this package for 
        convenience wrapper.
        
    Returns
    -------
    pargs, a dictionary of plotting options to send to xarray-wrapped plot calls, and 
    oargs, a dictionary of plotting items that might be useful but do not go into 
    plot calls.
    
    Example usage
    -------------
    Plot 2D DataArray `var` on a map:
    >>> pargs, oargs = replots.setup_map(proj=cartopy.crs.LambertConformal())
    >>> var.plot(**pargs, add_colorbar=False)  # can include other keyword arguments too
    '''
    
    if ax is None:
        assert proj is not None, 'If ax is input, proj also needs to be input.'
    
    if proj is not None:
        assert isinstance(proj,cartopy.crs.Projection), 'input "proj" must be a `cartopy` projection.'
        
    if transform is not None:
        assert isinstance(transform,cartopy.crs.Projection), 'input "transform" must be a `cartopy` projection.'
    
    # store arguments for use after this function is called
    pargs = {}  # arguments to go into subsequent plot call
    oargs = {}  # other arguments that might be useful
    
    if ax is None:
        fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=proj))
        oargs['fig'] = fig


    # Add natural features
    if land:
        ax.add_feature(cartopy.feature.LAND.with_scale('10m'), facecolor='0.8')
    if coast:
        ax.add_feature(cartopy.feature.COASTLINE.with_scale('10m'), edgecolor='0.2')
    if rivers:
        ax.add_feature(cartopy.feature.RIVERS.with_scale('10m'), edgecolor='b')
    if states:
        ax.add_feature(cartopy.feature.STATES.with_scale('10m'), edgecolor='k')
    
    if subargs is not None:
        assert 'label' in subargs, 'need "label" in subargs'
        ax = subplot_label(ax, subargs.pop('label'), **subargs)
        
    if title is not None:
        ax.set_title(title, fontsize=titlesize)
        pargs['add_labels'] = False  # don't override axis and colorbar labeling in call to plot
    
    if extent is not None:
        ax.set_extent(extent)

    glargs_in = {'draw_labels': True, 'x_inline': False, 'y_inline': False}
    glargs_in.update(glargs)
    gl = ax.gridlines(**glargs_in)
        
    xticklabelargs.update({'size': ticklabelsize})
    gl.xlabel_style = xticklabelargs
    yticklabelargs.update({'size': ticklabelsize})
    gl.ylabel_style = yticklabelargs

    # manipulate `gridliner` object to change locations of labels
    gl.top_labels = top_labels
    gl.right_labels = right_labels
    gl.bottom_labels = bottom_labels
    gl.left_labels = left_labels
    
    if xticks is not None:
        gl.xlocator = mticker.FixedLocator(xticks)
    if yticks is not None:
        gl.ylocator = mticker.FixedLocator(yticks)
        
    oargs['gl'] = gl
    
    
    if not xticklabels:
        ax.xaxis.set_ticklabels('')
    if not yticklabels:
        ax.yaxis.set_ticklabels('')

    pargs['x'] = 'longitude'
    pargs['y'] = 'latitude'
        
    pargs['infer_intervals'] = infer_intervals
    pargs['robust'] = robust
    
    if levels is not None:
        pargs['levels'] = levels
    
    if transform is None:
        transform=cartopy.crs.PlateCarree()
    pargs['transform'] = transform  # map projection that plot data is in. Assumed lon/lat or PlateCarree.
        
    pargs['ax'] = ax
    
    pargs['add_colorbar'] = add_colorbar

    return pargs, oargs


def setup_hov(var, ax=None, xaxis='time', yaxis='lat', title=None, titlesize=None, 
              ticklabelsize=None, subargs=None, xticklabels=True, yticklabels=True,
              add_colorbar=False):
    """Setup Hovmoller plot with options for lat/lon and time.
    
    Inputs
    ------
    var: DataArray, ndarray
        Variable to operate on.
    ax: matplotlib Axes instance, optional
        Previously-created Axes in which to set up the map. If not provided, a single 
        Axes instance will be created.
    xaxis: str, optional
        Option to treat xaxis as a particular type of axis for labeling: "lon", "lat", 
        or "time".
    yaxis: str, optional
        Option to treat yaxis as a particular type of axis for labeling: "lon", "lat", 
        or "time".
    title: str, optional
        Title to add to Axes. If title is given, xarray will not automatically add labels 
        to Axes or title (`add_labels=False`)
    titlesize: int, string, optional
        Size of label on colorbar in points (e.g., 12) or descriptive size (e.g.,
        "small", "large").
    ticklabelsize: int, optional
        Set fontsize for all x and y major and minor tick labels.
    subargs: dict, optional
        Options to pass to `subplot_label`. Example: 
        `subargs={'label': 'd', 'loc': 'bottom left'}`
    xticklabels: bool, optional
        If False, do not plot x tick labels.
    yticklabels: bool, optional
        If False, do not plot y tick labels.
    add_colorbar: bool, optional, default: False
        Use xarray plotting call to add colorbar. False by default to then add own 
        colorbar since more options then. Use `cbar` function in this package for 
        convenience wrapper.
    
    Returns
    -------
    pargs, a dictionary of plotting options to send to xarray-wrapped plot calls.
    
    Example usage
    -------------
    Plot 2D DataArray `var` as a Hovmoller plot of latitude vs. time:
    >>> pargs = replots.setup_hov(var)
    >>> var.plot(**pargs, add_colorbar=False)  # can include other keyword arguments too
    """
    
    pargs = {}
    oargs = {}
    
    if ax is None:
        fig, ax = plt.subplots(1, 1)
        oargs['fig'] = fig

    var = var.cf.guess_coord_axis()
    
    ## Latitude and longitude ##
    # https://scitools.org.uk/cartopy/docs/v0.15/examples/tick_labels.html
    if yaxis == 'lat':    
        formatter = LatitudeFormatter()#number_format='.0f')
        ax.yaxis.set_major_formatter(formatter)
        ykey = 'latitude'
    if xaxis == 'lat':
        formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(formatter)        
        xkey = 'latitude'
    if yaxis == 'lon':
        formatter = LongitudeFormatter()
        ax.yaxis.set_major_formatter(formatter)
        ykey = 'longitude'
    if xaxis == 'lon':
        formatter = LongitudeFormatter()
        ax.xaxis.set_major_formatter(formatter)
        xkey = 'longitude'

        
    ## Time ##
    if xaxis == 'time':
        
        xkey = 'time'

        if 'dayofyear' in var.dims:
            # convert from dayofyear back to dates for labeling
            # the year choice isn't important here but needs a placeholder
            dates = [pd.Timestamp(1970, 1, 1) + pd.Timedelta(str(day - 1) + ' days') for day in var.dayofyear.values]  
            var['dayofyear'] = dates
            
            plt.xticks(rotation=0)  # ticks better without rotation
            
            # https://stackoverflow.com/questions/9581837/setting-dates-as-first-letter-on-x-axis-using-matplotlib
            month_fmt = mdates.DateFormatter('%b')
            def m_fmt(x, pos=None):
                return month_fmt(x)[0]

            # edge gets major ticks but no label
            months_edge = mdates.MonthLocator(bymonthday=1)  
            ax.xaxis.set_major_locator(months_edge)
            ax.xaxis.set_ticklabels('')
            
            # mid gets label but no tick
            months_mid = mdates.MonthLocator(bymonthday=17)
            ax.tick_params(which='minor', length=0)
            ax.xaxis.set_minor_formatter(m_fmt)
            ax.xaxis.set_minor_locator(months_mid)
            
    pargs['x'] = xkey
    pargs['y'] = ykey
    
    if not xticklabels:
        ax.xaxis.set_ticklabels('')
    if not yticklabels:
        ax.yaxis.set_ticklabels('')
    
    if ticklabelsize is not None:
        ax.tick_params(axis='both', which='both', labelsize=ticklabelsize)
    
    if subargs is not None:
        assert 'label' in subargs, 'need "label" in subargs'
        ax = subplot_label(ax, subargs.pop('label'), **subargs)

    if title is not None:
        ax.set_title(title, fontsize=titlesize)
        pargs['add_labels'] = False  # don't override axis and colorbar labeling in call to plot
        
    pargs['ax'] = ax
    
    pargs['add_colorbar'] = add_colorbar

    return pargs, oargs


def setup_cbar(fraction=0.046, pad=0.04, kwargs={}):#label=None, ax=None, fs=None):
    """Set up colorbar sizing with some convenient default choices.
    
    Inputs
    ------
    fraction: float, optional, default: 0.046
        Fraction of original axes to use for colorbar. See `plt.colorbar` docs for
        more information.
    pad: float, optional, default: 0.04
        Fraction of original axes between colorbar and new image axes. See
        `plt.colorbar` docs for more information.
    kwargs: dictionary, optional
        Other keyword arguments to pass through to `plt.colorbar`.
        
    Returns
    -------
    
    Example usage
    -------------
    >>> replots.setup_cbar(kwargs={'ax': [ax4,ax5], 'label': 'Celsius'})
    """
    cbar_kwargs = {'fraction': fraction, 'pad': pad}
        
    # prioritize input arguments over defaults.
    cbar_kwargs = {**cbar_kwargs, **kwargs}

    return cbar_kwargs


def subplot_label(ax, label, loc='bottom left', props=None, fs=14):
    """
    
    loc: str
        Where to put the label. Options: 'upper left', 'upper right',
        'bottom left', 'bottom right'.
    label: str
        Label to use for subplot, e.g., 'A'.
    props: dict, optional
        matplotlib.patch.Patch properties to change box. If None, 
        use defaults: 
        `dict(boxstyle='round', facecolor='w', alpha=0.75)`
    fs: int, optional
        Fontsize for label.
    
    """

    if props is None:
        props = dict(boxstyle='round', facecolor='w', alpha=0.75)

    if loc == 'upper left':
        ax.text(0.05, 0.92, label, transform=ax.transAxes, fontsize=fs,
                 verticalalignment='top', bbox=props)
    elif loc == 'upper right':
        ax.text(0.92, 0.92, label, transform=ax.transAxes, fontsize=fs,
                 verticalalignment='top', bbox=props)
    elif loc == 'bottom left':
        ax.text(0.05, 0.12, label, transform=ax.transAxes, fontsize=fs,
                 verticalalignment='top', bbox=props)
    elif loc == 'bottom right':
        ax.text(0.92, 0.12, label, transform=ax.transAxes, fontsize=fs,
                 verticalalignment='top', bbox=props)
        
    return ax


def cbar(mappable, ax=None, cax=None, orientation='vertical', 
         fraction=0.046, pad=0.04, shrink=1, extend='neither', cbargs={}, 
         label=None, labelsize=None, labelweight=None, labelargs={}, 
         ticksize=None, tickargs={}):
    """Make a custom colorbar.
    
    Inputs
    ------
    mappable: matplotlib Mappable instance output from plot
        Mappable of plot with which to associate colorbar.
    ax: matplotlib Axes instance or array of instances
        One or more Axes from which to take space for the colorbar.
    cax: matplotlib Axes instance
        Axes into which the colorbar will be drawn.
    orientation: string, optional, default: 'vertical'
        Whether to plot colorbar "vertical": up and down to the righthand
        side of the Axes or "horizontal": left to right below the plot.
    fraction: float, default: 0.046
        Fraction of original axes to use for colorbar.
    pad: float, default: 0.04
        Fraction of original axes between colorbar and new image axes.
    shrink: float, default: 1.0
        Fraction by which to multiply the size of the colorbar.
    extend: {'neither', 'both', 'min', 'max'}
        If not 'neither', make pointed end(s) for out-of-
        range values.  These are set for a given colormap
        using the colormap set_under and set_over methods.
    cbargs: dict, optional
        Additional keyword arguments to pass to `colorbar`. More information in 
        matplotlib docs at `plt.colorbar` for above and other input options.
    label: str, optional
        Label for colorbar
    labelsize: int, string, optional
        Size of label on colorbar in points (e.g., 12) or descriptive size (e.g.,
        "small", "large").
    labelweight: string, optional
        Weight of font for colorbar label, e.g., "bold".
    labelargs: dict, optional
        Additional keyword arguments to pass to `cb.set_label`. Other text options:
        https://matplotlib.org/3.1.1/tutorials/text/text_props.html
    ticksize: int, string, optional
        Size of tick labels on colorbar in points (e.g., 12) or descriptive size (e.g.,
        "small", "large").
    tickargs: dict, optional
        Additional keyword arguments to pass to `cb.ax.tick_params`. More information in 
        matplotlib docs at `cb.ax.tick_params` for above and other input options.
    """
    
    cbar_default = {'ax': ax, 'cax': cax, 'orientation': orientation, 
                    'fraction': fraction, 'pad': pad, 'shrink': shrink, 'extend': extend}
    cbar_default.update(**cbargs)  # add in input arguments, overwriting if duplicates.
    cb = plt.colorbar(mappable, **cbar_default)
    
    labelargs_default = {'label': label, 'size': labelsize, 'weight': labelweight}
    labelargs_default.update(**labelargs)
    cb.set_label(**labelargs_default)
    
    tickargs_default = {'labelsize': ticksize}
    tickargs_default.update(**tickargs)
    cb.ax.tick_params(**tickargs_default)
    
    return cb