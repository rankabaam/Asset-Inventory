import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from inventory import classify_assets, dashboard, load_table

ROOT = Path(__file__).resolve().parents[1]

class InventoryTests(unittest.TestCase):
    def data(self):
        a = load_table(ROOT / 'sample_data/assets.csv', ('asset_id', 'category', 'custodian', 'state'))
        o = load_table(ROOT / 'sample_data/observations.csv', ('asset_id', 'observed_on', 'result'))
        return a,o

    def test_each_status(self):
        a,o=self.data()
        statuses={r['asset_id']:r['status'] for r in classify_assets(a,o,'2026-10-18')}
        self.assertEqual(statuses['LAB-A01'],'Verified')
        self.assertEqual(statuses['LAB-A02'],'Review')
        self.assertEqual(statuses['LAB-A03'],'Outdated')
        self.assertEqual(statuses['LAB-A04'],'Unknown')
        self.assertEqual(statuses['LAB-A05'],'Archived')

    def test_unknown_is_not_missing(self):
        a,o=self.data()
        self.assertNotIn('Missing', {r['status'] for r in classify_assets(a,o,'2026-10-18')})

    def test_duplicate_ids_are_rejected(self):
        a,o=self.data()
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            classify_assets(a+[a[0]],o,'2026-10-18')

    def test_unknown_observation_is_rejected(self):
        a,o=self.data()
        o.append({'asset_id':'NONEXISTENT','observed_on':'2026-10-18','result':'Pass'})
        with self.assertRaisesRegex(ValueError,'unknown asset'):
            classify_assets(a,o,'2026-10-18')

    def test_dashboard_escapes_content(self):
        a,o=self.data()
        rows=classify_assets(a,o,'2026-10-18')
        rows[0]['category']='<img src=x>'
        html=dashboard(rows,'2026-10-18')
        self.assertIn('&lt;img',html)
        self.assertNotIn('<img src=x>',html)

if __name__=='__main__':unittest.main()
