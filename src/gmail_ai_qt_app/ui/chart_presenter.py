from __future__ import annotations

import pyqtgraph as pg


class MainWindowChartPresenter:
    def __init__(self, window):
        self.window = window

    def configure_plots(self) -> None:
        pg.setConfigOptions(antialias=True)

        self._reset_plot(self.window.activity_plot)
        self._reset_plot(self.window.rate_plot)

        self._setup_plot(
            self.window.activity_plot,
            self.window.text("plot_activity_title"),
            y_range=None,
            axis_color="#64748b",
        )
        self._setup_plot(
            self.window.rate_plot,
            self.window.text("plot_rate_title"),
            y_range=(0, 100),
            axis_color="#64748b",
        )

        self.window.activity_plot.addLegend(
            offset=(12, 12),
            brush=(255, 255, 255, 230),
            pen=pg.mkPen("#d7dee7"),
        )

        self.window.activity_checked_curve = self.window.activity_plot.plot(
            pen=pg.mkPen("#0f766e", width=3),
            name=self.window.text("plot_legend_checked"),
        )
        self.window.activity_hit_curve = self.window.activity_plot.plot(
            pen=pg.mkPen("#16a34a", width=3),
            name=self.window.text("plot_legend_hit"),
        )
        self.window.rate_curve = self.window.rate_plot.plot(
            pen=pg.mkPen("#c2410c", width=3),
            name=self.window.text("plot_legend_rate"),
        )

    def apply_snapshot(self, payload: dict) -> None:
        self.window.last_snapshot = payload
        stats = payload["stats"]
        history = payload["history"]

        checked = int(stats["checked"])
        hit = int(stats["hit"])
        taken = int(stats.get("taken", 0))
        hold = int(stats.get("hold", 0))
        error = int(stats["error"])
        rate = float(stats["rate"])

        self.window.checked_card.value_label.setText(str(checked))
        self.window.hit_card.value_label.setText(str(hit))
        self.window.error_card.value_label.setText(str(taken))
        if self.window.runtime_settings.provider == "manual":
            self.window.rate_card.value_label.setText(str(hold))
        else:
            self.window.rate_card.value_label.setText(str(error))
        self.window.rate_badge.setText(self.window.text("rate_badge", rate=rate))

        x_values = list(range(len(history["checked"])))
        self.window.activity_checked_curve.setData(x_values, history["checked"])
        self.window.activity_hit_curve.setData(x_values, history["hit"])
        self.window.rate_curve.setData(x_values, history["rate"])

    @staticmethod
    def _reset_plot(plot_widget) -> None:
        plot_item = plot_widget.getPlotItem()
        plot_item.clear()
        if plot_item.legend is not None:
            plot_item.legend.scene().removeItem(plot_item.legend)
            plot_item.legend = None

    @staticmethod
    def _setup_plot(plot_widget, title: str, y_range, axis_color: str) -> None:
        plot_widget.setBackground("transparent")
        plot_item = plot_widget.getPlotItem()
        plot_item.setMenuEnabled(False)
        plot_item.showGrid(x=True, y=True, alpha=0.22)
        plot_item.setTitle(title, color="#0f172a", size="12pt")
        plot_item.hideButtons()

        axis_pen = pg.mkPen(axis_color)
        for axis_name in ("left", "bottom"):
            axis = plot_item.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(axis_pen)

        if y_range is not None:
            plot_widget.setYRange(*y_range, padding=0.06)
