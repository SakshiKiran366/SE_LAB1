import pytest

from shipping_quote import process_shipments, monitor_container_pressures


def test_invalid_shipments_input():
    with pytest.raises(ValueError):
        process_shipments("invalid", 20)

    with pytest.raises(ValueError):
        process_shipments([], -1)


def test_empty_shipments():
    result = process_shipments([], 20)
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_unapproved_shipment():
    shipments = [{"manifest_approved": False}]
    result = process_shipments(shipments, 20)
    assert result["status"] == "NO_CARGO"


def test_air_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "air",
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 140.0
    assert result["status"] == "CLEARED"


def test_ground_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"


def test_express_priority():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": True,
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 75.0


def test_heavy_package():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 40, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 260.0


def test_zero_and_negative_package_weights():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0, "is_hazmat": False},
            {"weight_kg": -5, "is_hazmat": False}
        ]
    }]
    result = process_shipments(shipments, 20)
    assert result["status"] == "CLEARED"


def test_hazardous_non_fragile_package():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 10, "is_hazmat": True}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 70.0
    assert result["status"] == "CLEARED"


def test_hazardous_fragile_package():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": True,
        "packages": [{"weight_kg": 10, "is_hazmat": True}]
    }]
    result = process_shipments(shipments, 20)
    assert result["total_quote"] == 0.0
    assert result["status"] == "NO_CARGO"


def test_unknown_transport_mode():
    shipments = [{
        "manifest_approved": True,
        "mode": "sea",
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 20)
    assert result["status"] == "NO_CARGO"


def test_too_many_rejected_parcels():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0, "is_hazmat": False},
            {"weight_kg": 0, "is_hazmat": False},
            {"weight_kg": 0, "is_hazmat": False},
            {"weight_kg": 0, "is_hazmat": False}
        ]
    }]
    result = process_shipments(shipments, 20)
    assert result["status"] == "FLAGGED_REVIEW"


def test_no_pressure_data():
    assert monitor_container_pressures([]) == "NO_DATA"
    assert monitor_container_pressures([[]]) == "STABLE"


def test_pressure_leak_detection():
    assert monitor_container_pressures([[13.0, 12.0]]) == "LEAK_DETECTED"


def test_pressure_returns_to_normal():
    assert monitor_container_pressures([[13.0, 15.0, 13.0]]) == "STABLE"


def test_pressure_single_low_reading():
    assert monitor_container_pressures([[13.0]]) == "STABLE"


def test_pressure_streak_resets():
    assert monitor_container_pressures([[13.0, 15.0, 13.0, 12.0]]) == "LEAK_DETECTED"
