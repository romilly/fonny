import pytest
from unittest.mock import patch, MagicMock
from serial import SerialException

from fonny.adapters.serial_adapter import SerialAdapter


class TestSerialAdapter:
    """Tests for the SerialAdapter class."""
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_connect_creates_serial_connection(self, mock_serial):
        """Test that connect creates a serial connection with the right parameters."""
        # Arrange
        adapter = SerialAdapter(port='/dev/test', baud_rate=9600, timeout=2)
        mock_serial.return_value = MagicMock()
        
        # Act
        result = adapter.connect()
        
        # Assert
        assert result is True
        mock_serial.assert_called_once_with(
            port='/dev/test',
            baudrate=9600,
            timeout=2
        )
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_connect_handles_exception(self, mock_serial):
        """Test that connect handles exceptions gracefully."""
        # Arrange
        adapter = SerialAdapter()
        mock_serial.side_effect = SerialException("Test exception")
        
        # Act
        result = adapter.connect()
        
        # Assert
        assert result is False
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_disconnect_closes_connection(self, mock_serial):
        """Test that disconnect closes the serial connection."""
        # Arrange
        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        adapter = SerialAdapter()
        adapter.connect()
        
        # Act
        adapter.disconnect()
        
        # Assert
        mock_serial_instance.close.assert_called_once()
        assert adapter._serial is None
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_is_connected_returns_true_when_connected(self, mock_serial):
        """Test that is_connected returns True when connected."""
        # Arrange
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial.return_value = mock_serial_instance
        adapter = SerialAdapter()
        adapter.connect()
        
        # Act & Assert
        assert adapter.is_connected() is True
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_is_connected_returns_false_when_not_connected(self, mock_serial):
        """Test that is_connected returns False when not connected."""
        # Arrange
        adapter = SerialAdapter()
        
        # Act & Assert
        assert adapter.is_connected() is False
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_send_command_writes_to_serial(self, mock_serial):
        """Test that send_command writes to the serial connection."""
        # Arrange
        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        adapter = SerialAdapter()
        adapter.connect()
        
        # Act
        adapter.send_command("test command")
        
        # Assert
        mock_serial_instance.write.assert_called_once_with(b"test command")
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_send_command_raises_error_when_not_connected(self, mock_serial):
        """Test that send_command raises an error when not connected."""
        # Arrange
        adapter = SerialAdapter()
        
        # Act & Assert
        with pytest.raises(ConnectionError):
            adapter.send_command("test command")
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_receive_response_reads_from_serial(self, mock_serial):
        """Test that receive_response reads from the serial connection."""
        # Arrange
        mock_serial_instance = MagicMock()
        mock_serial_instance.in_waiting = True
        mock_serial_instance.readline.return_value = b"test response"
        mock_serial.return_value = mock_serial_instance
        adapter = SerialAdapter()
        adapter.connect()
        
        # Act
        response = adapter.receive_response()
        
        # Assert
        assert response == "test response"
        mock_serial_instance.readline.assert_called_once()
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_receive_response_returns_none_when_no_data(self, mock_serial):
        """Test that receive_response returns None when no data is available."""
        # Arrange
        mock_serial_instance = MagicMock()
        mock_serial_instance.in_waiting = False
        mock_serial.return_value = mock_serial_instance
        adapter = SerialAdapter()
        adapter.connect()
        
        # Act
        response = adapter.receive_response()
        
        # Assert
        assert response is None
        mock_serial_instance.readline.assert_not_called()
    
    @patch('fonny.adapters.serial_adapter.serial.Serial')
    def test_receive_response_raises_error_when_not_connected(self, mock_serial):
        """Test that receive_response raises an error when not connected."""
        # Arrange
        adapter = SerialAdapter()
        
        # Act & Assert
        with pytest.raises(ConnectionError):
            adapter.receive_response()
