#include <pybind11/pybind11.h>
#include "BondMath.h"

namespace py = pybind11;

PYBIND11_MODULE(_bondyield, m)
{
    m.doc() = "BondYield C++ extension";

    py::class_<BondMath::YieldResult>(m, "YieldResult")
        .def_readonly("yield_value", &BondMath::YieldResult::yield_value)
        .def_readonly("iterations", &BondMath::YieldResult::iterations)
        .def_readonly("elapsed_nanoseconds", &BondMath::YieldResult::elapsed_nanoseconds);

    m.def("calculate_price", &BondMath::CalcPrice,
        py::arg("coupon"),
        py::arg("years"),
        py::arg("face"),
        py::arg("rate"));
    m.def("calculate_yield_stepwise", &BondMath::CalcYield,
        py::arg("coupon"),
        py::arg("years"),
        py::arg("face"),
        py::arg("price"));
    m.def("calculate_yield_deeley", &BondMath::CalcYieldDeeley,
        py::arg("rate"),
        py::arg("term"),
        py::arg("value"),
        py::arg("price"));
}