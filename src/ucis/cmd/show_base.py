"""
Base class for UCIS show commands
"""
import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TextIO


class ShowBase(ABC):
    """
    Abstract base class for all show commands.
    
    Provides common functionality for:
    - Database loading
    - Output formatting (JSON, text)
    - Error handling
    """
    
    def __init__(self, args):
        """
        Initialize show command.
        
        Args:
            args: Parsed command-line arguments
        """
        self.args = args
        self.db = None
        
    def execute(self):
        """
        Execute the show command.
        
        This is the main entry point called by the command dispatcher.
        Handles database loading, execution, and output formatting.
        """
        from ucis.rgy.format_rgy import FormatRgy
        
        rgy = FormatRgy.inst()
        
        # Determine input format
        if self.args.input_format is None:
            # Try to detect format from file
            detected_format = rgy.detectDatabaseFormat(self.args.db)
            if detected_format is not None:
                self.args.input_format = detected_format
            else:
                self.args.input_format = rgy.getDefaultDatabase()
            
        if not rgy.hasDatabaseFormat(self.args.input_format):
            raise Exception("Unknown input format %s ; supported=%s" % (
                self.args.input_format, str(rgy.getDatabaseFormats())))
        
        # Load database
        input_desc = rgy.getDatabaseDesc(self.args.input_format)
        input_if = input_desc.fmt_if()
        self.db = input_if.read(self.args.db)
        
        try:
            # Get data
            data = self.get_data()
            
            # Output
            self._write_output(data)
            
        finally:
            if self.db:
                self.db.close()
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Get the data to display.
        
        Subclasses must implement this method to extract
        the relevant data from self.db.
        
        Returns:
            Dictionary containing the data to output
        """
        pass
    
    def _write_output(self, data: Dict[str, Any]):
        """
        Write output in the specified format.
        
        Args:
            data: Dictionary to output
        """
        output_format = getattr(self.args, 'output_format', 'json')
        out = getattr(self.args, 'out', None)
        
        if out is None:
            fp = sys.stdout
            close_fp = False
        else:
            fp = open(out, 'w')
            close_fp = True
            
        try:
            if output_format == 'json':
                self._write_json(data, fp)
            elif output_format == 'text' or output_format == 'txt':
                self._write_text(data, fp)
            else:
                raise Exception("Unknown output format: %s" % output_format)
        finally:
            if close_fp:
                fp.close()
    
    def _write_json(self, data: Dict[str, Any], fp: TextIO):
        """Write data as JSON."""
        json.dump(data, fp, indent=2)
        fp.write("\n")
        
    def _write_text(self, data: Dict[str, Any], fp: TextIO):
        """
        Write data as human-readable text.
        
        Default implementation. Subclasses can override for
        custom text formatting.
        """
        self._format_text_recursive(data, fp, indent=0)
        
    def _format_text_recursive(self, obj: Any, fp: TextIO, indent: int = 0):
        """Recursively format objects as text."""
        ind = "  " * indent
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    fp.write(f"{ind}{key}:\n")
                    self._format_text_recursive(value, fp, indent + 1)
                else:
                    fp.write(f"{ind}{key}: {value}\n")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._format_text_recursive(item, fp, indent)
                else:
                    fp.write(f"{ind}- {item}\n")
        else:
            fp.write(f"{ind}{obj}\n")
