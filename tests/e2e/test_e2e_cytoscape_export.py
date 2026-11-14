"""Validation tests for Cytoscape.js export schema and graph topology."""

from __future__ import annotations

import unittest
from sbh.e2e.cytoscape import CytoscapeValidator


class TestE2ECytoscapeExport(unittest.TestCase):
    """Verify Cytoscape element validation edge cases."""

    def test_valid_elements(self):
        payload = {
            "nodes": [
                {"data": {"id": "n1", "label": "node_1", "risk_category": "bot"}},
                {"data": {"id": "n2", "label": "node_2", "risk_category": "human"}},
            ],
            "edges": [
                {"data": {"id": "n1->n2", "source": "n1", "target": "n2"}},
            ],
        }
        report = CytoscapeValidator.validate(payload)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.node_count, 2)
        self.assertEqual(report.edge_count, 1)
        self.assertEqual(len(report.orphan_edges), 0)

    def test_orphan_edge_detection(self):
        payload = {
            "nodes": [{"data": {"id": "n1", "label": "node_1"}}],
            "edges": [{"data": {"id": "n1->n2", "source": "n1", "target": "missing_node"}}],
        }
        report = CytoscapeValidator.validate(payload)
        self.assertFalse(report.is_valid)
        self.assertIn("n1->missing_node", report.orphan_edges)

    def test_missing_required_keys(self):
        payload = {
            "nodes": [{"data": {"id": "n1"}}],  # missing label
            "edges": [{"data": {"source": "n1"}}],  # missing id and target
        }
        report = CytoscapeValidator.validate(payload)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("label" in m for m in report.missing_fields))


if __name__ == "__main__":
    unittest.main()
