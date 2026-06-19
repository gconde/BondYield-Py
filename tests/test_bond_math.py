import math
import itertools
import pytest

from bondyield import _bondyield


def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-5,
    message: str = "",
) -> None:
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (
        f"{message}\n"
        f"actual={actual}, expected={expected}, tolerance={tolerance}"
    )


def test_price_at_par_rate_equals_face_value():
    price = _bondyield.calculate_price(
        coupon=0.05,
        years=10,
        face=1000.0,
        rate=0.05,
    )

    assert_close(price, 1000.0)


def test_yield_methods_agree_for_discount_bond():
    iterative = _bondyield.calculate_yield_stepwise(
        coupon=0.05,
        years=10,
        face=1000.0,
        price=950.0,
    )

    deeley = _bondyield.calculate_yield_deeley(
        rate=0.05,
        term=10,
        value=1000.0,
        price=950.0,
    )

    assert_close(iterative.yield_value, deeley.yield_value, tolerance=1e-6)
    assert iterative.iterations > deeley.iterations


def test_yield_methods_agree_for_premium_bond():
    iterative = _bondyield.calculate_yield_stepwise(
        coupon=0.05,
        years=10,
        face=1000.0,
        price=1050.0,
    )

    deeley = _bondyield.calculate_yield_deeley(
        rate=0.05,
        term=10,
        value=1000.0,
        price=1050.0,
    )

    assert_close(iterative.yield_value, deeley.yield_value, tolerance=1e-6)


def test_yield_result_has_expected_fields():
    result = _bondyield.calculate_yield_deeley(
        rate=0.05,
        term=10,
        value=1000.0,
        price=950.0,
    )

    assert isinstance(result.yield_value, float)
    assert isinstance(result.iterations, int)
    assert isinstance(result.elapsed_nanoseconds, int)
    assert result.iterations > 0
    assert result.elapsed_nanoseconds >= 0


def test_one_iteration_yield():
    iterative = _bondyield.calculate_yield_stepwise(
        coupon=0.05,
        years=10,
        face=1000.0,
        price=1000.0,
    )

    assert_close(iterative.yield_value, .05, tolerance=1e-6)
    assert iterative.iterations == 1

    deeley = _bondyield.calculate_yield_deeley(
        rate=0.05,
        term=10,
        value=1000.0,
        price=1000.0,
    )

    assert_close(deeley.yield_value, .05, tolerance=1e-6)
    assert deeley.iterations == 1


@pytest.mark.parametrize(
    "coupon,years,face,price_multiplier",
    list(itertools.product(
        [0.01, 0.05, 0.20],
        [2, 10, 30],
        [100.0, 1000.0],
        [0.5, 0.75, .95, 1],
    )),
)
def test_yield_methods_agree_across_supported_grid(
    coupon: float,
    years: float,
    face: float,
    price_multiplier: float,
):
    price = face * price_multiplier

    iterative = _bondyield.calculate_yield_stepwise(
        coupon=coupon,
        years=years,
        face=face,
        price=price,
    )

    deeley = _bondyield.calculate_yield_deeley(
        rate=coupon,
        term=years,
        value=face,
        price=price,
    )

    case = (
        f"coupon={coupon}, years={years}, face={face}, "
        f"price_multiplier={price_multiplier}, price={price}"
    )

    assert iterative.yield_value != -1, case
    assert deeley.yield_value != -1, case

    assert_close(
        deeley.yield_value,
        iterative.yield_value,
        tolerance=1e-4,
        message=case,
    )


def test_iterative_yield_reprices_supported_grid():
    coupons = [0.01, 0.05, 0.20]
    years_values = [1, 2, 10, 30]
    face_values = [100.0, 1000.0]
    price_multipliers = [0.5, 0.75, 0.95, 1.0]

    for coupon, years, face, price_multiplier in itertools.product(
        coupons,
        years_values,
        face_values,
        price_multipliers,
    ):
        price = face * price_multiplier

        result = _bondyield.calculate_yield_stepwise(
            coupon=coupon,
            years=years,
            face=face,
            price=price,
        )

        repriced = _bondyield.calculate_price(
            coupon=coupon,
            years=years,
            face=face,
            rate=result.yield_value,
        )

        case = (
            f"coupon={coupon}, years={years}, face={face}, "
            f"price_multiplier={price_multiplier}, price={price}, "
            f"yield={result.yield_value}, repriced={repriced}, "
            f"iterations={result.iterations}"
        )

        assert result.yield_value != -1, case

        assert_close(
            repriced,
            price,
            tolerance=1e-6,
            message=case,
        )


@pytest.mark.parametrize(
    "coupon,years,face,rate",
    [
        (float("nan"), 10, 1000.0, 0.05),
        (0.05, 10, float("nan"), 0.05),
        (0.05, 10, 1000.0, float("nan")),
        (0.05, 0, 1000.0, 0.05),
        (0.05, -1, 1000.0, 0.05),
        (0.05, 10, 0.0, 0.05),
        (0.05, 10, -1000.0, 0.05),
        (-0.01, 10, 1000.0, 0.05),
        (0.05, 10, 1000.0, -1.0),
    ],
)
def test_calculate_price_rejects_invalid_inputs(coupon, years, face, rate):
    with pytest.raises(ValueError):
        _bondyield.calculate_price(
            coupon=coupon,
            years=years,
            face=face,
            rate=rate,
        )


@pytest.mark.parametrize(
    "coupon,years,face,price",
    [
        (float("nan"), 10, 1000.0, 950.0),
        (0.05, 10, float("nan"), 950.0),
        (0.05, 10, 1000.0, float("nan")),
        (0.05, 0, 1000.0, 950.0),
        (0.05, -1, 1000.0, 950.0),
        (0.05, 10, 0.0, 950.0),
        (0.05, 10, -1000.0, 950.0),
        (0.05, 10, 1000.0, 0.0),
        (0.05, 10, 1000.0, -950.0),
        (-0.01, 10, 1000.0, 950.0),
    ],
)
def test_calculate_yield_stepwise_rejects_invalid_inputs(coupon, years, face, price):
    with pytest.raises(ValueError):
        _bondyield.calculate_yield_stepwise(
            coupon=coupon,
            years=years,
            face=face,
            price=price,
        )


@pytest.mark.parametrize(
    "rate,term,value,price",
    [
        (float("nan"), 10, 1000.0, 950.0),
        (0.05, 10, float("nan"), 950.0),
        (0.05, 10, 1000.0, float("nan")),
        (0.05, 0, 1000.0, 950.0),
        (0.05, -1, 1000.0, 950.0),
        (0.05, 10, 0.0, 950.0),
        (0.05, 10, -1000.0, 950.0),
        (0.05, 10, 1000.0, 0.0),
        (0.05, 10, 1000.0, -950.0),
        (-0.01, 10, 1000.0, 950.0),
    ],
)
def test_calculate_yield_deeley_rejects_invalid_inputs(rate, term, value, price):
    with pytest.raises(ValueError):
        _bondyield.calculate_yield_deeley(
            rate=rate,
            term=term,
            value=value,
            price=price,
        )
