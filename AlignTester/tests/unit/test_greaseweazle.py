"""
Tests unitaires pour greaseweazle.py
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from api.greaseweazle import GreaseweazleExecutor


@pytest.mark.asyncio
class TestGreaseweazleExecutor:
    """Tests pour GreaseweazleExecutor"""
    
    def test_init_default_path(self):
        """Test initialisation avec chemin par défaut"""
        executor = GreaseweazleExecutor()
        
        assert executor.gw_path is not None
        assert executor.platform is not None
    
    def test_init_custom_path(self):
        """Test initialisation avec chemin personnalisé"""
        executor = GreaseweazleExecutor(gw_path="/custom/path/gw")
        
        assert executor.gw_path == "/custom/path/gw"
    
    @patch('subprocess.run')
    def test_check_version_success(self, mock_run):
        """Test vérification de version - succès"""
        mock_run.return_value = Mock(returncode=0, stdout="Greaseweazle 1.0.0\n")
        
        executor = GreaseweazleExecutor(gw_path="gw")
        version = executor.check_version()
        
        assert version == "Greaseweazle 1.0.0"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_check_version_failure(self, mock_run):
        """Test vérification de version - échec"""
        mock_run.return_value = Mock(returncode=1, stdout="")
        
        executor = GreaseweazleExecutor(gw_path="gw")
        version = executor.check_version()
        
        assert version is None
    
    @patch('subprocess.run')
    def test_check_version_exception(self, mock_run):
        """Test vérification de version - exception"""
        mock_run.side_effect = Exception("Command not found")
        
        executor = GreaseweazleExecutor(gw_path="gw")
        version = executor.check_version()
        
        assert version is None
    
    @patch('subprocess.run')
    def test_check_align_available_true(self, mock_run):
        """Test vérification disponibilité align - disponible"""
        mock_run.return_value = Mock(returncode=0)
        
        executor = GreaseweazleExecutor(gw_path="gw")
        available = executor.check_align_available()
        
        assert available is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "align" in args
        assert "--help" in args
    
    @patch('subprocess.run')
    def test_check_align_available_false(self, mock_run):
        """Test vérification disponibilité align - non disponible"""
        mock_run.return_value = Mock(returncode=1)
        
        executor = GreaseweazleExecutor(gw_path="gw")
        available = executor.check_align_available()
        
        assert available is False
    
    @patch('subprocess.run')
    def test_check_align_available_exception(self, mock_run):
        """Test vérification disponibilité align - exception"""
        mock_run.side_effect = Exception("Command not found")
        
        executor = GreaseweazleExecutor(gw_path="gw")
        available = executor.check_align_available()
        
        assert available is False
    
    @patch('asyncio.create_subprocess_exec')
    async def test_run_command_success(self, mock_subprocess):
        """Test exécution de commande - succès"""
        # Mock du processus
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdout.readline = AsyncMock(side_effect=[
            "Line 1\n",
            "Line 2\n",
            "",  # Fin
        ])
        mock_process.wait = AsyncMock(return_value=0)
        # stderr est redirigé vers stdout dans le code, donc None est OK
        mock_process.stderr = AsyncMock()
        mock_process.stderr.read = AsyncMock(return_value="")
        
        mock_subprocess.return_value = mock_process
        
        executor = GreaseweazleExecutor(gw_path="gw")
        output_lines = []
        
        def on_output(line):
            output_lines.append(line)
        
        result = await executor.run_command(["test"], on_output=on_output)
        
        assert result.returncode == 0
        assert "Line 1" in result.stdout
        assert "Line 2" in result.stdout
        assert len(output_lines) == 2
    
    @patch('asyncio.create_subprocess_exec')
    async def test_run_command_no_output(self, mock_subprocess):
        """Test exécution de commande - pas de sortie"""
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdout.readline = AsyncMock(return_value="")
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.stderr = AsyncMock()
        mock_process.stderr.read = AsyncMock(return_value="")
        
        mock_subprocess.return_value = mock_process
        
        executor = GreaseweazleExecutor(gw_path="gw")
        result = await executor.run_command(["test"])
        
        assert result.returncode == 0
        assert result.stdout == ""
    
    @patch('asyncio.create_subprocess_exec')
    async def test_run_align(self, mock_subprocess):
        """Test exécution de la commande align"""
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdout.readline = AsyncMock(side_effect=[
            "00.0    : base: 1.000 us [99.911%]\n",
            "",  # Fin
        ])
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.stderr = AsyncMock()
        mock_process.stderr.read = AsyncMock(return_value="")
        
        mock_subprocess.return_value = mock_process
        
        executor = GreaseweazleExecutor(gw_path="gw")
        output_lines = []
        
        def on_output(line):
            output_lines.append(line)
        
        result = await executor.run_align(cylinders=80, retries=3, on_output=on_output)
        
        assert result["success"] is True
        assert result["returncode"] == 0
        assert len(output_lines) == 1
        assert "99.911%" in output_lines[0]
        
        # Vérifier les arguments de la commande
        call_args = mock_subprocess.call_args
        assert "align" in call_args[0]
    
    @patch('asyncio.create_subprocess_exec')
    async def test_run_align_failure(self, mock_subprocess):
        """Test exécution de la commande align - échec"""
        mock_process = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdout.readline = AsyncMock(return_value="")
        mock_process.wait = AsyncMock(return_value=1)
        mock_process.stderr = AsyncMock()
        mock_process.stderr.read = AsyncMock(return_value="")
        
        mock_subprocess.return_value = mock_process
        
        executor = GreaseweazleExecutor(gw_path="gw")
        result = await executor.run_align(cylinders=80, retries=3)
        
        assert result["success"] is False
        assert result["returncode"] == 1

