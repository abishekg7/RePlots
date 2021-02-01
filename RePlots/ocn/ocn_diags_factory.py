#!/usr/bin/env python3
"""ocean diagnostics factory function
"""

# import the Plot modules
from ocn_diags_bc import UnknownDiagType
from modelplots import ModelPlots
import model_vs_obs
import model_vs_control
import model_timeseries

def oceanDiagnosticsFactory(diag_type):
    """Create and return an object of the requested type.
    """
    diag = None
    if diag_type == 'MODEL':
        diag = ModelPlots.modelVsObs()

    elif diag_type == 'MODEL_VS_OBS':
        diag = model_vs_control.modelVsControl()

    elif diag_type == 'MODEL_VS_CONTROL':
        diag = model_timeseries.modelTimeseries()

    elif diag_type == 'MODEL_TIMESERIES':
        diag = model_timeseries.modelTimeseries()

    else:
        raise UnknownDiagType('WARNING: Unknown diagnostics type requested: "{0}"'.format(diag_type))

    return diag
