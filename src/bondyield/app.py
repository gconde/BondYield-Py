import sys
from bondyield import _bondyield

from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BondYield-Py")

        central = QWidget()
        main_layout = QVBoxLayout(central)

        inputs_group = QGroupBox("Bond Inputs")
        self.inputs_layout = QFormLayout(inputs_group)

        self.face_value = QDoubleSpinBox()
        self.face_value.setRange(0.01, 1_000_000_000.0)
        self.face_value.setValue(1000.0)
        self.face_value.setDecimals(2)

        self.coupon_rate = QDoubleSpinBox()
        self.coupon_rate.setRange(0.0, 100.0)
        self.coupon_rate.setValue(5.0)
        self.coupon_rate.setDecimals(4)
        self.coupon_rate.setSuffix(" %")

        self.years = QSpinBox()
        self.years.setRange(1, 30)
        self.years.setValue(10)

        self.rate_or_price = QDoubleSpinBox()
        self.rate_or_price.setRange(0.0, 1_000_000_000.0)
        self.rate_or_price.setValue(950.0)
        self.rate_or_price.setDecimals(4)

        self.rate_or_price_label = QLabel("Rate")

        self.inputs_layout.addRow("Face value", self.face_value)
        self.inputs_layout.addRow("Coupon rate", self.coupon_rate)
        self.inputs_layout.addRow("Years", self.years)
        self.inputs_layout.addRow(self.rate_or_price_label, self.rate_or_price)

        main_layout.addWidget(inputs_group)

        calc_group = QGroupBox("Calculation")
        calc_layout = QFormLayout(calc_group)

        self.calculate_price_radio = QRadioButton("Calculate Price")
        self.calculate_yield_radio = QRadioButton("Calculate Yield")
        self.calculate_price_radio.setChecked(True)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)

        calc_layout.addRow(self.calculate_price_radio)
        calc_layout.addRow(self.calculate_yield_radio)
        calc_layout.addRow(self.calculate_button)

        main_layout.addWidget(calc_group)

        results_group = QGroupBox("Results")
        results_layout = QFormLayout(results_group)

        self.primary_result = QLabel("—")
        self.iterative_result = QLabel("—")
        self.deeley_result = QLabel("—")

        results_layout.addRow("Result", self.primary_result)
        results_layout.addRow("Step Wise", self.iterative_result)
        results_layout.addRow("Deeley", self.deeley_result)

        main_layout.addWidget(results_group)

        self.setCentralWidget(central)

        self._last_result = dict()
        self.calculate_price_radio.toggled.connect(self.update_mode)
        self.update_mode()

    def update_mode(self) -> None:
        if self.calculate_price_radio.isChecked():
            self.rate_or_price_label.setText("Rate")
            self.rate_or_price.setSuffix(" %")
            self.rate_or_price.setRange(0.0, 100.0)
            if 'rate' in self._last_result.keys():
                self.rate_or_price.setValue(self._last_result['rate'])
            else:
                self.rate_or_price.setValue(5.0)
        else:
            self._last_result['rate'] = self.rate_or_price.value()
            self.rate_or_price_label.setText("Price")
            self.rate_or_price.setSuffix("")
            self.rate_or_price.setRange(0.01, 1_000_000_000.0)
            if 'price' in self._last_result.keys():
                self.rate_or_price.setValue(round(self._last_result['price'], 2))
            else:
                self.rate_or_price.setValue(950.0)

    def is_deeley_supported(self, coupon: float, years: float, face: float, price: float) -> bool:
        return (
                years >= 2.0
                and coupon >= 0.01
                and face * 0.5 <= price <= face
        )

    def calculate(self) -> None:
        face = self.face_value.value()
        coupon = self.coupon_rate.value() / 100.0
        years = self.years.value()
        input_value = self.rate_or_price.value()

        if self.calculate_price_radio.isChecked():
            rate = input_value / 100.0
            price = _bondyield.calculate_price(coupon, years, face, rate)
            self._last_result['price'] = price

            self.primary_result.setText(f"${price:,.2f}")
            self.iterative_result.setText("—")
            self.deeley_result.setText("—")
        else:
            price = input_value

            iterative = _bondyield.calculate_yield_stepwise(
                face=face,
                price=price,
                coupon=coupon,
                years=years,
            )

            # Deeley's method is shown only for the demo's supported input range.
            # Stepwise yield is still calculated for wider valid inputs.
            if self.is_deeley_supported(coupon, years, face, price):
                deeley = _bondyield.calculate_yield_deeley(
                    value=face,
                    price=price,
                    rate=coupon,
                    term=years,
                )
                self._last_result['rate'] = deeley.yield_value * 100.0
                if abs(deeley.yield_value - iterative.yield_value) < 1e-5:
                    self.primary_result.setText('Algorithms agree!')
                else:
                    self.primary_result.setText('Algorithm yield result is different.')
                self.deeley_result.setText(
                    f"{deeley.yield_value * 100.0:.4f} % | "
                    f"{deeley.iterations} iterations | "
                    f"{deeley.elapsed_nanoseconds / 1_000_000.0:.4f} ms"
                )
            else:
                self.deeley_result.setText("Not supported for this input range")
                self.primary_result.setText('-')
                self._last_result['rate'] = iterative.yield_value * 100.0

            self.iterative_result.setText(
                f"{iterative.yield_value * 100.0:.4f} % | "
                f"{iterative.iterations} iterations | "
                f"{iterative.elapsed_nanoseconds / 1_000_000.0:.4f} ms"
            )



def main() -> None:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(520, 420)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()