import os
import tempfile
import yaml
from pathlib import Path

import pytest

from config_reader import ConfigReader


class TestConfigReader:
    """Test class for ConfigReader functionality."""
    
    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_config_file(self):
        """Test ConfigReader with nonexistent config file."""
        config_reader = ConfigReader('/nonexistent/path/config.yaml')
        assert config_reader.configs == []
    
    def test_empty_config_file(self):
        """Test ConfigReader with empty config file."""
        config_path = os.path.join(self.temp_dir, 'empty_config.yaml')
        with open(config_path, 'w') as f:
            f.write('')
        
        config_reader = ConfigReader(config_path)
        assert config_reader.configs == []
    
    def test_single_config(self):
        """Test ConfigReader with single config."""
        config_data = {
            'library_path': '/test/library',
            'ext_lib_name': 'test-lib',
            'mirror_path': '/test/mirror',
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        
        config_path = os.path.join(self.temp_dir, 'single_config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data
    
    def test_multiple_configs(self):
        """Test ConfigReader with multiple configs in single file."""
        config_data1 = {
            'library_path': '/test/library1',
            'ext_lib_name': 'test-lib1',
            'mirror_path': '/test/mirror1',
            'dry_run': True
        }
        config_data2 = {
            'library_path': '/test/library2',
            'ext_lib_name': 'test-lib2',
            'mirror_path': '/test/mirror2',
            'dry_run': False
        }
        
        config_path = os.path.join(self.temp_dir, 'multiple_configs.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data1, f)
            f.write('---\n')  # YAML document separator
            yaml.dump(config_data2, f)
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 2
        assert config_reader.configs[0] == config_data1
        assert config_reader.configs[1] == config_data2
    
    def test_config_with_defaults(self):
        """Test ConfigReader with config that uses default values."""
        config_data = {
            'library_path': '/test/library',
            'ext_lib_name': 'test-lib'
            # Missing mirror_path, dry_run, etc. - should use defaults
        }
        
        config_path = os.path.join(self.temp_dir, 'config_with_defaults.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data
    
    def test_invalid_yaml_syntax(self):
        """Test ConfigReader with invalid YAML syntax."""
        config_path = os.path.join(self.temp_dir, 'invalid_config.yaml')
        with open(config_path, 'w') as f:
            f.write('invalid: yaml: syntax: [\n')
        
        # Should raise ValueError with informative error message
        with pytest.raises(ValueError) as exc_info:
            ConfigReader(config_path)
        
        error_message = str(exc_info.value)
        assert "Error parsing YAML file" in error_message
        assert config_path in error_message
        assert "mapping values are not allowed here" in error_message.lower()
    
    def test_configs_property(self):
        """Test that configs property returns the correct data."""
        config_data = {'test': 'value'}
        config_path = os.path.join(self.temp_dir, 'test_config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        config_reader = ConfigReader(config_path)
        assert config_reader.configs == [config_data]
        # Test that it's a property that returns the same data
        assert config_reader.configs == [config_data]
    
    def test_empty_yaml_file(self):
        """Test ConfigReader with YAML file containing only whitespace."""
        config_path = os.path.join(self.temp_dir, 'empty_yaml.yaml')
        with open(config_path, 'w') as f:
            f.write('\n\n  \n\n')
        
        config_reader = ConfigReader(config_path)
        assert config_reader.configs == []
    
    def test_yaml_with_comments(self):
        """Test ConfigReader with YAML file containing comments."""
        config_data = {
            'library_path': '/test/library',
            'ext_lib_name': 'test-lib'
        }
        
        config_path = os.path.join(self.temp_dir, 'commented_config.yaml')
        with open(config_path, 'w') as f:
            f.write('# This is a comment\n')
            f.write('# Another comment\n')
            yaml.dump(config_data, f)
            f.write('# End comment\n')
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data
    
    def test_complex_config_structure(self):
        """Test ConfigReader with complex nested config structure."""
        config_data = {
            'library_path': '/test/library',
            'ext_lib_name': 'test-lib',
            'mirror_path': '/test/mirror',
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub',
            'nested_config': {
                'option1': 'value1',
                'option2': ['item1', 'item2', 'item3'],
                'option3': {
                    'suboption1': True,
                    'suboption2': False
                }
            },
            'list_config': ['item1', 'item2', 'item3']
        }
        
        config_path = os.path.join(self.temp_dir, 'complex_config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data
    
    def test_config_file_permissions(self):
        """Test ConfigReader with different file permissions."""
        config_data = {'test': 'value'}
        config_path = os.path.join(self.temp_dir, 'permission_test.yaml')
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Test with read-only file
        os.chmod(config_path, 0o444)
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data
    
    def test_unicode_in_config(self):
        """Test ConfigReader with unicode characters in config."""
        config_data = {
            'library_path': '/test/📚/library',
            'ext_lib_name': '作者名-library',
            'mirror_path': '/test/镜像/mirror',
            'description': 'Test config with unicode: 📚 作者名 镜像'
        }
        
        config_path = os.path.join(self.temp_dir, 'unicode_config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        config_reader = ConfigReader(config_path)
        assert len(config_reader.configs) == 1
        assert config_reader.configs[0] == config_data


class TestConfigReaderIntegration:
    """Integration tests for ConfigReader with real file system."""
    
    def test_real_config_file(self):
        """Test with actual config file structure."""
        # Create a config file similar to the real one
        config_data = {
            'library_path': '/Volumes/Storage-Pool/Books/Calibre Libraries/Calibre Comics Library',
            'ext_lib_name': 'thomas-calibre-web',
            'mirror_path': '/Volumes/Scratch/test-mirror',
            'dry_run': True,
            'source_format': '.cbz',
            'dest_format': '.cbz'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config_reader = ConfigReader(config_path)
            assert len(config_reader.configs) == 1
            assert config_reader.configs[0] == config_data
        finally:
            os.unlink(config_path) 