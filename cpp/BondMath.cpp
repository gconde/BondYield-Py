#include "BondMath.h"

#include <chrono>
#include <cmath>
#include <stdexcept>

namespace BondMath {

constexpr double tolerance = 1e-10;
constexpr int max_iterations = 1'000'000;
constexpr double near_zero = 1e-7;

double CalcPrice(double coupon, int years, double face, double rate)
{
    if (!std::isfinite(coupon) || !std::isfinite(years) || !std::isfinite(face) || !std::isfinite(rate)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(coupon >= 0. && years > 0 && face > 0. && rate > -1.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    if (std::floor(years) != years) {
        throw std::invalid_argument("Fractional periods are not supported.");
    }
    double r = 1.0 + rate;
    double C = coupon * face;
    double price = face / std::pow(r, years);
    for (int i = 1; i <= years; i++) {
        price += C / std::pow(r, i);
    }
    return price;
}

YieldResult CalcYield(double coupon, int years, double face, double price)
{
    if (!std::isfinite(coupon) || !std::isfinite(years) || !std::isfinite(face) || !std::isfinite(price)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(coupon >= 0. && years > 0 && face > 0. && price > 0.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    if (std::floor(years) != years) {
        throw std::invalid_argument("Fractional periods are not supported.");
    }
    double C = coupon * face;
    double r = (C - (price - face) / years) / ((price + face) / 2.0); //initial guess
    double increment = r / 2.;
    double calc_price = 0.0;
    double delta = 1.0;
    bool sign = true; //false for subtract, true for add
    int iterations = 0;
    auto start = std::chrono::steady_clock::now();
    while (std::fabs(delta) > tolerance) {
        calc_price = CalcPrice(coupon, years, face, r);
        delta = calc_price - price;
        if (std::fabs(delta) > tolerance) {
            if (delta < 0.0) {
                //calc was less, guess lower r
                r -= increment;
                if (sign) {
                    increment /= 2.0;
                    sign = false;
                }
            }
            else {
                //calc was greater, guess higher r
                r += increment;
                if (!sign) {
                    increment /= 2.0;
                    sign = true;
                }
            }
        }
        ++iterations;
        if (iterations > max_iterations) {
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

YieldResult CalcYieldDeeley(double rate, int n, double V, double P)
{
    if (!std::isfinite(rate) || !std::isfinite(n) || !std::isfinite(V) || !std::isfinite(P)) {
        throw std::invalid_argument("Non-finite input detected.");
    }
    if (!(rate >= 0. && n > 0 && V > 0. && P > 0.)) {
        throw std::invalid_argument("Invalid input range detected.");
    }
    if (std::floor(n) != n) {
        throw std::invalid_argument("Fractional periods are not supported.");
    }
    auto start = std::chrono::steady_clock::now();
    double calc_price = 0.0;
    double delta = 1.0;
    int iterations = 0;
    double C = rate * V;
    double i = (C - (P - V) / n) / ((P + V) / 2.0); //initial guess
    while (std::fabs(delta) > tolerance) {
        if (std::fabs(i) < near_zero) {
            throw std::runtime_error("Calculation failed.");
        }
        double FV = C * ((std::pow(1.0 + i, n) - 1.0) / i) + V;
        i = std::pow(FV / P, 1.0 / n) - 1.0;
        calc_price = CalcPrice(rate, n, V, i);
        delta = calc_price - P;
        ++iterations;
        if (iterations > max_iterations) {
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
}