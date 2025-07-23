import unittest
from unittest.mock import patch, MagicMock
import json
from scripts.lead_data_utils import get_lead_additional_data, update_lead_additional_data

class TestLeadDataUtils(unittest.TestCase):
    @patch('psycopg2.connect')
    def test_get_lead_additional_data_returns_json(self, mock_connect):
        # Mock do cursor e conexão
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [json.dumps({"foo": "bar", "x": 1})]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        result = get_lead_additional_data("5511999999999")
        self.assertEqual(result, {"foo": "bar", "x": 1})

    @patch('psycopg2.connect')
    def test_update_lead_additional_data_merge_and_update(self, mock_connect):
        # Simula additional_data existente
        existing_data = {"foo": "bar", "x": 1}
        # Nova informação a ser mesclada
        new_data = {"x": 2, "y": 3}
        # Esperado após merge
        expected_merged = {"foo": "bar", "x": 2, "y": 3}

        # Mock do cursor e conexão
        mock_cursor = MagicMock()
        # Primeira chamada: busca o additional_data atual
        mock_cursor.fetchone.return_value = [json.dumps(existing_data)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Chama a função
        result = update_lead_additional_data("5511999999999", new_data)
        self.assertTrue(result)
        # Verifica se o UPDATE foi chamado com o JSON mesclado
        merged_json = json.dumps(expected_merged)
        mock_cursor.execute.assert_any_call(
            "UPDATE leads SET additional_data = %s, updated_at = CURRENT_TIMESTAMP WHERE phone_number = %s",
            (merged_json, "5511999999999")
        )

    @patch('psycopg2.connect')
    def test_update_lead_additional_data_adds_new_key(self, mock_connect):
        # Simula additional_data existente
        existing_data = {"foo": "bar"}
        new_data = {"new_key": 123}
        expected_merged = {"foo": "bar", "new_key": 123}

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [json.dumps(existing_data)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        result = update_lead_additional_data("5511999999999", new_data)
        self.assertTrue(result)
        merged_json = json.dumps(expected_merged)
        mock_cursor.execute.assert_any_call(
            "UPDATE leads SET additional_data = %s, updated_at = CURRENT_TIMESTAMP WHERE phone_number = %s",
            (merged_json, "5511999999999")
        )

if __name__ == "__main__":
    unittest.main() 