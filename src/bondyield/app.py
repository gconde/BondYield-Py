from bondyield import _bondyield


def main() -> None:
    result = _bondyield.calculate_price(face=1000.0,
    rate=.15,
    coupon=0.1,
    years=5)
    print(f"price: {result}")
    result = _bondyield.calculate_yield_iterative(face=1000.0,
    price=832.4,
    coupon=0.1,
    years=5)
    print(f"iterative yield: {result.yield_value}, iterations: {result.iterations}, elapsed_nanoseconds: {result.elapsed_nanoseconds}")
    result = _bondyield.calculate_yield_deeley(value=1000.0,
    price=832.4,
    rate=0.1,
    term=5)
    print(f"deeley yield: {result.yield_value}, iterations: {result.iterations}, elapsed_nanoseconds: {result.elapsed_nanoseconds}")


if __name__ == "__main__":
    main()