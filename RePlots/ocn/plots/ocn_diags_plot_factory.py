#!/usr/bin/env python3
"""ocean diagnostics plots factory function
"""

# import the Plot modules
from RePlots.ocn.plots.ocn_diags_plot_bc import UnknownPlotType
#import basin_averages
#import eulerian_velocity
#import horizontal_vector_fields
from RePlots.ocn.plots import surface_fields
#import zonal_average_3d_fields

plot_map = {'PM_BASINAVGTS': 'basin_averages.BasinAverages_{0}()',
            'PM_VELZ': 'eulerian_velocity.EulerianVelocity_{0}()',
            'PM_VECV': 'horizontal_vector_fields.HorizontalVectorFields_{0}()',
            'PM_SEAS': 'seasonal_cycle.SeasonalCycle_{0}()',
            'PM_FLD2D': 'surface_fields.SurfaceFields_{0}()',
            'PM_FLD3DZA': 'zonal_average_3d_fields.ZonalAverage3dFields_{0}()',}

# TODO diag_type must be 'obs' or 'model' or whatever to match the classname in the plot class
def oceanDiagnosticPlotFactory(diag_type, plot_type):
    """Create and return an object of the requested type.
    """
    plot = None

    try:
        plot_string = plot_map[plot_type].format(diag_type)
        print('Requested plot class {0}',format(plot_string))
    except KeyError:
        # TODO throw a warning that diag type does not exist
        print('WARNING: diag type does not exist')
        pass

    try:
        plot = eval(plot_string)
    except NameError:
        # TODO throw a warning that plot class does not exist
        print('WARNING: plot class does not exist')
        pass

    return plot
