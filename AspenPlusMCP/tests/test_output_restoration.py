import sys
import os
import unittest
from unittest.mock import MagicMock

# Add code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aspen_core.streams import StreamsMixin
from aspen_core.blocks import BlocksMixin
import UserDifineException as UDE

class MockElement:
    def __init__(self, name, value=None, attributes=None, children=None):
        self.Name = name
        self.Value = value
        self.Attributes = attributes or {}
        self.Children = children or []
        
        # Attribute mappings:
        # 2: Unit Category (PQ)
        # 3: Unit Index (UM)
        # 5: Option List
        # 18: HAP_OUTVAR (1 = Output Variable)
        # 19: Description

    def AttributeValue(self, index):
        if index == 5: # Option List
             mock_options = MagicMock()
             if 5 in self.Attributes:
                 mock_options.Elements.Count = len(self.Attributes[5])
                 mock_options.Elements = lambda i: MagicMock(Value=self.Attributes[5][i])
                 return mock_options
             return None
        return self.Attributes.get(index)

    @property
    def Elements(self):
        mock_collection = MagicMock()
        mock_collection.__iter__.return_value = self.Children
        mock_collection.Count = len(self.Children)
        return mock_collection

class TestStrictRestoration(unittest.TestCase):
    def setUp(self):
        self.mock_aspen = MagicMock()
        
    def test_stream_output_traversal(self):
        print("\nTesting Get_StreamOutputConditionsList logic...")
        
        # Create a mock StreamsMixin instance
        class StreamTester(StreamsMixin):
            def __init__(self, aspen_mock):
                self.aspen = aspen_mock
            
            def StreamsNameList(self):
                return ["TEST_STREAM"]
                
            def UnitList(self, args, table=False):
                return "kg/hr"
        
        tester = StreamTester(self.mock_aspen)
        
        # Mock the tree structure: \Data\Streams\TEST_STREAM\Output
        # Structure:
        # Output
        #   - TEMP (Output Var, Value=100.0, Unit=C)
        #   - FLOW (Folder)
        #       - MIXED (Output Var, Value=50.0, Unit=kg/hr)
        
        temp_node = MockElement("TEMP", value=100.0, attributes={
            18: 1, # Output variable
            19: "Termperature",
            2: 22, # Unit cat
            3: 1   # Unit index
        })
        
        mixed_node = MockElement("MIXED", value=50.0, attributes={
            18: 1, # Output variable
            19: "Mass Flow",
            2: 10, 
            3: 3
        })
        
        flow_node = MockElement("FLOW", attributes={18: 0}, children=[mixed_node])
        
        output_root = MockElement("Output", children=[temp_node, flow_node])
        
        self.mock_aspen.Tree.FindNode.return_value = output_root
        
        # Run test
        results = tester.Get_StreamOutputConditionsList("TEST_STREAM", table=True)
        
        # Verify
        self.assertIn("TEMP", results)
        self.assertEqual(results["TEMP"]["value"], 100.0)
        self.assertIn("FLOW\\MIXED", results)
        self.assertEqual(results["FLOW\\MIXED"]["value"], 50.0)
        print("Stream traversal verified successfully!")

    def test_block_output_traversal(self):
        print("\nTesting Get_BlockOutputSpecificationsList logic...")
        
        # Create a mock BlocksMixin instance
        class BlockTester(BlocksMixin):
            def __init__(self, aspen_mock):
                self.aspen = aspen_mock
                
            def BlocksNameList(self):
                return ["TEST_BLOCK"]
            
            def BlockType(self, name):
                return "RADFRAC"
                
            def UnitList(self, args, table=False):
                return "kW"

        tester = BlockTester(self.mock_aspen)
        
        # Mock: \Data\Blocks\TEST_BLOCK\Output
        # Output
        #   - DUTY (Output Var, Value=2500.0, Unit=kW)
        
        duty_node = MockElement("DUTY", value=2500.0, attributes={
            18: 1,
            19: "Heat Duty",
            2: 15,
            3: 2
        })
        
        output_root = MockElement("Output", children=[duty_node])
        self.mock_aspen.Tree.FindNode.return_value = output_root
        
        # Run test
        results = tester.Get_BlockOutputSpecificationsList("TEST_BLOCK", table=True)
        
        # Verify
        self.assertIn("DUTY", results)
        self.assertEqual(results["DUTY"]["value"], 2500.0)
        print("Block traversal verified successfully!")

if __name__ == '__main__':
    unittest.main()
