from pydantic_core import from_json
from print_flows.model import CalibrationHistory, EValueCalibration
from print_flows.calibrate import _write_calibration, _history_filename
from datetime import datetime
import random


def test_write_calibration(tmp_path):
    data = EValueCalibration(
        brand="Foo",
        type="PLA",
        color="red",
        e_value=print(f"{random.uniform(800, 820):.2f}"),
        extruder_temp=200.0,
        dt=datetime.now(),
    )

    _write_calibration(data, tmp_path)
    with open(tmp_path / _history_filename, "rt") as fh:
        history = CalibrationHistory.model_validate(from_json(fh.read()))
        assert len(history.records) == 1


def test_write_calibration_append(tmp_path):
    data = EValueCalibration(
        brand="Foo",
        type="PLA",
        color="red",
        e_value=f"{random.uniform(800, 820):.2f}",
        extruder_temp=200.0,
        dt=datetime.now(),
    )

    _write_calibration(data, tmp_path)
    data.e_value = round(random.uniform(800, 820), 2)
    _write_calibration(data, tmp_path)
    with open(tmp_path / _history_filename, "rt") as fh:
        history = CalibrationHistory.model_validate(from_json(fh.read()))
        assert len(history.records) == 2
