import tempfile
from pathlib import Path
import shutil
from zip_manager.zip_parser import add_to_zip, extract_from_zip, remove_from_zip, search_file, REGISTRY_SHELVE
import shelve
import zipfile

print('Starting smoke test...')
# create temp dir simulation
tmp = Path(tempfile.mkdtemp())
folder = tmp / "f"
folder.mkdir()
(a := folder / "a.txt").write_text("A")
(b := folder / "b.txt").write_text("B")
archive = tmp / "test.zip"
# Add files
add_to_zip(str(archive), "", str(folder), file_info={"book_name": "sample"})
# Check registry
with shelve.open(REGISTRY_SHELVE) as reg:
    assert str(archive) in reg
    entry = reg[str(archive)]
    members = entry.get('members', [])
    assert any('a.txt' in m for m in members) or any('b.txt' in m for m in members)
print('Registry contains archive and members OK')
# Search across registry
matches = search_file(REGISTRY_SHELVE, [("book_name","sample")])
print('search matches:', matches)
# Remove a member
with zipfile.ZipFile(archive, 'r') as zf:
    member = zf.namelist()[0]
remove_from_zip(str(archive), "", member)
with shelve.open(REGISTRY_SHELVE) as reg:
    entry2 = reg[str(archive)]
    assert member not in entry2.get('members', [])
print('Member removal reflected in registry')

# cleanup temporary files
shutil.rmtree(tmp)
print('smoke-test passed')