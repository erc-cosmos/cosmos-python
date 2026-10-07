"""Filesystem integration checks; no network or target code execution."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
import shutil
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
spec = importlib.util.spec_from_file_location('setup_repo', SOURCE / 'setup_repo.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'My Research Repo'
        self.target.mkdir()

    def test_preserves_existing_files_and_merges_ignores(self):
        (self.target / 'README.md').write_text('Research notes\n')
        (self.target / 'pyproject.toml').write_text('[project]\nname="example"\n')
        (self.target / '.gitignore').write_bytes(b'data/\n.pixi/')
        files, before, suffix = setup.plan(self.target, '3.14')
        setup.install_files(self.target, files, before, suffix)
        self.assertEqual((self.target / 'README.md').read_text(), 'Research notes\n')
        self.assertIn('name = "my-research-repo"', (self.target / 'pixi.toml').read_text())
        self.assertEqual((self.target / 'pixi.lock').read_bytes(), (SOURCE / 'templates/pixi.lock').read_bytes())
        ignored = (self.target / '.gitignore').read_text()
        self.assertTrue(ignored.startswith('data/\n.pixi/\n'))
        self.assertEqual(ignored.count('.pixi/'), 1)
        with self.assertRaises(ValueError):
            setup.plan(self.target, '3.14')
        self.assertEqual((self.target / '.gitignore').read_text(), ignored)

    def test_preview_writes_nothing_and_custom_python_has_no_stale_lock(self):
        files, _, _ = setup.plan(self.target, '3.12')
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertNotIn('pixi.lock', files)
        self.assertIn(b'python = "3.12.*"', files['pixi.toml'])

    def test_existing_pixi_pyproject_rejected(self):
        (self.target / 'pyproject.toml').write_text('[tool.pixi.workspace]\nname="old"\n')
        with self.assertRaises(ValueError):
            setup.plan(self.target, '3.14')
        self.assertEqual(len(list(self.target.iterdir())), 1)

    def test_existing_file_and_symlink_rejected_without_changes(self):
        (self.target / 'cosmos.sh').symlink_to(self.target / 'nonexistent')
        with self.assertRaises(ValueError):
            setup.plan(self.target, '3.14')
        self.assertEqual(len(list(self.target.iterdir())), 1)

    def test_ignore_symlink_rejected(self):
        elsewhere = Path(self.temp.name) / 'ignore'
        elsewhere.write_text('keep\n')
        (self.target / '.gitignore').symlink_to(elsewhere)
        with self.assertRaises(ValueError):
            setup.plan(self.target, '3.14')
        self.assertEqual(elsewhere.read_text(), 'keep\n')

    def test_standalone_customizations_do_not_leak_into_projects(self):
        source = Path(self.temp.name) / 'custom standalone'
        source.mkdir()
        shutil.copytree(SOURCE / 'templates', source / 'templates')
        for name in (*setup.COPY_FILES, 'template-version.txt'):
            shutil.copy2(SOURCE / name, source / name)
        (source / 'pixi.toml').write_text('[workspace]\nname="personal"\nrequires-pixi="==99.0"\n[dependencies]\npython="3.12.*"\nnumpy="*"\n')
        (source / 'pixi.lock').write_text('personal lock')
        with patch.object(setup, 'SOURCE', source):
            files, _, _ = setup.plan(self.target, '3.14')
        manifest = files['pixi.toml'].decode()
        self.assertIn('python = "3.14.*"', manifest)
        self.assertNotIn('numpy="*"', manifest)
        self.assertEqual(files['pixi.lock'], (SOURCE / 'templates/pixi.lock').read_bytes())
        self.assertIn(b'"requires_pixi": "==0.81.0"', files['.cosmos-python.json'])
        self.assertIn('install.sh', files)
        self.assertIn('install.ps1', files)

    def test_missing_target_rejected(self):
        with self.assertRaises(ValueError):
            setup.plan(self.target / 'missing', '3.14')

    def test_creation_race_preserves_conflicting_file_and_rolls_back(self):
        files, before, suffix = setup.plan(self.target, '3.14')
        (self.target / 'cosmos.sh').write_text('created after preview')
        with self.assertRaises(FileExistsError):
            setup.install_files(self.target, files, before, suffix)
        self.assertEqual(list(self.target.iterdir()), [self.target / 'cosmos.sh'])
        self.assertEqual((self.target / 'cosmos.sh').read_text(), 'created after preview')


if __name__ == '__main__':
    unittest.main()
