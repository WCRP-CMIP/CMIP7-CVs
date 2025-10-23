'''
pytest -v --color=yes test_cv.py
'''


import pytest
import json
import os


def test_cv_structure(cv_data):
    """Test if the CV data has the correct top-level structure."""
    assert set(cv_data.keys()) == {
        'CV'}, "CV data should have only one top-level key: 'CV'"


def test_conventions(cv_data):
    """Test if the Conventions field is correctly formatted."""
    conventions = cv_data['CV']['Conventions']
    assert conventions == [
        "^CF-1.7 CMIP-6.[0-2,5]\\( UGRID-1.0\\)\\{0,\\}$"], f"Unexpected Conventions format: {conventions}"


def test_activity_id(cv_data):
    """Test if activity_id is a dictionary."""
    assert isinstance(cv_data['CV']['activity_id'],
                      dict), "activity_id should be a dictionary"


def test_experiment_structure(cv_data):
    """Test if the experiment structure contains all required keys."""

    expected_keys = {
        "activity_id", "additional_allowed_model_components", "description",
        "experiment", "experiment_id", "parent_activity_id",
        "parent_experiment_id", "required_model_components", "sub_experiment_id"
    }

    for test_experiment in cv_data['CV']['experiment_id'].values():

        missing_keys = expected_keys - set(test_experiment.keys())
        assert not missing_keys, f"Experiment is missing the following keys: {missing_keys}"


def test_experiment_types(cv_data):
    """Test if the experiment fields have the correct types."""
    expected_types = {
        "activity_id": list,
        "additional_allowed_model_components": list,
        "description": str,
        "experiment": str,
        "experiment_id": str,
        "parent_activity_id": list,
        "parent_experiment_id": list,
        "required_model_components": list,
        "sub_experiment_id": list,
    }
    for test_experiment in cv_data['CV']['experiment_id'].values():
        for attr, attr_type in expected_types.items():
            assert isinstance(
                test_experiment[attr], attr_type), f"Field '{attr}' should be of type {attr_type}, but is {type(test_experiment[attr])}"


def test_sub_experiment_id(cv_data):
    """Test if sub_experiment_id is valid."""
    for test_experiment in cv_data['CV']['experiment_id'].values():
        assert test_experiment['sub_experiment_id'][0] in cv_data['CV']['sub_experiment_id'], \
            f"Invalid sub_experiment_id: {test_experiment['sub_experiment_id'][0]} from experiment {test_experiment['experiment_id']}"


def test_index_types(cv_data):
    """Test if index fields are lists."""
    index_types = ['realization', 'initialization', 'physics', 'forcing']
    for index_type in index_types:
        assert isinstance(cv_data['CV'][f'{index_type}_index'], list), \
            f"{index_type}_index should be a list, but is {type(cv_data['CV'][f'{index_type}_index'])}"


def test_institution_id(cv_data):
    """Test if institution_id is a dictionary."""
    assert isinstance(cv_data['CV']['institution_id'], dict), \
        f"institution_id should be a dictionary, but is {type(cv_data['CV']['institution_id'])}"


def test_license(cv_data):
    """Test if license is a list with the correct format."""
    assert isinstance(cv_data['CV']['license'],
                      list), "license should be a list"
    assert cv_data['CV']['license'][0].startswith("^CMIP6Plus model data produced by"), \
        f"Unexpected license format: {cv_data['CV']['license'][0]}"


def test_nominal_resolution(cv_data):
    """Test if nominal_resolution contains expected values."""
    expected_resolutions = {
        "0.5 km", "1 km", "10 km", "100 km", "1000 km", "10000 km",
        "1x1 degree", "2.5 km", "25 km", "250 km", "2500 km",
        "5 km", "50 km", "500 km", "5000 km",
    }
    actual_resolutions = set(cv_data['CV']['nominal_resolution'])
    missing_resolutions = expected_resolutions - actual_resolutions
    extra_resolutions = actual_resolutions - expected_resolutions
    assert not missing_resolutions and not extra_resolutions, \
        f"Missing resolutions: {missing_resolutions}, Unexpected resolutions: {extra_resolutions}"


