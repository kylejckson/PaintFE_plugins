import importlib.util, unittest, tempfile, json
from pathlib import Path
spec=importlib.util.spec_from_file_location('catalogue',Path(__file__).parents[1]/'tools/catalogue.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class CatalogueTests(unittest.TestCase):
 def asset(self,id=1,count=0,pack='pack',created=1000):return dict(id=id,download_count=count,pack=pack,created=created)
 def test_day_one_has_real_counts(self):
  state,counts=c.update_metrics({},[self.asset(count=12)],2000)
  self.assertEqual(counts['pack']['downloads'],12);self.assertEqual(counts['pack']['recent_downloads'],12)
 def test_seven_day_window(self):
  state,_=c.update_metrics({},[self.asset(count=10)],2000)
  state,counts=c.update_metrics(state,[self.asset(count=17)],2000+7*86400)
  self.assertEqual(counts['pack']['recent_downloads'],7)
 def test_new_version_keeps_old_downloads(self):
  state,_=c.update_metrics({},[self.asset(count=12)],2000)
  _,counts=c.update_metrics(state,[self.asset(id=2,count=4,created=3000)],4000)
  self.assertEqual(counts['pack']['downloads'],16)
 def test_counter_reset_is_monotonic(self):
  state,_=c.update_metrics({},[self.asset(count=12)],2000)
  _,counts=c.update_metrics(state,[self.asset(count=2)],3000)
  self.assertEqual(counts['pack']['downloads'],14)
 def test_missing_history_is_not_invented(self):
  _,counts=c.update_metrics({},[self.asset(count=100,created=1)],10*86400)
  self.assertEqual(counts['pack']['recent_downloads'],0)
 def test_old_unavailable_asset_not_trending(self):
  state,_=c.update_metrics({},[self.asset(count=12)],2000)
  _,counts=c.update_metrics(state,[],2000+10*86400)
  self.assertEqual(counts['pack']['recent_downloads'],0)
 def test_samples_are_bounded(self):
  state={}
  for day in range(90):state,_=c.update_metrics(state,[self.asset(count=day)],2000+day*86400)
  self.assertLessEqual(len(state['assets']['1']['samples']),10)
 def test_paths(self):
  for name in ['../x','/x','a\\x','a//x','a/./b','C:/x']:self.assertFalse(c.resource(name),name)
  self.assertTrue(c.resource('effects/test.rhai'))
 def test_source_schema_is_valid_json(self):
  schema=json.loads((c.ROOT/'schemas/manifest.schema.json').read_text())
  self.assertEqual(schema['properties']['api']['const'],1)
  self.assertTrue(c.re.fullmatch(schema['properties']['version']['pattern'],'1.0.0'))
 def test_duplicate_json_keys_are_rejected(self):
  with self.assertRaises(AssertionError):json.loads('{"id":1,"id":2}',object_pairs_hook=c.unique)
 def test_parameter_types(self):
  for p in [dict(id='x',label='X',kind='number',default=2,min=0,max=1),dict(id='x',label='X',kind='boolean',default=1)]:
   with self.assertRaises(AssertionError):c.check_parameter(p)
 def test_examples_validate_and_package_deterministically(self):
  key=c.Ed25519PrivateKey.from_private_bytes(bytes([7])*32)
  for path in c.sources():
   m,files=c.source_manifest(path.parent);a=c.package(m,files,key);self.assertEqual(a,c.package(m,files,key))
   envelope=json.loads(c.zipfile.ZipFile(c.io.BytesIO(a)).read('manifest.json'));key.public_key().verify(bytes.fromhex(envelope['signature']),envelope['payload'].encode())
if __name__=='__main__':unittest.main()

class NumericBoundsTests(unittest.TestCase):
 def test_integer_bounds_match_native_controls(self):
  for lo,hi,step in [(0.25,10,1),(0,10,.5),(0,2**64,1)]:
   with self.assertRaises(AssertionError):c.check_parameter(dict(id='count',label='Count',kind='integer',default=1,min=lo,max=hi,step=step))
 def test_group_heading_is_bounded(self):
  with self.assertRaises(AssertionError):c.check_parameter(dict(id='value',label='Value',kind='number',default=0,group='x'*81))
