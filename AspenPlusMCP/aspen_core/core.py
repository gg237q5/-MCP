# -*- coding: utf-8 -*-
"""
Core operations for Aspen Plus COM interface.
Handles connection, file operations, GUI visibility, and dialog suppression.

Corresponds to: mcp_tools/core/
"""

import os
import UserDifineException as UDE
from .constants import ExportType


class CoreMixin:
    """Mixin class for Aspen Plus core operations (connection + file ops)."""

    # ========== Connection Methods ==========

    def AspenConnect(self, version=None):
        """Connect to AspenPlus application via COM interface.

        :param version: String. Specify the version of AspenPlus to connect to 
                       (e.g., 'Apwn36.0' for Aspen Plus V10.0).
                       If None, connects to the default installed version.
        :return: None
        """
        import win32com.client as win32

        try:
            if self.aspen is not None:
                print("Already connected to AspenPlus.")
            else:
                if version is not None:
                    self.aspen = win32.Dispatch(f'Apwn.Document.{version}.0')
                else:
                    self.aspen = win32.Dispatch('Apwn.Document')
                print("Successfully connected to AspenPlus.")
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to connect to AspenPlus: {str(e)}")

    def IsAspenConnected(self):
        """Check if AspenPlus application is connected.

        :return: Boolean. True if connected, False otherwise.
        """
        try:
            _ = self.aspen.Visible
            return True
        except Exception:
            return False

    def CloseAspenConnection(self):
        """Close the connection to AspenPlus application.

        :return: None
        """
        try:
            self.aspen.Quit()
            print("AspenPlus connection closed.")
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to close AspenPlus connection: {str(e)}")

    def Show(self, log):
        """Show Aspen GUI or not.

        :param log: a Boolean value. True for Show the GUI, False for close the GUI.
        :return: None
        """
        if type(log) != bool:
            raise TypeError("table must be 'Boolen' value.")

        self.aspen.Visible = log

    def SuppressDialogs(self, suppress: bool):
        """Control whether Aspen Plus displays popup dialogs when running or saving.

        :param suppress: True to avoid popup dialogs, False to allow them.
        :return: None
        """
        if type(suppress) != bool:
            raise TypeError("suppress must be a 'Boolen' value.")
        try:
            self.aspen.SuppressDialogs = suppress
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to set SuppressDialogs: {str(e)}")

    def Close(self):
        """Close AspenPlus COM object.

        :return: None
        """
        self.aspen.Close()

    # ========== File Operations ==========

    def LoadFile(self, path):
        """Load the AspenFile.
        
        :param path: String. Path to the Aspen Plus file to load.
        :return: None
        """
        try:
            if not os.path.isfile(path):
                raise UDE.FileNotExist(
                    "File cannot find at designated dictionary." +
                    " Please check the dic you input.")

            self.aspen.InitFromArchive(path)
            self.Show(True)
            self.SuppressDialogs(True)
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to open AspenPlus file: {str(e)}")

    def RunStatus(self):
        """Determine the status of Aspen After Run

        :return: if file is available, return 'Available'. if file has waring, return 'Warning'.
        if file has error, return 'Error'.
        """
        try:
            # Navigate to the Run-Status node step by step to handle None cases
            data_node = self.aspen.Tree.Elements("Data")
            if data_node is None:
                raise UDE.AspenPlus_FileStatusError("Data node not found")
            
            results_summary = data_node.Elements("Results Summary")
            if results_summary is None:
                raise UDE.AspenPlus_FileStatusError("Results Summary node not found")
            
            run_status_node = results_summary.Elements("Run-Status")
            if run_status_node is None:
                raise UDE.AspenPlus_FileStatusError("Run-Status node not found")
            
            status_code = run_status_node.AttributeValue(12)
            if status_code is None:
                raise UDE.AspenPlus_FileStatusError("Run-Status AttributeValue(12) returned None")
            
            if (status_code & 1) == 1:
                return 'Available'
            elif (status_code & 4) == 4:
                return 'Warning'
            elif (status_code & 32) == 32:
                return 'Error'
            else:
                raise UDE.AspenPlus_FileStatusError(f"Run Status recognized error. Status code: {status_code}")
        except UDE.AspenPlus_FileStatusError:
            raise
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get run status: {str(e)}")

    def Save(self):
        """Save current AspenPlus file

        :return: None
        """
        self.aspen.Save()

    def SaveAs(self, filename):
        """Save current AspenPlus file to a new location with specified filename.

        :param filename: String. Path and filename to save the file to.
        :return: None
        """
        if type(filename) != str:
            raise TypeError("filename must be a 'String'.")

        try:
            file_path, file_ext = os.path.splitext(filename)
            if file_ext.lower() == '.inp':
                filename = file_path + '.bkp'
                print(f"File extension changed from .inp to .bkp")

            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

            self.aspen.SaveAs(filename)
            print(f"File successfully saved as: {filename}")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to save file as {filename}: {str(e)}")

    def CreateInpFile(self, path, Components_list, CAS_list):
        """Create the AspenInputFile(.inp).
        
        :param path: String. Path to save the .inp file.
        :param Components_list: List. List of component names.
        :param CAS_list: List. List of CAS numbers corresponding to components.
        :return: None
        """
        inp_content = """\
DYNAMICS
    DYNAMICS RESULTS=ON

IN-UNITS SI ENERGY=kJ FLOW='kg/hr' MASS-FLOW='kg/hr'  &
        MOLE-FLOW='kmol/hr' VOLUME-FLOW='cum/hr' ENTHALPY-FLO=kW  &
        MOLE-HEAT-CA='kJ/kmol-K' HEAT-TRANS-C='kW/sqm-K' POWER=kW  &
        PRESSURE=bar SURFACE-TENS='dyne/cm' TEMPERATURE=C  &
        THERMAL-COND='kW/m-K' VISCOSITY=cP DELTA-T=C  &
        MOLE-ENTHALP='MBtu/lbmol' MASS-ENTHALP='kJ/kg'  &
        MOLE-ENTROPY='kJ/kmol-K' MASS-ENTROPY='kJ/kg-K'  &
        ELEC-POWER=kW MASS-HEAT-CA='kJ/kg-K' UA='kJ/sec-K' WORK=kJ  &
        HEAT=kJ PDROP-PER-HT='mbar/m' PDROP=bar  &
        VOL-HEAT-CAP='kJ/cum-K' INVERSE-PRES='1/bar'  &
        INVERSE-HT-C='sqm-K/kW' VOL-ENTHALPY='kJ/cum'

DEF-STREAMS CONVEN ALL

SIM-OPTIONS MASS-BAL-CHE=YES TLOWER=-17.777778 FLASH-MAXIT=100  &
        FLASH-TOL=1E-005 PARADIGM=SM GAMUS-BASIS=AQUEOUS

MODEL-OPTION

DATABANKS 'APV140 PURE40' / 'APV140 AQUEOUS' / 'APV140 SOLIDS' &
         / 'APV140 INORGANIC' / 'APV140 PC-SAFT' / NOASPENPCD

PROP-SOURCES 'APV140 PURE40' / 'APV140 AQUEOUS' /  &
        'APV140 SOLIDS' / 'APV140 INORGANIC' / 'APV140 PC-SAFT'

COMPONENTS """
        for component, cas in zip(Components_list, CAS_list):
            inp_content = inp_content + """ 
    {component}  {cas}/""".format(component=component, cas=cas)

        with open(path, 'w') as file:
            file.write(inp_content)
        print(f".inp file generated at {path}")

    def Export(self, export_type: int, file_path: str):
        """Export Aspen Plus file to specified format.

        :param export_type: Export type constant (use ExportType class):
                           ExportType.BACKUP (1) = .bkp
                           ExportType.REPORT (2) = .rep
                           ExportType.SUMMARY (3) = .sum
                           ExportType.INPUT (4) = .inp without graphics
                           ExportType.INPUT_GRAPHICS (5) = .inp with graphics
        :param file_path: Path to save the exported file.
        :return: None
        """
        valid_types = [ExportType.BACKUP, ExportType.REPORT, ExportType.SUMMARY, 
                       ExportType.INPUT, ExportType.INPUT_GRAPHICS]
        if not isinstance(export_type, int) or export_type not in valid_types:
            raise ValueError(f"export_type must be one of {valid_types}")
        
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string")

        try:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

            # Call Aspen Plus Export method
            self.aspen.Export(export_type, file_path)
            
            print(f"Successfully exported {ExportType.get_description(export_type)} to: {file_path}")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to export file: {str(e)}")

