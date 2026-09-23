"""Tests for scripts/sync_from_brain.py. Standard library only.

Run from the repository root:
    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sync_from_brain as sync  # noqa: E402

PUBLIC = {
    "role": "### Acme - Security Engineer\n\n*Jan. 2025-present*\n\n- Builds and secures public things.",
    "projects": "- **[Tool](https://github.com/example/tool)** - A public tool. It reads `/proc` without root.",
    "education": "- **Some Degree**, Some University - completed 2024",
    "community": "I am a member of a public programme.",
    "talks": (
        "### Upcoming\n\n"
        "- **ConfA, City, Oct. 2, 2026:** a public talk\n\n"
        "### Past talks and research\n\n"
        "- **[ConfB](https://example.org/talks/1), May 2026:** *A public title*"
    ),
}

# Private material that sits in the same files, outside the public blocks.
PRIVATE_NOTES = [
    "Target salary USD 6,000 per month, floor USD 5,000",
    "/home/valen/Desktop/Personal/CV Valentin Torassa/Valentin_ATS_CV_ES.pdf",
    "recruiter.contact@example.com",
    "Inscripción de un autor antes del 3 Oct o no se publican",
    "ghp_" + "a" * 36,
    "Do not publish: client name Initech",
]

UNLISTED_SECRET = "LEAKED-FROM-AN-UNLISTED-FILE"


def private_section() -> str:
    return "\n".join(f"- {note}" for note in PRIVATE_NOTES)


def write_brain(root: Path, public: dict[str, str] | None = None) -> Path:
    """A fake Brain: whitelisted files mix private notes with public blocks."""
    public = dict(PUBLIC if public is None else public)
    by_file: dict[str, list[str]] = {}
    for section, rel in sync.SOURCES.items():
        by_file.setdefault(rel, []).append(section)
    for rel, sections in by_file.items():
        parts = [f"# {rel}", "", "## Private notes", "", private_section(), ""]
        for section in sections:
            if section in public:
                parts += [
                    f"<!-- public-readme:{section}:start -->",
                    public[section],
                    f"<!-- public-readme:{section}:end -->",
                    "",
                ]
        parts += ["## More private notes", "", private_section(), ""]
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(parts), encoding="utf-8")
    # A file outside the whitelist that even carries a well-formed public block.
    unlisted = root / "audits" / "private-plan.md"
    unlisted.parent.mkdir(parents=True, exist_ok=True)
    unlisted.write_text(
        "<!-- public-readme:talks:start -->\n"
        f"- {UNLISTED_SECRET}\n"
        "<!-- public-readme:talks:end -->\n",
        encoding="utf-8",
    )
    return root


README_HEAD = "<h1>Name \u2014 hand-written, outside the markers</h1>\n\nIntro with trailing spaces   \n\n## Role\n\n"
README_TAIL = "\n\n<h2>Find me online</h2>\n\nRosario \u00b7 UTC\u22123"


def readme_text(contents: dict[str, str] | None = None) -> str:
    contents = contents or {section: f"old {section} text" for section in sync.SOURCES}
    middle = "\n\n## Between sections\n\n".join(
        f"<!-- brain:{section}:start -->\n{contents[section]}\n<!-- brain:{section}:end -->"
        for section in sync.SOURCES
    )
    return README_HEAD + middle + README_TAIL


def run(*args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
        code = sync.main(list(args))
    return code, out.getvalue(), err.getvalue()


class TempRepo(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.brain = write_brain(self.tmp / "brain")
        self.readme = self.tmp / "README.md"
        self.readme.write_bytes(readme_text().encode("utf-8"))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def sync(self, *extra: str) -> tuple[int, str, str]:
        return run(str(self.brain), "--readme", str(self.readme), "--today", "2026-09-01", *extra)


class PrivacyGuardTest(TempRepo):
    def test_private_content_in_whitelisted_files_does_not_leak(self) -> None:
        code, out, err = self.sync()
        self.assertEqual(code, 0, err)
        result = self.readme.read_text(encoding="utf-8")
        for section, text in PUBLIC.items():
            self.assertIn(text, result, section)
        for note in PRIVATE_NOTES + [UNLISTED_SECRET, "Private notes"]:
            self.assertNotIn(note, result)

    def test_logs_never_quote_brain_content(self) -> None:
        code, out, err = self.sync()
        self.assertEqual(code, 0, err)
        logs = out + err
        for note in PRIVATE_NOTES + [UNLISTED_SECRET]:
            self.assertNotIn(note, logs)
        for text in PUBLIC.values():
            for line in filter(None, text.split("\n")):
                self.assertNotIn(line, logs)

    def test_only_whitelisted_files_are_read(self) -> None:
        brain_root = self.brain.resolve()
        opened: list[str] = []
        real_read_bytes = Path.read_bytes

        def recording(path: Path) -> bytes:
            resolved = Path(path).resolve()
            if resolved.is_relative_to(brain_root):
                opened.append(resolved.relative_to(brain_root).as_posix())
            return real_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", autospec=True, side_effect=recording):
            code, _, err = self.sync()
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(set(opened)), sorted(set(sync.SOURCES.values())))

    def test_unmapped_block_in_a_whitelisted_file_is_ignored(self) -> None:
        path = self.brain / "cv" / "profile.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n<!-- public-readme:salary:start -->\nUSD 6,000 target\n<!-- public-readme:salary:end -->\n",
            encoding="utf-8",
        )
        code, out, err = self.sync()
        self.assertEqual(code, 0, err)
        self.assertIn("'salary'", err)
        self.assertNotIn("USD 6,000", err + out + self.readme.read_text(encoding="utf-8"))

    def test_private_content_inside_a_public_block_is_refused(self) -> None:
        samples = {
            "local-path": "/home/valen/Desktop/Investigacion/paper.pdf",
            "local-path-mac": "/Users/valen/Documents/notes.md",
            "local-path-home": "see ~/Documents/plan.md",
            "local-path-windows": "C:\\Users\\valen\\cv.docx",
            "email": "reach me at someone.private@example.com",
            "github-token": "ghp_" + "b" * 36,
            "aws-key": "AKIAABCDEFGHIJKLMNOP",
            "private-key": "-----BEGIN OPENSSH PRIVATE KEY-----",
            "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2YWxlbiJ9.signature",
            "password": "password: hunter2",
            "http-link": "[site](http://example.com/)",
            "ip-link": "https://192.168.1.10/admin",
            "local-host": "https://valensrv.local/status",
            "bare-host": "https://nas:8080/files",
            "tailnet": "https://box.tail1234.ts.net/",
            "userinfo": "https://user:pass@example.com/",
            "relative-link": "[plan](../audits/2026-09-17-career-plan/README.md)",
            "html-href": '<a href="/private/notes">notes</a>',
            "html-comment": "<!-- hidden from the rendered page -->",
            "phone": "+54 9 341 555-1234",
            "id-number": "DNI 12345678",
            "do-not-publish": "No publicar hasta que confirmen",
        }
        original = self.readme.read_bytes()
        for name, sample in samples.items():
            with self.subTest(name):
                public = dict(PUBLIC)
                public["projects"] = PUBLIC["projects"] + f"\n- extra line {sample}"
                write_brain(self.brain, public)
                code, out, err = self.sync()
                self.assertEqual(code, 2, f"{name}: {err}")
                self.assertIn("section 'projects'", err)
                self.assertNotIn(sample, out + err)
                self.assertEqual(self.readme.read_bytes(), original)

    def test_public_links_with_long_ids_are_allowed(self) -> None:
        public = dict(PUBLIC)
        public["projects"] = (
            "- **[Post](https://www.linkedin.com/feed/update/urn:li:activity:7234567890123456789/)** - a public post\n"
            "- **[Channel](https://www.youtube.com/@vtcibersecurity)** - a public channel"
        )
        write_brain(self.brain, public)
        code, _, err = self.sync()
        self.assertEqual(code, 0, err)

    def test_symlinked_source_is_refused(self) -> None:
        target = self.brain / "cv" / "cv-facts.md"
        target.unlink()
        target.symlink_to(self.brain / "audits" / "private-plan.md")
        code, out, err = self.sync()
        self.assertEqual(code, 2)
        self.assertIn("symlink", err)
        self.assertNotIn(UNLISTED_SECRET, out + err + self.readme.read_text(encoding="utf-8"))

    def test_symlinked_directory_is_refused(self) -> None:
        real = self.brain / "publications"
        real.rename(self.brain / "elsewhere")
        real.symlink_to(self.brain / "elsewhere", target_is_directory=True)
        code, _, err = self.sync()
        self.assertEqual(code, 2)
        self.assertIn("symlink", err)

    def test_whitelist_holds_plain_relative_paths(self) -> None:
        for rel in sync.SOURCES.values():
            path = Path(rel)
            self.assertFalse(path.is_absolute(), rel)
            self.assertNotIn("..", path.parts, rel)
            self.assertTrue(rel.endswith(".md"), rel)


class StyleTest(TempRepo):
    def test_dashes_and_invisible_characters_are_normalized(self) -> None:
        public = dict(PUBLIC)
        public["role"] = (
            "### Acme \u2014 Security Engineer\n\n*Jan. 2025\u2013present*   \n\n"
            "- UTC\u22123,\u00a0non\u2011breaking,\u200b zero\u2060width"
        )
        write_brain(self.brain, public)
        code, _, err = self.sync()
        self.assertEqual(code, 0, err)
        result = self.readme.read_text(encoding="utf-8")
        self.assertIn(
            "### Acme - Security Engineer\n\n*Jan. 2025-present*\n\n- UTC-3, non-breaking, zerowidth", result
        )

    def test_blank_edges_are_trimmed(self) -> None:
        self.assertEqual(sync.apply_style("\n\n  \n- a  \n\n- b\n\n"), "- a\n\n- b")

    def test_empty_block_is_refused(self) -> None:
        public = dict(PUBLIC)
        public["community"] = "   \n"
        write_brain(self.brain, public)
        code, _, err = self.sync()
        self.assertEqual(code, 2)
        self.assertIn("empty", err)


class RenderTest(TempRepo):
    def test_text_outside_the_markers_stays_byte_identical(self) -> None:
        before = self.readme.read_bytes()
        code, _, err = self.sync()
        self.assertEqual(code, 0, err)
        after = self.readme.read_bytes()
        self.assertNotEqual(before, after)
        head, tail = README_HEAD.encode("utf-8"), README_TAIL.encode("utf-8")
        self.assertTrue(before.startswith(head) and after.startswith(head))
        self.assertTrue(before.endswith(tail) and after.endswith(tail))
        # Every line that is not a block body is unchanged, marker lines included.
        self.assertEqual(_outside_blocks(before), _outside_blocks(after))

    def test_check_reports_without_writing(self) -> None:
        before = self.readme.read_bytes()
        code, out, err = self.sync("--check")
        self.assertEqual(code, 1)
        self.assertIn("would update", out)
        self.assertIn("out of date", err)
        self.assertEqual(self.readme.read_bytes(), before)

    def test_sync_is_idempotent(self) -> None:
        self.assertEqual(self.sync()[0], 0)
        once = self.readme.read_bytes()
        code, out, _ = self.sync("--check")
        self.assertEqual(code, 0)
        self.assertIn("in sync with the Brain", out)
        self.assertEqual(self.sync()[0], 0)
        self.assertEqual(self.readme.read_bytes(), once)

    def test_only_changed_sections_are_reported(self) -> None:
        self.readme.write_bytes(readme_text({**PUBLIC, "talks": "stale talks"}).encode("utf-8"))
        code, out, _ = self.sync("--check")
        self.assertEqual(code, 1)
        self.assertIn("talks: would update", out)
        for section in ("role", "projects", "education", "community"):
            self.assertIn(f"{section}: in sync", out)

    def test_missing_brain_block_fails_without_writing(self) -> None:
        public = dict(PUBLIC)
        del public["education"]
        write_brain(self.brain, public)
        before = self.readme.read_bytes()
        code, _, err = self.sync()
        self.assertEqual(code, 2)
        self.assertIn("'education'", err)
        self.assertEqual(self.readme.read_bytes(), before)

    def test_bad_readme_markers_fail_without_writing(self) -> None:
        good = readme_text()
        cases = {
            "missing": good.replace("<!-- brain:talks:start -->\n", "").replace("\n<!-- brain:talks:end -->", ""),
            "unknown": good + "\n<!-- brain:salary:start -->\nx\n<!-- brain:salary:end -->\n",
            "duplicate": good + "\n<!-- brain:role:start -->\nx\n<!-- brain:role:end -->\n",
            "unclosed": good.replace("\n<!-- brain:role:end -->", ""),
            "nested": good.replace(
                "<!-- brain:role:start -->", "<!-- brain:role:start -->\n<!-- brain:projects:start -->", 1
            ),
        }
        for name, text in cases.items():
            with self.subTest(name):
                self.readme.write_bytes(text.encode("utf-8"))
                code, _, err = self.sync()
                self.assertEqual(code, 2, name)
                self.assertTrue(err.startswith("error: README.md"), err)
                self.assertEqual(self.readme.read_bytes(), text.encode("utf-8"))

    def test_missing_brain_directory_fails(self) -> None:
        code, _, err = run(str(self.tmp / "nowhere"), "--readme", str(self.readme))
        self.assertEqual(code, 2)
        self.assertIn("does not exist", err)

    def test_list_sources_prints_the_whitelist(self) -> None:
        code, out, _ = run("--list-sources")
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), sorted(set(sync.SOURCES.values())))


def _outside_blocks(data: bytes) -> list[str]:
    """The README lines that are not inside a brain block body, markers included."""
    kept, inside = [], False
    for line in data.decode("utf-8").split("\n"):
        match = sync.README_MARKER.fullmatch(line.strip())
        if match:
            inside = match.group(2) == "start"
            kept.append(line)
        elif not inside:
            kept.append(line)
    return kept


class StaleTalkTest(unittest.TestCase):
    TALKS = (
        "### Upcoming\n\n"
        "- **First Conf, City, Sep. 28, 2026:** talk\n"
        "- **Second Conf, City, Oct. 5-9, 2026:** papers\n\n"
        "### Past talks and research\n\n"
        "- **Old Conf, July 24, 2026:** *Title*"
    )

    def test_warns_only_for_upcoming_items_that_ended(self) -> None:
        warnings = sync.stale_upcoming(self.TALKS, dt.date(2026, 10, 6))
        self.assertEqual(len(warnings), 1)
        self.assertIn("upcoming item 1 ended on 2026-09-28", warnings[0])
        self.assertNotIn("First Conf", warnings[0])

    def test_last_day_of_a_range_counts(self) -> None:
        self.assertEqual(len(sync.stale_upcoming(self.TALKS, dt.date(2026, 10, 9))), 1)
        self.assertEqual(len(sync.stale_upcoming(self.TALKS, dt.date(2026, 10, 10))), 2)

    def test_nothing_stale_before_the_dates(self) -> None:
        self.assertEqual(sync.stale_upcoming(self.TALKS, dt.date(2026, 9, 23)), [])


class RepositoryReadmeTest(unittest.TestCase):
    """Checks on the real README.md, which the workflow also runs."""

    def setUp(self) -> None:
        self.text = sync.DEFAULT_README.read_text(encoding="utf-8")

    def test_every_section_has_markers(self) -> None:
        spans = sync.find_blocks(self.text, sync.README_MARKER, "README.md")
        self.assertEqual(set(spans), set(sync.SOURCES))

    def test_whole_readme_follows_the_style_rules(self) -> None:
        self.assertEqual(sync.style_violations(self.text), [])
        self.assertNotIn("\r", self.text)
        for number, line in enumerate(self.text.split("\n"), 1):
            self.assertEqual(line, line.rstrip(), f"trailing whitespace on line {number}")

    def test_current_sections_pass_the_checks_unchanged(self) -> None:
        lines = self.text.split("\n")
        for section, (start, end) in sync.find_blocks(self.text, sync.README_MARKER, "README.md").items():
            body = "\n".join(lines[start + 1 : end])
            with self.subTest(section):
                self.assertEqual(sync.enforce(section, body), body)


if __name__ == "__main__":
    unittest.main()
