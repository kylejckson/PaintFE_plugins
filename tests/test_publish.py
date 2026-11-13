import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
import publish
class PublishTests(unittest.TestCase):
 def listing(self,version='1.0.0',digest='same'):
  return dict(manifest=dict(id='pack',version=version),sha256=digest,published=100,updated=100,url='immutable')
 def test_unchanged_packs_retain_original_asset_and_dates(self):
  old=self.listing();new=self.listing();new['published']=999
  value=dict(packs=[new,self.listing()]);value['packs'][1]['manifest']['id']='new'
  fresh=publish.reconcile(value,dict(pack=old))
  self.assertIs(value['packs'][0],old);self.assertEqual(len(fresh),1)
 def test_changed_pack_retains_first_publication_date(self):
  old=self.listing();new=self.listing('1.0.1','different');new['published']=999;new['updated']=999
  publish.reconcile(dict(packs=[new]),dict(pack=old))
  self.assertEqual(new['published'],100);self.assertEqual(new['updated'],999)
 def test_same_version_cannot_replace_published_content(self):
  with self.assertRaises(AssertionError):publish.reconcile(dict(packs=[self.listing(digest='changed')]),dict(pack=self.listing()))
 def test_source_removal_can_withdraw_last_listing(self):
  self.assertEqual(publish.reconcile(dict(packs=[]),dict(pack=self.listing())),[])
 def test_unchanged_catalogue_requires_statistics_workflow(self):
  with self.assertRaises(AssertionError):publish.reconcile(dict(packs=[self.listing()]),dict(pack=self.listing()))
