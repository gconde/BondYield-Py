#pragma once

#include <cstdint>

namespace BondMath {

    struct YieldResult {
        double yield_value {};
        int iterations {};
        int64_t elapsed_nanoseconds {};
    };

    /*!
     * Calculates the present value of a fixed-rate coupon bond.
     *
     * Inputs are expressed per period. For example, a 5% coupon rate
     * should be passed as 0.05.
     *
     * Throws std::invalid_argument for invalid or non-finite inputs.
     *
     * \param coupon Coupon rate per period.
     * \param years Number of remaining periods to maturity.
     * \param face Redemption value of the bond.
     * \param rate Discount rate per period.
     * \return Present value of the bond.
     */
    double CalcPrice(double coupon, int years, double face, double rate);

    /*!
     * Calculates bond yield using a simple stepwise search.
     *
     * This method starts with an approximate yield and adjusts it up or
     * down until the calculated price matches the target price within the
     * implementation tolerance.
     *
     * Returns YieldResult::yield_value == -1.0 if the search does not
     * converge within the iteration limit.
     *
     * Throws std::invalid_argument for invalid or non-finite inputs.
     *
     * \param coupon Coupon rate per period.
     * \param years Number of remaining periods to maturity.
     * \param face Redemption value of the bond.
     * \param price Purchase price of the bond.
     * \return Yield result, including yield, iteration count, and timing.
     */
    YieldResult CalcYield(double coupon, int years, double face, double price);

    /*!
     * Calculates bond yield using Deeley's method.
     *
     * Deeley's method is described in:
     * "Superseding Newton with a superior bond yield algorithm"
     * by Chris Deeley.
     *
     * This demo uses Deeley's method for ordinary positive-yield coupon
     * bond examples. Some edge cases are intentionally treated as outside
     * the supported demo range.
     *
     * Returns YieldResult::yield_value == -1.0 if the calculation does not
     * converge within the iteration limit.
     *
     * Throws std::invalid_argument for invalid or non-finite inputs.
     * Throws std::runtime_error if the calculation reaches an unsupported
     * numerical condition.
     *
     * \param rate Coupon rate per period.
     * \param n Number of remaining periods to maturity.
     * \param V Redemption value of the bond.
     * \param P Purchase price of the bond.
     * \return Yield result, including yield, iteration count, and timing.
     */
    YieldResult CalcYieldDeeley(double rate, int n, double V, double P);
}