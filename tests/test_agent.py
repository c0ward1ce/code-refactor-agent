from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from refactor_agent.agent import RefactorAgent
from refactor_agent.config import AgentConfig


class RefactorAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = Path(__file__).resolve().parents[1] / ".tmp-tests"
        self.workspace.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        if self.workspace.exists():
            shutil.rmtree(self.workspace)

    def test_scan_detects_python_findings(self) -> None:
        case_dir = self.workspace / "scan-case"
        case_dir.mkdir(parents=True, exist_ok=True)
        target = case_dir / "sample.py"
        target.write_text("if value == None:\n    pass\n", encoding="utf-8")

        agent = RefactorAgent(AgentConfig(root=case_dir, exclude_dirs=()))
        analyses, plan = agent.scan()

        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0].language, "python")
        self.assertEqual(len(plan), 1)
        self.assertGreaterEqual(plan[0].finding_count, 1)
        self.assertTrue(analyses[0].agent_insights)

    def test_apply_writes_safe_python_refactor(self) -> None:
        case_dir = self.workspace / "apply-case"
        case_dir.mkdir(parents=True, exist_ok=True)
        target = case_dir / "sample.py"
        target.write_text(
            "def check(flag):    \n"
            "    if flag == True:\n"
            "        return flag != None\n",
            encoding="utf-8",
        )

        agent = RefactorAgent(
            AgentConfig(
                root=case_dir,
                write=True,
                artifact_dir=case_dir / "artifacts",
                emit_diff=True,
                emit_pr_report=True,
                exclude_dirs=(),
            )
        )
        _, _, result = agent.apply()

        updated = target.read_text(encoding="utf-8")
        self.assertEqual(len(result.verification_errors), 0)
        self.assertIn("if flag:", updated)
        self.assertIn("return flag is not None", updated)
        self.assertNotIn("== True", updated)
        self.assertTrue((case_dir / "artifacts" / "refactor.patch").exists())
        self.assertTrue((case_dir / "artifacts" / "pull_request.md").exists())

    def test_scan_supports_multiple_languages(self) -> None:
        case_dir = self.workspace / "multi-language"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "frontend.ts").write_text("const ready = flag === true;\n", encoding="utf-8")
        (case_dir / "Legacy.java").write_text("class Legacy { boolean f(boolean flag){ return flag == false; } }\n", encoding="utf-8")
        (case_dir / "service.go").write_text("package main\nfunc ok(flag bool) bool { return flag == true }\n", encoding="utf-8")

        agent = RefactorAgent(AgentConfig(root=case_dir, exclude_dirs=()))
        analyses, plan = agent.scan()

        self.assertEqual(len(analyses), 3)
        self.assertEqual(len(plan), 3)
        self.assertEqual(sorted(step.language for step in plan), ["go", "java", "typescript"])


if __name__ == "__main__":
    unittest.main()
