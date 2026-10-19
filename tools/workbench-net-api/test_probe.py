import json
import struct
import unittest
from unittest.mock import patch
import probe


class FragmentedSocket:
    def __init__(self, data):
        self.data = data
    def recv(self, size):
        chunk = self.data[:min(size, 2)]
        self.data = self.data[len(chunk):]
        return chunk


class ProbeTests(unittest.TestCase):
    def test_empty_entities_rejected(self):
        with self.assertRaises(ValueError):
            probe.validate_payload({"endpoint": probe.EXPECTED_VERSION, "selectedCount": 1, "entities": [{}]})

    def test_structured_entity_accepted(self):
        probe.validate_payload({"endpoint": probe.EXPECTED_VERSION, "selectedCount": 1, "entities": [
            {"firstSelectedName": "MP133", "fields": [
                {"path": "component[4]", "field": "capacity", "valueType": "int", "status": "ok", "value": "0"}]}]})

    def test_zero_selection(self):
        probe.validate_payload({"endpoint": probe.EXPECTED_VERSION, "selectedCount": 0})
    def test_utf8_frame(self):
        wire = probe.frame("дробь")
        self.assertEqual(struct.unpack("<I", wire[:4])[0], len("дробь".encode()))
        self.assertEqual(probe.receive_string(FragmentedSocket(wire)), "дробь")

    def test_incomplete(self):
        with self.assertRaises(EOFError):
            probe.receive_string(FragmentedSocket(b"\x01"))

    def test_oversize(self):
        with self.assertRaises(ValueError):
            probe.receive_string(FragmentedSocket(struct.pack("<I", probe.MAX_FRAME + 1)))

    def test_mutation_forbidden(self):
        with self.assertRaises(ValueError):
            probe.call(5775, "OpenResource")

    def test_transport_stops_sequence(self):
        with patch("sys.argv", ["probe", "--custom"]), patch("probe.call", side_effect=TimeoutError()), patch("builtins.print"), patch("probe.call", side_effect=TimeoutError()) as request:
            self.assertEqual(probe.main(), 1)
            self.assertEqual(request.call_count, 1)

    def test_stale_handler_rejected(self):
        def response(port, endpoint, nonce=None):
            payload = {"endpoint": "WAX_ReadOnlyNetApi/v4", "nonce": nonce}
            return {"endpoint": endpoint, "error_code": "Ok", "payload": payload}
        with patch("sys.argv", ["probe", "--custom"]), patch("probe.call", side_effect=response), patch("builtins.print"):
            self.assertEqual(probe.main(), 1)


if __name__ == "__main__":
    unittest.main()
