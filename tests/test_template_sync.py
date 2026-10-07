import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
import template_sync as sync
import setup_repo


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'template'
        self.source.mkdir()
        (self.source / 'templates').mkdir()
        for name in (*sync.HELPERS, *sync.INSTALLERS, 'template-version.txt'):
            shutil.copy2(SOURCE / name, self.source / name)
        shutil.copy2(SOURCE / 'templates/pixi.toml', self.source / 'templates/pixi.toml')
        shutil.copy2(SOURCE / 'templates/COSMOS-TOOLS.md', self.source / 'templates/COSMOS-TOOLS.md')
        self.target = self.root / 'Example With Spaces'
        self.target.mkdir()
        files, before, suffix = setup_repo.plan(self.target, '3.11')
        setup_repo.install_files(self.target, files, before, suffix)

    def change(self):
        with (self.source/'activate.sh').open('a') as f:
            f.write('\n# New template release\n')
        (self.source/'template-version.txt').write_text('1.2.0\n')

    def test_updates_helpers_and_state_preserves_project(self):
        self.change()
        (self.target/'PYTHON-ENVIRONMENT.md').write_text('Project-specific notes')
        protected = {n:(self.target/n).read_bytes() for n in ['pixi.toml','pixi.lock','PYTHON-ENVIRONMENT.md','.gitignore']}
        plan=sync.plan_update(self.source,self.target)
        before=(self.target/'activate.sh').read_bytes()
        backup=sync.apply_update(self.target,plan)
        self.assertEqual((backup/'activate.sh').read_bytes(),before)
        self.assertEqual((self.target/'activate.sh').read_bytes(),(self.source/'activate.sh').read_bytes())
        for n,data in protected.items(): self.assertEqual((self.target/n).read_bytes(),data)
        self.assertEqual(sync.plan_update(self.source,self.target),{})

    def test_conflict_changes_nothing(self):
        self.change()
        (self.target/'activate.sh').write_text('my custom helper')
        before=(self.target/sync.STATE).read_bytes()
        with self.assertRaisesRegex(ValueError,'Local changes conflict'):
            sync.plan_update(self.source,self.target)
        self.assertEqual((self.target/sync.STATE).read_bytes(),before)
        self.assertFalse((self.target/'.cache').exists())

    def test_missing_metadata_requires_adoption_and_matching_scripts(self):
        (self.target/sync.STATE).unlink()
        (self.target/'COSMOS-TOOLS.md').unlink()
        with self.assertRaisesRegex(ValueError,'--adopt'):
            sync.plan_update(self.source,self.target)
        sync.apply_update(self.target,sync.plan_update(self.source,self.target,True))
        self.assertTrue((self.target/sync.STATE).is_file())
        (self.target/sync.STATE).unlink()
        (self.target/'activate.sh').write_text('custom')
        with self.assertRaisesRegex(ValueError,'Cannot adopt'):
            sync.plan_update(self.source,self.target,True)

    def test_tool_version_migration_preserves_dependencies(self):
        p=self.source/'templates/pixi.toml'
        p.write_text(p.read_text().replace('==0.81.0','==0.82.0'))
        p=self.target/'pixi.toml'
        original=p.read_bytes()
        sync.apply_update(self.target,sync.plan_update(self.source,self.target))
        self.assertEqual(p.read_bytes(),original.replace(b'==0.81.0',b'==0.82.0'))
        p.write_bytes(original.replace(b'==0.81.0',b'>=0.80'))
        with self.assertRaisesRegex(ValueError,'locally customized'):
            sync.plan_update(self.source,self.target)

    def test_previous_release_receives_installers_without_dependency_changes(self):
        state=json.loads((self.target/sync.STATE).read_text())
        state['template_version']='1.1.0'
        for name in sync.INSTALLERS:
            del state['files'][name]
            (self.target/name).unlink()
        (self.target/sync.STATE).write_text(json.dumps(state))
        manifest=(self.target/'pixi.toml').read_bytes()
        lock=(self.target/'pixi.lock').read_bytes()
        plan=sync.plan_update(self.source,self.target)
        self.assertTrue(all(name in plan for name in sync.INSTALLERS))
        sync.apply_update(self.target,plan)
        self.assertEqual((self.target/'pixi.toml').read_bytes(),manifest)
        self.assertEqual((self.target/'pixi.lock').read_bytes(),lock)
        self.assertEqual(sync.plan_update(self.source,self.target),{})

    def test_symlink_refused(self):
        self.change()
        (self.target/'activate.sh').unlink()
        (self.target/'activate.sh').symlink_to(self.source/'activate.sh')
        with self.assertRaisesRegex(ValueError,'symlink'):
            sync.plan_update(self.source,self.target)

    def test_failure_restores_already_written_files(self):
        self.change()
        plan=sync.plan_update(self.source,self.target)
        before={n:(self.target/n).read_bytes() for n in plan}
        real=sync.atomic_write
        count=0
        def fail_second(*args):
            nonlocal count
            count+=1
            if count==2: raise OSError('simulated write failure')
            return real(*args)
        with patch.object(sync,'atomic_write',side_effect=fail_second):
            with self.assertRaises(OSError): sync.apply_update(self.target,plan)
        for n,data in before.items(): self.assertEqual((self.target/n).read_bytes(),data)

    def test_preview_and_batch_conflict_no_mutation(self):
        # CLI uses the real source; remove metadata to generate an adoption plan.
        (self.target/sync.STATE).unlink()
        result=subprocess.run([sys.executable,str(SOURCE/'update_repos.py'),str(self.target),'--adopt','--dry-run'],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse((self.target/sync.STATE).exists())
        bad=self.root/'bad'; bad.mkdir()
        result=subprocess.run([sys.executable,str(SOURCE/'update_repos.py'),str(self.target),str(bad),'--adopt'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.target/sync.STATE).exists())

    def test_backup_directory_symlink_refused(self):
        self.change()
        (self.target/'.cache').symlink_to(self.source,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Unsafe backup'):
            sync.apply_update(self.target,sync.plan_update(self.source,self.target))


if __name__=='__main__': unittest.main()
