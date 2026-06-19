#include "BondMath.h"

#include <chrono>
#include <cmath>
#include <stdexcept>

namespace BondMath {

double CalcPrice(double coupon, double years, double face, double rate)
{
    if (!std::isfinite(coupon) || !std::isfinite(years) || !std::isfinite(face) || !std::isfinite(rate)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(coupon >= 0. && years > 0. && face > 0. && rate > -1.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    double r = 1.f + rate;
    double C = coupon * face;
    double price = face / std::pow(r, years);
    for (int i = 1; i <= years; i++) {
        price += C / std::pow(r, i);
    }
    return price;
}

YieldResult CalcYield(double coupon, double years, double face, double price)
{
    if (!std::isfinite(coupon) || !std::isfinite(years) || !std::isfinite(face) || !std::isfinite(price)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(coupon >= 0. && years > 0. && face > 0. && price > 0.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    double C = coupon * face;
    double r = (C - (price - face) / years) / ((price + face) / 2.f); //initial guess
    double increment = r / 2.;
    double calc_price = 0.f;
    double delta = 1.f;
    bool sign = true; //false for subtract, true for add
    int iterations = 0;
    auto start = std::chrono::steady_clock::now();
    while (std::fabs(delta) > 1e-010) {
        calc_price = CalcPrice(coupon, years, face, r);
        delta = calc_price - price;
        if (std::fabs(delta) > 1e-010) {
            if (delta < 0.f) {
                //calc was less, guess lower r
                r -= increment;
                if (sign) {
                    increment /= 2.f;
                    sign = false;
                }
            }
            else {
                //calc was greater, guess higher r
                r += increment;
                if (!sign) {
                    increment /= 2.f;
                    sign = true;
                }
            }
        }
        ++iterations;
        if (iterations > 1000000) {
            r = -1;
            break;
        }
    }
    auto end = std::chrono::steady_clock::now();
    auto diff = end - start;
    auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(diff);
    return YieldResult{
        .yield_value = r,
        .iterations = iterations,
        .elapsed_nanoseconds = ns.count()
    };
}

YieldResult CalcYieldDeeley(double rate, double n, double V, double P)
{
    if (!std::isfinite(rate) || !std::isfinite(n) || !std::isfinite(V) || !std::isfinite(P)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(rate >= 0. && n > 0. && V > 0. && P > 0.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    auto start = std::chrono::steady_clock::now();
    double calc_price = 0.f;
    double delta = 1.f;
    int iterations = 0;
    double C = rate * V;
    double i = (C - (P - V) / n) / ((P + V) / 2.f); //initial guess
    while (std::fabs(delta) > 1e-010) {
        if (std::fabs(i) < 0.0000001) {
            throw std::runtime_error("Calculation failed.");
        }
        double FV = C * ((std::pow(1.f + i, n) - 1.f) / i) + V;
        i = std::pow(FV / P, 1.f / n) - 1.f;
        calc_price = CalcPrice(rate, n, V, i);
        delta = calc_price - P;
        ++iterations;
        if (iterations > 1000000) {
            i = -1;
            break;
        }
    }
    auto end = std::chrono::steady_clock::now();
    auto diff = end - start;
    auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(diff);
    return YieldResult{
        .yield_value = i,
        .iterations = iterations,
        .elapsed_nanoseconds = ns.count()
    };
}
} // namespace BondYield