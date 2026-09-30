"""Exercise command wiring without running TRELLIS, Blender or any STL."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import make_award


class OrchestratorTests(unittest.TestCase):
    def test_dry_run_describes_full_pipeline_without_running_it(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            image = root / "image.png"
            image.write_bytes(b"test fixture; not decoded in dry run")
            trellis = root / "TRELLIS"
            trellis.mkdir()
            out = root / "output"
            printed = StringIO()
            with patch.object(make_award.subprocess, "run") as subprocess_run:
                with redirect_stdout(printed):
                    result = make_award.main([
                        "--image", str(image), "--name", "Alex", "--message", "Well|Done",
                        "--trellis-root", str(trellis), "--out", str(out), "--dry-run",
                    ])
            self.assertEqual(result, 0)
            subprocess_run.assert_not_called()
            self.assertFalse(out.exists())
            commands = printed.getvalue()
            for stage in ("trellis_generate.py", "weld_plug.py", "build_base_named.py",
                          "inspect_stl.py", "render_views.py"):
                self.assertIn(stage, commands)
            self.assertIn("PYTHONPATH=" + str(trellis.resolve()), commands)
            self.assertEqual(commands.count("inspect_stl.py"), 2)
            self.assertEqual(commands.count("render_views.py"), 2)


if __name__ == "__main__":
    unittest.main()
