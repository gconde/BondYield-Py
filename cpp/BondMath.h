#pragma once

#include <cstdint>

/*!
 * Very large values will cause low accurcy results??
 */
namespace BondMath {

    struct YieldResult {
        double yield_value {};
        int iterations {};
        int64_t elapsed_nanoseconds {};
    };

    /*!
     * Calculates the present value of the bond.
     *
     * \param coupon Rate per period.
     * \param years The term to maturity in interest (or rate) periods.
     * \param face The redemption value of the bond.
     * \param rate Annual rate of reinvestment.
     * \return The present value of the bond.
     */
    double CalcPrice(double coupon, double years, double face, double rate);

    /*!
     * Calculates the bond yield using an iterative approach. Approaches
     * the correct yield by adding/subtracting to the rate based on the difference
     * to the correct price by an amount that gets smaller.
     *
     * \param coupon Rate per period.
     * \param years The term to maturity in interest (or rate) periods.
     * \param face The redemption value of the bond.
     * \param price The purchase price of the bond.
     * \return The yield.
     */
    YieldResult CalcYield(double coupon, double years, double face, double price);

    /*!
     * Calculates the bond yield.
     * Uses algorithm described here: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1253166
     * Basically better than Newton's Method as it converges faster.
     *
     * \param rate Rate per period.
     * \param n The term to maturity in interest (or rate) periods.
     * \param V The redemption value of the bond.
     * \param P The purchase price of the bond.
     * \return The yield.
     */
    YieldResult CalcYieldDeeley(double rate, double n, double V, double P);
}
