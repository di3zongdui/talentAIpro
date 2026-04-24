# 本地文件夹数据源插件
# 监控本地文件夹，自动扫描简历和JD文件

import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import re

from . import TalentAIPlugin, PluginType, PluginStatus, HeartbeatResult, DataItem

logger = logging.getLogger(__name__)


class LocalFolderPlugin(TalentAIPlugin):
    """本地文件夹数据源插件"""

    def __init__(self, folder_path: str = None):
        super().__init__("local_folder", PluginType.DATA_SOURCE)
        self.folder_path = folder_path or self.config.get("folder_path", "")
        self.supported_formats = [".pdf", ".docx", ".xlsx", ".csv", ".txt"]
        self._file_index: Dict[str, Dict] = {}
        self._candidates_found = []
        self._jobs_found = []

    async def initialize(self) -> bool:
        """初始化插件"""
        if not self.folder_path or not os.path.exists(self.folder_path):
            logger.warning(f"LocalFolderPlugin: folder not found: {self.folder_path}")
            self._use_mock = True
        else:
            self._use_mock = False

        await self._scan_files()
        return True

    async def heartbeat(self) -> HeartbeatResult:
        """执行心跳 - 检查文件变化"""
        if self._use_mock:
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=3,
                items_updated=0,
                metadata={"mode": "mock", "files_found": 5}
            )

        try:
            new_files = await self._check_changes()
            if new_files:
                await self._scan_files()
                return HeartbeatResult(
                    plugin_name=self.name,
                    status=PluginStatus.SUCCESS,
                    items_added=len(new_files),
                    metadata={"new_files": new_files}
                )

            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=0,
                items_updated=0,
                metadata={"mode": "no_changes"}
            )

        except Exception as e:
            logger.error(f"LocalFolderPlugin heartbeat error: {e}")
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.FAILED,
                error_message=str(e)
            )

    async def fetch_data(self, since: Optional[datetime] = None) -> List[DataItem]:
        """获取数据条目"""
        items = []
        for candidate in self._candidates_found:
            items.append(DataItem(
                id=f"local_{candidate['id']}",
                type="candidate",
                source=self.name,
                data=candidate,
                timestamp=datetime.now()
            ))
        for job in self._jobs_found:
            items.append(DataItem(
                id=f"local_{job['id']}",
                type="job",
                source=self.name,
                data=job,
                timestamp=datetime.now()
            ))
        return items

    async def _scan_files(self):
        """扫描文件夹"""
        if self._use_mock:
            self._init_mock_data()
            return

        self._candidates_found = []
        self._jobs_found = []
        folder = Path(self.folder_path)

        for ext in self.supported_formats:
            for file_path in folder.rglob(f"*{ext}"):
                try:
                    file_info = {
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                    }

                    if self._is_resume(file_path.name):
                        candidate = await self._parse_resume(file_path)
                        if candidate:
                            self._candidates_found.append(candidate)
                            self._file_index[str(file_path)] = file_info
                    elif self._is_job_description(file_path.name):
                        job = await self._parse_jd(file_path)
                        if job:
                            self._jobs_found.append(job)
                            self._file_index[str(file_path)] = file_info
                except Exception as e:
                    logger.error(f"Error scanning {file_path}: {e}")

        logger.info(f"LocalFolderPlugin: found {len(self._candidates_found)} candidates, {len(self._jobs_found)} jobs")

    async def _check_changes(self) -> List[str]:
        """检查文件变化"""
        new_files = []
        folder = Path(self.folder_path)
        for ext in self.supported_formats:
            for file_path in folder.rglob(f"*{ext}"):
                if str(file_path) not in self._file_index:
                    new_files.append(str(file_path))
        return new_files

    def _is_resume(self, filename: str) -> bool:
        """判断是否是简历"""
        resume_keywords = ["简历", "candidate", "resume", "CV", "个人简历"]
        filename_lower = filename.lower()
        return any(kw.lower() in filename_lower for kw in resume_keywords)

    def _is_job_description(self, filename: str) -> bool:
        """判断是否是JD"""
        jd_keywords = ["JD", "job", "职位", "招聘", "岗位说明"]
        filename_lower = filename.lower()
        return any(kw.lower() in filename_lower for kw in jd_keywords)

    async def _parse_resume(self, file_path: Path) -> Optional[Dict]:
        """解析简历文件"""
        if file_path.suffix == ".txt":
            return await self._parse_text_resume(file_path)
        else:
            return await self._parse_generic_resume(file_path)

    async def _parse_text_resume(self, file_path: Path) -> Optional[Dict]:
        """解析文本简历"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "id": f"candidate_{hash(file_path.name) % 10000}",
                "name": self._extract_name_from_filename(file_path.name),
                "file_path": str(file_path),
                "format": "txt",
                "content_preview": content[:500],
                "raw_file": str(file_path)
            }
        except Exception as e:
            logger.error(f"Error parsing text resume {file_path}: {e}")
            return None

    async def _parse_generic_resume(self, file_path: Path) -> Dict:
        """通用简历解析（Mock）"""
        return {
            "id": f"candidate_{hash(file_path.name) % 10000}",
            "name": self._extract_name_from_filename(file_path.name),
            "file_path": str(file_path),
            "format": file_path.suffix[1:],
            "skills": ["待解析"],
            "experience_years": 0,
            "education": "待解析",
            "raw_file": str(file_path)
        }

    async def _parse_jd(self, file_path: Path) -> Optional[Dict]:
        """解析JD文件"""
        try:
            content = ""
            if file_path.suffix == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            return {
                "id": f"job_{hash(file_path.name) % 10000}",
                "title": self._extract_job_title_from_filename(file_path.name),
                "file_path": str(file_path),
                "content_preview": content[:500] if content else "",
                "raw_file": str(file_path)
            }
        except Exception as e:
            logger.error(f"Error parsing JD {file_path}: {e}")
            return None

    def _extract_name_from_filename(self, filename: str) -> str:
        """从文件名提取姓名"""
        name = Path(filename).stem
        for prefix in ["简历_", "简历-", "candidate_", "resume_"]:
            name = name.replace(prefix, "")
        match = re.search(r'[\u4e00-\u9fa5]{2,4}', name)
        if match:
            return match.group()
        return name[:10] if len(name) > 10 else name

    def _extract_job_title_from_filename(self, filename: str) -> str:
        """从文件名提取职位"""
        name = Path(filename).stem
        for prefix in ["JD_", "JD-", "job_", "职位_", "招聘_"]:
            name = name.replace(prefix, "")
        match = re.search(r'(前端|后端|全栈|产品|运营|设计|测试|开发|经理|总监)', name)
        if match:
            return match.group() + "工程师"
        return name[:15] if len(name) > 15 else name

    def _init_mock_data(self):
        """初始化Mock数据"""
        self._candidates_found = [
            {"id": "mock_001", "name": "张明", "title": "前端开发工程师",
             "skills": ["React", "Vue", "TypeScript"], "experience_years": 4,
             "education": "本科", "current_company": "字节跳动", "expected_salary": 35, "status": "active"},
            {"id": "mock_002", "name": "李华", "title": "产品经理",
             "skills": ["产品设计", "需求分析", "数据分析"], "experience_years": 6,
             "education": "硕士", "current_company": "腾讯", "expected_salary": 45, "status": "active"},
            {"id": "mock_003", "name": "王芳", "title": "UI设计师",
             "skills": ["Figma", "Sketch", "UI设计"], "experience_years": 3,
             "education": "本科", "current_company": "阿里巴巴", "expected_salary": 28, "status": "passive"}
        ]
        self._jobs_found = [
            {"id": "job_001", "title": "高级前端开发工程师", "company": "CGL",
             "skills_required": ["React", "Vue", "Node.js"], "experience_required": "3-5年",
             "salary_range": "30-50K", "status": "open"},
            {"id": "job_002", "title": "产品总监", "company": "某知名互联网",
             "skills_required": ["产品战略", "团队管理", "数据分析"], "experience_required": "8-10年",
             "salary_range": "80-120K", "status": "open"}
        ]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "folder_path": self.folder_path,
            "candidates_count": len(self._candidates_found),
            "jobs_count": len(self._jobs_found),
            "files_indexed": len(self._file_index),
            "supported_formats": self.supported_formats
        }
