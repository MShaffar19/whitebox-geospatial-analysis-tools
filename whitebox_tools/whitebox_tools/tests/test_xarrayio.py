
import numpy as np
import pytest
import xarray as xr

from whitebox_tools.whitebox_cli import * # __all__ is defined there

HELP = get_all_help()

DEFAULT_ATTRS = {
    'south': 0,
    'north': 1,
    'east': -1,
    'west': 1,
    'data_scale': 'continuous',
    'rows': 'FILL_OUT_LATER',
    'cols': 'FILL_OUT_LATER',
    'xy_units': 'meters',
    'z_units': 'meters',
    'min': 0.,
    'max': 10.,
}


def example_arr(shape=(100, 100), min_max=(0, 10)):
    X = np.random.uniform(0, 1, shape)
    x, y = (np.linspace(0, 10, s) for s in shape)
    X = xr.DataArray(X, coords=[('x', x), ('y', y)], dims=('x', 'y'))
    attrs = DEFAULT_ATTRS.copy()
    attrs['rows'], attrs['cols'] = shape
    X.attrs.update(attrs)
    return X


def example_xr(shape=(100, 100), names=None):

    if not names:
        return example_arr(shape=shape)
    X = {}
    for name in names:
        X[name] = example_arr(shape=shape)
    return X


def make_synthetic_kwargs(tool, shape=(100,100), names=None):
    arg_spec_help = HELP[tool]
    kwargs = {}
    for arg_names, help_str in arg_spec_help:
        arg_name = [a[2:] for a in arg_names if '--' == a[:2]][0]
        if 'input' == arg_name:
            kwargs[arg_name] = example_xr(shape=shape, names=names)
        else:
            pass #? anything TODO here?
    return kwargs


def _data_arr_assert(arr, shape=(100, 100)):
    assert arr.dims == ('x', 'y')
    assert arr.values.shape == shape
    assert 'kwargs' in arr.attrs


possible_names = (None, ('one_raster'), ('raster_a', 'raster_b'))
tools_names_list = [(tool, names) for tool in tools for names in possible_names]
@pytest.mark.parametrize('tool, names', tools_names_list)
def test_each_tool(tool, names):
    shape = (100, 100)
    kwargs = make_synthetic_kwargs(tool, shape=shape, names=names)
    out = globals()[tool](**kwargs)
    if names:
        assert isinstance(out, xr.Dataset)
        assert set(names) == set(out.data_vars)
        for name in names:
            _data_arr_assert(out[name], shape=shape)
    else:
        assert isinstance(out, xr.DataArray)
        _data_arr_assert(out, shape=shape)

