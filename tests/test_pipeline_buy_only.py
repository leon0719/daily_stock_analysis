# -*- coding: utf-8 -*-
"""REPORT_BUY_ONLY: only buy results are pushed."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.litellm_stub import ensure_litellm_stub

ensure_litellm_stub()

from src.core.pipeline import StockAnalysisPipeline
from src.enums import ReportType


def _result(code, decision_type, advice):
    return SimpleNamespace(code=code, name=code, decision_type=decision_type, operation_advice=advice)


class BuyOnlyTest(unittest.TestCase):
    def _pipeline(self, enabled):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.config = SimpleNamespace(report_buy_only=enabled)
        pipeline.notifier = MagicMock()
        pipeline.notifier.is_available.return_value = False
        pipeline._generate_aggregate_report = MagicMock(return_value="report")
        return pipeline

    def test_filters_hold_results(self):
        pipeline = self._pipeline(True)
        results = [_result("A", "buy", "买入"), _result("B", "hold", "观望"), _result("C", "sell", "卖出")]
        pipeline._send_notifications(results, ReportType.BRIEF)
        pushed = pipeline._generate_aggregate_report.call_args[0][0]
        self.assertEqual([r.code for r in pushed], ["A"])

    def test_no_buy_sends_no_signal_line(self):
        pipeline = self._pipeline(True)
        pipeline.notifier.is_available.return_value = True
        pipeline._send_notifications(
            [_result("B", "hold", "观望"), _result("C", "sell", "减仓")], ReportType.BRIEF
        )
        pipeline._generate_aggregate_report.assert_not_called()
        self.assertIn("今日無買進訊號", pipeline.notifier.send.call_args[0][0])

    def test_disabled_keeps_all(self):
        pipeline = self._pipeline(False)
        results = [_result("A", "buy", "买入"), _result("B", "hold", "观望")]
        pipeline._send_notifications(results, ReportType.BRIEF)
        self.assertEqual(len(pipeline._generate_aggregate_report.call_args[0][0]), 2)


if __name__ == "__main__":
    unittest.main()
