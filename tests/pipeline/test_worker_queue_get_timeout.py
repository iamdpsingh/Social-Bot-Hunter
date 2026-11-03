from __future__ import annotations

import unittest

from sbh.pipeline.worker import BoundedJobQueue


class PipelineWorkerTest_test_worker_queue_get_timeout(unittest.TestCase):
    def test_empty_timeout(self) -> None:
        q = BoundedJobQueue(maxsize=10)
        self.assertIsNone(q.get(timeout=0.01))
