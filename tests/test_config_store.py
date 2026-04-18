import json
import tempfile
import unittest
from pathlib import Path

from skybot.config_manager import ConfigStore


class ConfigStoreTests(unittest.TestCase):
    def test_updates_and_persists_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            store = ConfigStore(config_path)

            store.update("logging_channel_id", 1234)
            store.update("automod_enabled", True)
            store.update("mute_duration_default", 45)
            store.add_to_list("admin_role_ids", 999)

            reloaded = ConfigStore(config_path)
            config = reloaded.get_all()

            self.assertEqual(config["logging_channel_id"], 1234)
            self.assertTrue(config["automod_enabled"])
            self.assertEqual(config["mute_duration_default"], 45)
            self.assertEqual(config["admin_role_ids"], [999])

            on_disk = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(on_disk, config)

    def test_invalid_keys_raise_key_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "config.json")

            with self.assertRaises(KeyError):
                store.update("unknown_key", 1)

            with self.assertRaises(KeyError):
                store.add_to_list("logging_channel_id", 1)

            with self.assertRaises(KeyError):
                store.add_to_list("completely_unknown_key", 1)

            with self.assertRaises(KeyError):
                store.get("invalid_key")


if __name__ == "__main__":
    unittest.main()
