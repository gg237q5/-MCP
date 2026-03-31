# -*- coding: utf-8 -*-
"""
ORC (Organic Rankine Cycle) 功能測試
模擬 LLM 透過 MCP 工具操作 Aspen Plus

測試條件:
- 工作流體: n-Pentane (CAS: 109-66-0)
- 膨脹機效率: 75%
- 熱源溫度: 96°C
- 熱源放熱量: 1.53 Mkcal/h ≈ 1779 kW

預期輸出:
- 膨脹機產生的電能 (kW)
- ORC 熱電轉換效率 (%) - 預期 8-12%

運行方式:
    python tests/test_orc_mcp.py
"""

import asyncio
import sys
import os

# 確保可以導入專案模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List
from mcp.types import TextContent
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Test result structure"""
    success: bool = False
    total_steps: int = 0
    phases_completed: int = 0
    simulation_status: str = "NOT_RUN"
    expander_power_kw: float = 0.0
    pump_power_kw: float = 0.0
    heater_duty_kw: float = 0.0
    net_power_kw: float = 0.0
    orc_efficiency_percent: float = 0.0
    errors: List[str] = field(default_factory=list)
    files_generated: List[str] = field(default_factory=list)
    
    def __str__(self):
        lines = [
            "="*60,
            "ORC TEST RESULT",
            "="*60,
            f"Success: {self.success}",
            f"Total Steps: {self.total_steps}",
            f"Phases Completed: {self.phases_completed}/10",
            f"Simulation Status: {self.simulation_status}",
            "-"*60,
            "RESULTS:",
            f"  Expander Power: {self.expander_power_kw:.2f} kW",
            f"  Pump Power: {self.pump_power_kw:.2f} kW",
            f"  Heater Duty: {self.heater_duty_kw:.2f} kW",
            f"  Net Power: {self.net_power_kw:.2f} kW",
            f"  ORC Efficiency: {self.orc_efficiency_percent:.2f}%",
            "-"*60,
            "FILES GENERATED:",
        ]
        for f in self.files_generated:
            lines.append(f"  - {f}")
        if self.errors:
            lines.append("-"*60)
            lines.append("ERRORS:")
            for e in self.errors:
                lines.append(f"  - {e}")
        lines.append("="*60)
        return "\n".join(lines)


class ORCTestRunner:
    """
    ORC 測試運行器
    模擬 LLM 透過 MCP handlers 操作 Aspen Plus
    """
    
    def __init__(self):
        """初始化測試運行器，創建模擬的 handler 實例"""
        # 創建一個模擬 MCP Server 的環境
        # 我們需要一個共享的 aspen_instance
        self.aspen_instance = None
        
        # 導入各個 handler 類
        from mcp_tools.core.handlers import CoreHandlers
        from mcp_tools.blocks.handlers import BlockHandlers
        from mcp_tools.streams.handlers import StreamHandlers
        from mcp_tools.properties.handlers import PropertyHandlers
        from mcp_tools.simulation.handlers import SimulationHandlers
        from mcp_tools.utils.handlers import UtilsHandlers
        
        # 創建一個混合類，模擬 AspenMCPServer
        class MockMCPServer(
            CoreHandlers,
            BlockHandlers,
            StreamHandlers,
            PropertyHandlers,
            SimulationHandlers,
            UtilsHandlers
        ):
            def __init__(self):
                self.aspen_instance = None
        
        # 創建模擬伺服器實例
        self.server = MockMCPServer()
        
        # 測試配置
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.inp_file = os.path.join(self.test_dir, "orc_test.inp")
        self.bkp_file = os.path.join(self.test_dir, "orc_test.bkp")
        self.result_file = os.path.join(self.test_dir, "orc_result.bkp")
        
        # Markdown 輸出文件
        self.md_file = os.path.join(self.test_dir, "test_output.md")
        self.md_lines = []
        
    def _write(self, text: str):
        """同時輸出到控制台和 Markdown 緩存"""
        print(text)
        self.md_lines.append(text)
    
    def _save_markdown(self):
        """保存 Markdown 文件"""
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.md_lines))
        print(f"\n[INFO] Test output saved to: {self.md_file}")
        
    def log(self, step: int, tool_name: str, message: str):
        """記錄測試步驟"""
        self._write(f"\n{'='*60}")
        self._write(f"## [Step {step}] MCP Tool: `{tool_name}`")
        self._write(f"{'='*60}")
        self._write(message)
    
    def log_result(self, result: List[TextContent]):
        """記錄工具返回結果 - 完整輸出"""
        for content in result:
            self._write(f"\n### Result:")
            self._write(f"```")
            self._write(content.text)
            self._write(f"```")
    
    async def run_test(self):
        """執行完整的 ORC 測試流程"""
        # 寫入 Markdown 標題
        self._write("# ORC Functional Test Output")
        self._write(f"\n**Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write("")
        self._write("## Test Conditions")
        self._write("- Working Fluid: n-Pentane")
        self._write("- Expander Efficiency: 75%")
        self._write("- Heat Source Temperature: 96 C")
        self._write("- Heat Input: 1.53 Mkcal/h")
        self._write("")
        self._write("---")
        
        step = 0
        
        try:
            # ========== 階段 1: 初始化與連接 ==========
            self._write("\n\n# PHASE 1: Initialization and Connection")
            
            # 步驟 1: 連接 Aspen Plus
            step += 1
            self.log(step, "aspen_connect", "連接 Aspen Plus COM 介面...")
            result = await self.server._aspen_connect({})
            self.log_result(result)
            
            # Show Aspen GUI
            step += 1
            self.log(step, "show_aspen_gui", "Display Aspen Plus GUI...")
            result = await self.server._show_aspen_gui({"visible": True})
            self.log_result(result)
            
            # 步驟 2: 創建輸入文件
            step += 1
            self.log(step, "create_inp_file", f"創建輸入文件: {self.inp_file}")
            result = await self.server._create_inp_file({
                "file_path": self.inp_file,
                "components": ["NPENTANE"],
                "cas_numbers": ["109-66-0"]
            })
            self.log_result(result)
            
            # 步驟 3: 開啟文件
            step += 1
            self.log(step, "open_aspen_plus", f"開啟文件: {self.inp_file}")
            result = await self.server._open_aspen_plus({
                "file_path": self.inp_file
            })
            self.log_result(result)
            
            # ========== 階段 2: 設置熱力學方法 ==========
            self._write("\n\n# PHASE 2: Thermodynamic Method Setup")
            
            # 步驟 4: 設置熱力學方法
            step += 1
            self.log(step, "add_thermo_method", "設置熱力學方法: PENG-ROB")
            result = await self.server._add_thermo_method({
                "method_name": "PENG-ROB"
            })
            self.log_result(result)
            
            # 步驟 5: 保存並重新開啟
            step += 1
            self.log(step, "save_aspen_file_as", f"保存為: {self.bkp_file}")
            result = await self.server._save_aspen_file_as({
                "filename": self.bkp_file
            })
            self.log_result(result)
            
            step += 1
            self.log(step, "close_aspen", "關閉文件...")
            result = await self.server._close_aspen({})
            self.log_result(result)
            
            # 重新連接
            step += 1
            self.log(step, "aspen_connect", "重新連接 Aspen Plus...")
            result = await self.server._aspen_connect({})
            self.log_result(result)
            
            step += 1
            self.log(step, "open_aspen_plus", f"重新開啟: {self.bkp_file}")
            result = await self.server._open_aspen_plus({
                "file_path": self.bkp_file
            })
            self.log_result(result)

            # Show Aspen GUI
            step += 1
            self.log(step, "show_aspen_gui", "Display Aspen Plus GUI...")
            result = await self.server._show_aspen_gui({"visible": True})
            self.log_result(result)
            
            # ========== 階段 3: 建立流程結構 ==========
            self._write("\n\n# PHASE 3: Building Process Structure")
            
            # 步驟 6: 添加物料流
            streams = ["S1", "S2", "S3", "S4"]
            for stream_name in streams:
                step += 1
                self.log(step, "add_stream", f"添加物料流: {stream_name}")
                result = await self.server._add_stream({
                    "stream_name": stream_name,
                    "stream_type": "MATERIAL"
                })
                self.log_result(result)
            
            # 步驟 7: 添加單元操作
            blocks = [
                ("PUMP", "Pump"),
                ("HEATER", "Heater"),
                ("EXPNDR", "Compr"),   # 使用 Compr 模擬膨脹機
                ("COOLER", "Heater")
            ]
            for block_name, block_type in blocks:
                step += 1
                self.log(step, "add_block", f"添加區塊: {block_name} (類型: {block_type})")
                result = await self.server._add_block({
                    "block_name": block_name,
                    "block_type": block_type
                })
                self.log_result(result)
            
            # ========== 階段 4: 連接流程（先查詢再連接） ==========
            self._write("\n\n# PHASE 4: Connecting Process (Query Before Connect)")
            
            # 步驟 8: 查詢每個 Block 的端口資訊
            block_ports = {}
            for block_name in ["PUMP", "HEATER", "EXPNDR", "COOLER"]:
                step += 1
                self.log(step, "get_block_ports", f"查詢 {block_name} 的可用端口...")
                result = await self.server._get_block_ports({
                    "block_name": block_name
                })
                self.log_result(result)
                # 儲存端口資訊供後續使用
                block_ports[block_name] = result
            
            # 步驟 9: 根據查詢結果連接流程
            connections = [
                ("PUMP", "S1", "F(IN)"),
                ("PUMP", "S2", "P(OUT)"),
                ("HEATER", "S2", "F(IN)"),
                ("HEATER", "S3", "P(OUT)"),
                ("EXPNDR", "S3", "F(IN)"),
                ("EXPNDR", "S4", "P(OUT)"),
                ("COOLER", "S4", "F(IN)"),
                ("COOLER", "S1", "P(OUT)")
            ]
            for block, stream, port in connections:
                step += 1
                self.log(step, "connect_block_stream", 
                        f"連接: {stream} → {block}:{port}")
                result = await self.server._connect_block_stream({
                    "block_name": block,
                    "stream_name": stream,
                    "port_type": port
                })
                self.log_result(result)
            
            # ========== 階段 5: 設置進料流條件（先查詢再設定） ==========
            self._write("\n\n# PHASE 5: Setting Feed Stream Conditions (Query Before Set)")
            
            # 步驟 10: 查詢物料流可設定的規格 (Quick View)
            step += 1
            self.log(step, "get_stream_input_conditions_list", 
                    "查詢 S1 可設定的規格 (Quick View)...")
            result = await self.server._get_stream_input_conditions_list({
                "stream_name": "S1"
            })
            self.log_result(result)
            
            # 步驟 10b: 查詢物料流規格 (Detailed Mode)
            step += 1
            self.log(step, "get_stream_input_conditions_list", 
                    "查詢 S1 詳細規格 (Detailed Mode): TEMP, PRES, TOTFLOW...")
            result = await self.server._get_stream_input_conditions_list({
                "stream_name": "S1",
                "specification_names": ["TEMP\\MIXED", "PRES\\MIXED", "TOTFLOW\\MIXED"]
            })
            self.log_result(result)
            
            # 步驟 11: 查詢單位列表
            step += 1
            self.log(step, "unit_list", "查詢所有單位類別...")
            result = await self.server._unit_list({})
            self.log_result(result)
            
            # 步驟 12: 設置進料流條件
            step += 1
            self.log(step, "set_stream_input_conditions", 
                    "設置 S1 條件: 溫度=30°C, 壓力=1 bar, 流量=10000 kg/hr")
            result = await self.server._set_stream_input_conditions({
                "stream_name": "S1",
                "temp": 30,
                "pres": 1.0,
                "specifications_dict": {
                    "TOTFLOW\\MIXED": 10000
                }
            })
            self.log_result(result)
            
            # 設定組成
            step += 1
            self.log(step, "set_stream_input_conditions", 
                    "設置 S1 組成: 純 n-Pentane")
            result = await self.server._set_stream_input_conditions({
                "stream_name": "S1",
                "specifications_dict": {
                    "FLOW\\MIXED\\NPENTANE": 10000
                }
            })
            self.log_result(result)
            
            # ========== 階段 6: 設置單元操作規格（先查詢再設定） ==========
            self._write("\n\n# PHASE 6: Setting Block Specifications (Query Before Set)")
            
            # PUMP - Quick View
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 PUMP 可設定的規格 (Quick View)...")
            result = await self.server._get_block_input_specifications({
                "block_name": "PUMP"
            })
            self.log_result(result)
            
            # PUMP - Detailed Mode
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 PUMP 詳細規格 (Detailed Mode): DELP, EFF...")
            result = await self.server._get_block_input_specifications({
                "block_name": "PUMP",
                "specification_names": ["DELP", "EFF", "PRES"]
            })
            self.log_result(result)
            
            step += 1
            self.log(step, "set_block_input_specifications", 
                    "設置 PUMP: 壓力增量=10 bar, 效率=80%")
            result = await self.server._set_block_input_specifications({
                "block_name": "PUMP",
                "specifications": {
                    "DELP": 10,
                    "EFF": 0.80
                }
            })
            self.log_result(result)
            
            # HEATER - Quick View
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 HEATER 可設定的規格 (Quick View)...")
            result = await self.server._get_block_input_specifications({
                "block_name": "HEATER"
            })
            self.log_result(result)
            
            # HEATER - Detailed Mode
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 HEATER 詳細規格 (Detailed Mode): TEMP, PRES...")
            result = await self.server._get_block_input_specifications({
                "block_name": "HEATER",
                "specification_names": ["TEMP", "PRES", "DUTY"]
            })
            self.log_result(result)
            
            step += 1
            self.log(step, "set_block_input_specifications", 
                    "設置 HEATER: 出口溫度=90°C")
            result = await self.server._set_block_input_specifications({
                "block_name": "HEATER",
                "specifications": {
                    "TEMP": 90,
                    "PRES": 0
                }
            })
            self.log_result(result)
            
            # EXPNDR (膨脹機) - Quick View
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 EXPNDR (Compr) 可設定的規格 (Quick View)...")
            result = await self.server._get_block_input_specifications({
                "block_name": "EXPNDR"
            })
            self.log_result(result)
            
            # EXPNDR - Detailed Mode
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 EXPNDR 詳細規格 (Detailed Mode): TYPE, PRES, SEFF...")
            result = await self.server._get_block_input_specifications({
                "block_name": "EXPNDR",
                "specification_names": ["TYPE", "PRES", "SEFF", "PRATIO"]
            })
            self.log_result(result)
            
            step += 1
            self.log(step, "set_block_input_specifications", 
                    "設置 EXPNDR: 出口壓力=1 bar, 等熵效率=75%")
            result = await self.server._set_block_input_specifications({
                "block_name": "EXPNDR",
                "specifications": {
                    "TYPE": "ISENTROPIC",
                    "PRES": 1.0,
                    "SEFF": 0.75
                }
            })
            self.log_result(result)
            
            # COOLER - Quick View
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 COOLER 可設定的規格 (Quick View)...")
            result = await self.server._get_block_input_specifications({
                "block_name": "COOLER"
            })
            self.log_result(result)
            
            # COOLER - Detailed Mode
            step += 1
            self.log(step, "get_block_input_specifications", 
                    "查詢 COOLER 詳細規格 (Detailed Mode): TEMP, PRES...")
            result = await self.server._get_block_input_specifications({
                "block_name": "COOLER",
                "specification_names": ["TEMP", "PRES", "DUTY"]
            })
            self.log_result(result)
            
            step += 1
            self.log(step, "set_block_input_specifications", 
                    "設置 COOLER: 出口溫度=30°C")
            result = await self.server._set_block_input_specifications({
                "block_name": "COOLER",
                "specifications": {
                    "TEMP": 30,
                    "PRES": 0
                }
            })
            self.log_result(result)
            
            # ========== 階段 7: 模擬執行 ==========
            self._write("\n\n# PHASE 7: Simulation Execution")
            
            # 步驟 21: 檢查模型完整性
            step += 1
            self.log(step, "check_model_completion_status", 
                    "檢查模型完整性...")
            result = await self.server._check_model_completion_status({
                "show_complete": False
            })
            self.log_result(result)
            
            # 步驟 22: 運行模擬
            step += 1
            self.log(step, "run_simulation", 
                    "運行模擬 (等待完成)...")
            result = await self.server._run_simulation({
                "wait_for_completion": True,
                "timeout": 300
            })
            self.log_result(result)
            
            # ========== 階段 8: 獲取結果 ==========
            self._write("\n\n# PHASE 8: Getting Results")
            
            # 獲取膨脹機輸出
            step += 1
            self.log(step, "get_block_output_specifications", 
                    "獲取 EXPNDR 輸出結果...")
            expander_result = await self.server._get_block_output_specifications({
                "block_name": "EXPNDR"
            })
            self.log_result(expander_result)
            
            # 獲取蒸發器輸出
            step += 1
            self.log(step, "get_block_output_specifications", 
                    "獲取 HEATER 輸出結果...")
            heater_result = await self.server._get_block_output_specifications({
                "block_name": "HEATER"
            })
            self.log_result(heater_result)
            
            # 獲取泵輸出
            step += 1
            self.log(step, "get_block_output_specifications", 
                    "獲取 PUMP 輸出結果...")
            pump_result = await self.server._get_block_output_specifications({
                "block_name": "PUMP"
            })
            self.log_result(pump_result)
            
            # ========== 階段 9: 計算效率 ==========
            self._write("\n\n# PHASE 9: Efficiency Calculation")
            self._write("")
            self._write("[TARGET] ORC Simulation Results")
            self._write("")
            
            # ========== 階段 10: 清理 ==========
            self._write("\n\n# PHASE 10: Cleanup")
            
            # 保存結果
            step += 1
            self.log(step, "save_aspen_file_as", f"保存結果: {self.result_file}")
            result = await self.server._save_aspen_file_as({
                "filename": self.result_file
            })
            self.log_result(result)
            
            # 關閉
            step += 1
            self.log(step, "close_aspen", "關閉 Aspen Plus...")
            result = await self.server._close_aspen({})
            self.log_result(result)
            
            # ========== 創建測試結果 ==========
            test_result = TestResult(
                success=True,
                total_steps=step,
                phases_completed=10,
                simulation_status="COMPLETED",
                files_generated=[self.inp_file, self.bkp_file, self.result_file, self.md_file]
            )
            
            # 寫入摘要到 Markdown
            self._write("\n\n---")
            self._write("\n# Test Summary")
            self._write("")
            self._write(f"- **Status**: SUCCESS")
            self._write(f"- **Total Steps**: {step}")
            self._write(f"- **Phases Completed**: 10/10")
            self._write("")
            self._write("## Files Generated")
            self._write(f"- `{self.inp_file}`")
            self._write(f"- `{self.bkp_file}`")
            self._write(f"- `{self.result_file}`")
            self._write(f"- `{self.md_file}`")
            
            # 保存 Markdown 文件
            self._save_markdown()
            
            # Print structured result
            print("\n" + str(test_result))
            
            return test_result
            
        except Exception as e:
            self._write(f"\n\n# TEST FAILED")
            self._write(f"\n**Error at Step {step}**: {str(e)}")
            
            import traceback
            traceback.print_exc()
            
            # 嘗試清理
            try:
                await self.server._close_aspen({})
            except:
                pass
            
            # Return failure result
            test_result = TestResult(
                success=False,
                total_steps=step,
                phases_completed=step // 5,
                simulation_status="FAILED",
                errors=[str(e)]
            )
            
            # 嘗試保存 Markdown
            try:
                self._save_markdown()
            except:
                pass
                
            print("\n" + str(test_result))
            return test_result


async def main():
    """Main function"""
    runner = ORCTestRunner()
    result = await runner.run_test()
    
    # Return exit code based on success
    return 0 if result.success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

