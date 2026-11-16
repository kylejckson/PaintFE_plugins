import json, zipfile, struct, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'plugins/kylejckson'

class ThemeCollection(unittest.TestCase):
    def test_collection_identity(self):
        manifests = [json.loads(p.read_text()) for p in ROOT.glob('*/manifest.json')]
        self.assertEqual(len(manifests), 11)
        self.assertEqual(sum(m['kind'] == 'theme' for m in manifests), 10)
        self.assertEqual(sum(m['kind'] == 'icons' for m in manifests), 1)
        self.assertEqual({m['author'] for m in manifests}, {'kylejckson'})
        self.assertEqual(len({m['id'] for m in manifests}), 11)

    def test_palettes_and_permissions(self):
        for p in ROOT.glob('*/theme.txt'):
            data = dict(line.split('=', 1) for line in p.read_text().splitlines() if '=' in line and not line.startswith('#'))
            self.assertEqual(len([key for key in data if key.startswith('ov_')]), 29, p.parent.name)
            self.assertFalse(any(key in data for key in ['automation', 'onnx_runtime_path', 'icon_pack_path', 'workspace', 'keybindings']))
            material = json.loads(data['glass'])
            self.assertTrue(0 <= material['grain'] <= 1)
            self.assertEqual(material['enabled'], 'Glass' in json.loads((p.parent/'manifest.json').read_text())['tags'])
            if not material['enabled']:
                def lum(c):
                    return sum(weight*(x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4) for weight, x in zip([.2126,.7152,.0722], [n/255 for n in c]))
                a,b = sorted(lum(list(map(int, data[key].split(',')[:3]))) for key in ['ov_bg_color','ov_text_color'])
                self.assertGreaterEqual((b+.05)/(a+.05), 4.5, p.parent.name)

    def test_complete_paired_icons_and_bounds(self):
        with zipfile.ZipFile(ROOT/'retro-98-icons/icons.zip') as z:
            ids = z.read('icons.txt').decode().splitlines()
            self.assertGreaterEqual(len(ids), 180)
            self.assertEqual(len(ids), len(set(ids)))
            self.assertLessEqual(len(z.namelist()), 1024)
            decoded = 0
            for name in ids:
                for mode in ['light','dark']:
                    png = z.read(name+'_'+mode+'.png')
                    self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
                    width,height = struct.unpack('>II', png[16:24])
                    self.assertEqual(png[25], 6)
                    self.assertEqual(height, 48)
                    self.assertEqual(width, 88 if name == 'tool_shapes' else 48)
                    decoded += width*height*4
            self.assertLess(decoded, 64*1024*1024)

    def test_toggle_and_settings_glyphs_differ(self):
        with zipfile.ZipFile(ROOT/'retro-98-icons/icons.zip') as z:
            for a,b in [('toolbar_grid_on','toolbar_grid_off'),('toolbar_guides_on','toolbar_guides_off'),('toolbar_wrap_preview_on','toolbar_wrap_preview_off'),('toolbar_mirror_h','toolbar_mirror_v'),('tool_brush','tool_smudge')]:
                self.assertNotEqual(z.read(a+'_light.png'), z.read(b+'_light.png'))
            names = ['settings_main','settings_interface','settings_hardware','settings_keybinds','settings_a_i','settings_plugins','settings_optional_features']
            self.assertEqual(len({z.read(name+'_light.png') for name in names}), len(names))

if __name__ == '__main__':
    unittest.main()