def test_realm(cv_data):
    """Test if realm contains all expected keys."""
    expected_realms = {'aerosol', 'atmos', 'atmosChem',
                       'land', 'landIce', 'ocean', 'ocnBgchem', 'seaIce'}
    actual_realms = set(cv_data['CV']['realm'].keys())
    missing_realms = expected_realms - actual_realms
    extra_realms = actual_realms - expected_realms
    assert not missing_realms and not extra_realms, \
        f"Missing realms: {missing_realms}, Unexpected realms: {extra_realms}"


def test_required_global_attributes(cv_data):
    """Test if required_global_attributes contains all expected attributes."""
    expected_attributes = [
        "Conventions", "activity_id", "creation_date", "data_specs_version",
        "experiment", "experiment_id", "forcing_index", "frequency",
        "grid", "grid_label", "initialization_index", "institution",
        "institution_id", "license", "mip_era", "nominal_resolution",
        "physics_index", "realization_index", "realm", "source",
        "source_id", "source_type", "sub_experiment", "sub_experiment_id",
        "table_id", "tracking_id", "variable_id", "variant_label"
    ]
    actual_attributes = set(cv_data['CV']['required_global_attributes'])
    missing_attributes = set(expected_attributes) - actual_attributes
    extra_attributes = actual_attributes - set(expected_attributes)
    assert not missing_attributes and not extra_attributes, \
        f"Missing attributes: {missing_attributes}, Unexpected attributes: {extra_attributes}"


def test_source_id(cv_data):
    """Test if source_id has the correct structure and types."""
    expected = {
        'activity_participation': list,
        'cohort': list,
        'institution_id': list,
        'source': str,
        'source_id': str
    }

    for test_source_id in cv_data['CV']['source_id'].values():
        for attr, attr_type in expected.items():
            assert isinstance(test_source_id[attr], attr_type), \
                f"Field '{attr}' should be of type {attr_type}, but is {type(test_source_id[attr])}"
        assert test_source_id['cohort'] == ['Published'], \
            f"Cohort should be ['Published'], but is {test_source_id['cohort']}"


def test_miscellaneous(cv_data):
    """Test miscellaneous fields for correct types and values."""
    for field in ['table_id', 'tracking_id', 'variant_label']:
        assert isinstance(cv_data['CV'].get(field),
                          list), f"{field} should be a list"
    assert isinstance(cv_data['CV']['version_metadata'],
                      dict), "version_metadata should be a dictionary"
    assert cv_data['CV'][
        'product'] == 'model-output', f"product should be 'model-output', but is {cv_data['CV']['product']}"
    assert cv_data['CV']['realm']["ocnBgchem"] == "Ocean Biogeochemistry", \
        f"ocnBgchem realm should be 'Ocean Biogeochemistry', but is {cv_data['CV']['realm']['ocnBgchem']}"


def test_no_null(cv_data, current_path=None, main=True):
    null_keys = []
    if current_path is None:
        current_path = []

    if isinstance(cv_data, dict):
        for key, value in cv_data.items():
            new_path = current_path + [key]
            if value is None:
                null_keys.append('.'.join(map(str, new_path)))
            elif isinstance(value, (dict, list)):
                null_keys.extend(test_no_null(value, new_path, False))

    elif isinstance(cv_data, list):
        for index, value in enumerate(cv_data):
            new_path = current_path + [index]
            if value is None:
                null_keys.append('.'.join(map(str, new_path)))
            elif isinstance(value, (dict, list)):
                null_keys.extend(test_no_null(value, new_path, False))

    if main:
        keys = [str(i) for i in enumerate(null_keys)]
        assert len(keys) == 0, f"Null values found at: {keys}"
    else:
        return null_keys
